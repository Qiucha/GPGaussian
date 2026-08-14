"""Motion Critique Loop driver: human-gated default and auto-rerun."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

_src_root = Path(__file__).resolve().parent.parent
if str(_src_root) not in sys.path:
    sys.path.insert(0, str(_src_root))

from .translator import MotionTranslator

DEFAULT_OUTPUT_DIR = Path("data/outputs/critique")
PathLike = Union[str, Path]
Solver = Callable[[Dict[str, Any], Path], List[str]]
StopFlag = Callable[[], bool]


@dataclass
class LoopResult:
    status: str
    solver_runs: int
    output_dir: Path


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def _resolve_human_text(
    text: Optional[str],
    text_file: Optional[PathLike],
    stdin_text: Optional[str] = None,
) -> str:
    if text is not None:
        raw = text
    elif text_file is not None:
        raw = Path(text_file).read_text()
    elif stdin_text is not None:
        raw = stdin_text
    else:
        raw = ""
    if not raw.strip():
        raise ValueError("human text is required; empty or whitespace is not a critique turn")
    return raw


def _critique_with_retry(
    translator,
    config: Dict[str, Any],
    cot: str,
    human_text: str,
    frame_paths: Optional[List[str]],
) -> tuple[Dict[str, Any], str]:
    try:
        return translator.critique(config, cot, human_text, frame_paths=frame_paths)
    except ValueError as err:
        retry_text = f"{human_text}\n{err}"
        return translator.critique(config, cot, retry_text, frame_paths=frame_paths)


def run_critique_loop(
    *,
    previous_config: Dict[str, Any],
    previous_cot: str,
    human_text: str,
    translator,
    solver: Solver,
    output_dir: PathLike,
    mode: str = "human-gated",
    max_runs: int = 3,
    stop_flag: Optional[StopFlag] = None,
) -> LoopResult:
    text = _resolve_human_text(human_text, None)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    config = previous_config
    cot = previous_cot or ""
    solver_runs = 0
    index = 0
    while True:
        if stop_flag is not None and stop_flag() and solver_runs > 0:
            return LoopResult(status="interrupted", solver_runs=solver_runs, output_dir=out)
        if mode == "auto" and solver_runs >= max_runs:
            return LoopResult(status="done", solver_runs=solver_runs, output_dir=out)
        run_dir = out / f"run_{index:02d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        _write_json(run_dir / "config.json", config)
        frame_paths = solver(config, run_dir) or []
        solver_runs += 1
        frames_arg: Optional[List[str]] = [str(p) for p in frame_paths] or None
        try:
            config, cot = _critique_with_retry(
                translator, config, cot, text, frames_arg
            )
        except ValueError:
            return LoopResult(status="failed", solver_runs=solver_runs, output_dir=out)
        index += 1
        next_dir = out / f"run_{index:02d}"
        _write_json(next_dir / "config.json", config)
        _write_text(next_dir / "reasoning.txt", cot)
        if mode != "auto":
            return LoopResult(status="waiting", solver_runs=solver_runs, output_dir=out)
        if solver_runs >= max_runs:
            return LoopResult(status="done", solver_runs=solver_runs, output_dir=out)


def _subprocess_solver(
    model_path: str, tags_path: Optional[str]
) -> Solver:
    import subprocess

    def solver(config: Dict[str, Any], output_path: Path) -> List[str]:
        del config
        cmd = [
            sys.executable,
            "-m",
            "src.simulation.runner",
            "--model_path",
            model_path,
            "--config",
            str(output_path / "config.json"),
            "--output_path",
            str(output_path),
            "--render_img",
        ]
        if tags_path:
            cmd.extend(["--tags_path", tags_path])
        subprocess.run(cmd, check=True)
        return sorted(str(p) for p in output_path.glob("*.png"))

    return solver


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Motion Critique Loop driver.")
    parser.add_argument("--config", required=True, help="Previous complete --config JSON.")
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--tags_path", default=None)
    parser.add_argument("--output_dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--text", default=None)
    parser.add_argument("--text-file", dest="text_file", default=None)
    parser.add_argument(
        "--mode",
        choices=("human-gated", "auto"),
        default="human-gated",
    )
    parser.add_argument("--max-runs", dest="max_runs", type=int, default=3)
    parser.add_argument("--reasoning", default="", help="Previous CoT (optional).")
    args = parser.parse_args(argv)
    stdin_text = None
    if args.text is None and args.text_file is None:
        if sys.stdin.isatty():
            raise SystemExit(
                "human text is required; pass --text or --text-file (stdin only when piped)"
            )
        stdin_text = sys.stdin.read()
    human = _resolve_human_text(args.text, args.text_file, stdin_text)
    previous = json.loads(Path(args.config).read_text())
    stop = {"value": False}

    def stop_flag() -> bool:
        return stop["value"]

    def _on_sigint(_signum, _frame):
        stop["value"] = True

    try:
        import signal

        signal.signal(signal.SIGINT, _on_sigint)
    except (ValueError, OSError):
        pass

    run_critique_loop(
        previous_config=previous,
        previous_cot=args.reasoning,
        human_text=human,
        translator=MotionTranslator(mock_llm=True),
        solver=_subprocess_solver(args.model_path, args.tags_path),
        output_dir=args.output_dir,
        mode=args.mode,
        max_runs=args.max_runs,
        stop_flag=stop_flag,
    )


if __name__ == "__main__":
    main()
