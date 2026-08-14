"""Stage 2: geometry proposes on-cloud clicks; MLLM/human writes spec JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Union

import numpy as np

from src.segmentation.partsam.surface import load_sample_100k, sample_npz_path

CLICKS_NAME = "clicks.json"
CANDIDATES_NAME = "click_candidates.json"
PREVIEW_NAME = "click_candidates.png"
GROUP_NAMES = ("pot", "trunk", "leaves")
K_CANDIDATES = 5
PathLike = Union[str, Path]


def clicks_json_path(output_dir: PathLike) -> Path:
    return Path(output_dir) / CLICKS_NAME


def validate_clicks(doc: Mapping[str, Any]) -> None:
    if doc.get("frame") != "world":
        raise ValueError("clicks JSON must have frame 'world'")
    if "source" not in doc:
        raise ValueError("clicks JSON missing source")
    groups = doc.get("groups")
    if not isinstance(groups, Mapping):
        raise ValueError("clicks JSON missing groups")
    missing = [name for name in GROUP_NAMES if name not in groups]
    if missing:
        raise ValueError(f"clicks JSON missing groups: {missing}")
    for name in GROUP_NAMES:
        group = groups[name]
        if not isinstance(group, Mapping) or "positives" not in group or "negatives" not in group:
            raise ValueError(f"group {name} must have positives and negatives")
        positives = group["positives"]
        if not isinstance(positives, list) or len(positives) < 1:
            raise ValueError(f"group {name} needs one or more positives")
        if not isinstance(group["negatives"], list):
            raise ValueError(f"group {name} negatives must be a list")


def clicks_are_complete(doc: Mapping[str, Any]) -> bool:
    try:
        validate_clicks(doc)
    except (TypeError, ValueError, KeyError):
        return False
    return True


def load_clicks(path: PathLike) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def knn_of_centroid(
    xyz: np.ndarray, mask: np.ndarray, k: int
) -> tuple[np.ndarray, np.ndarray]:
    if int(mask.sum()) < k:
        raise RuntimeError(f"bin too small: {int(mask.sum())} < {k}")
    centroid = xyz[mask].mean(axis=0)
    dist = np.linalg.norm(xyz - centroid, axis=1)
    dist_out = np.where(mask, dist, np.inf)
    idx = np.argpartition(dist_out, k)[:k]
    idx = idx[np.argsort(dist_out[idx])]
    return idx, centroid


def propose_click_candidates(
    coords: np.ndarray, colors: np.ndarray, k: int = K_CANDIDATES
) -> dict[str, Any]:
    xyz = np.asarray(coords, dtype=np.float32)
    rgb = np.asarray(colors, dtype=np.float32)
    lum = rgb.mean(axis=1)
    zc = xyz[:, 2]
    z_lo, z_hi = np.percentile(zc, [12, 70])
    green = (rgb[:, 1] > rgb[:, 0] + 8) & (rgb[:, 1] > 90)

    pot_m = (zc < z_lo) & (lum < 95)
    leaf_m = (zc > z_hi) & green
    mid = (zc > np.percentile(zc, 22)) & (zc < np.percentile(zc, 55)) & ~pot_m & ~leaf_m
    if int(mid.sum()) < 200:
        mid = (zc > np.percentile(zc, 20)) & (zc < np.percentile(zc, 60))
    axis = np.median(xyz[mid, :2], axis=0)
    radius = np.linalg.norm(xyz[:, :2] - axis, axis=1)
    r_cut = np.percentile(radius[mid], 18)
    trunk_m = mid & (radius < r_cut) & ~green & (lum > 70)

    groups: dict[str, Any] = {}
    for name, mask in (("pot", pot_m), ("trunk", trunk_m), ("leaves", leaf_m)):
        idx, centroid = knn_of_centroid(xyz, mask, k)
        groups[name] = {
            "n_bin": int(mask.sum()),
            "centroid": centroid.tolist(),
            "indices": idx.tolist(),
            "points": xyz[idx].tolist(),
        }
    return groups


def write_preview_png(
    path: PathLike,
    coords: np.ndarray,
    colors: np.ndarray,
    groups: Mapping[str, Any],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    xyz = np.asarray(coords, dtype=np.float32)
    rgb = np.asarray(colors, dtype=np.float32)
    rng = np.random.default_rng(0)
    vis = rng.choice(len(xyz), size=min(12000, len(xyz)), replace=False)
    vis_rgb = rgb[vis] / 255.0
    markers = {"pot": ("o", "red"), "trunk": ("s", "magenta"), "leaves": ("^", "lime")}
    pairs = [("x", "y", 0, 1), ("x", "z", 0, 2), ("y", "z", 1, 2)]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), dpi=140)
    fig.suptitle("100k click candidates (primary + extras)")
    for ax, (xl, yl, i, j) in zip(axes, pairs):
        ax.scatter(xyz[vis, i], xyz[vis, j], c=vis_rgb, s=0.4, linewidths=0)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_aspect("equal", adjustable="datalim")
        for gname, group in groups.items():
            mk, col = markers[gname]
            pts = np.asarray(group["points"])
            ax.scatter(
                pts[0, i],
                pts[0, j],
                marker=mk,
                s=80,
                facecolors="none",
                edgecolors=col,
                linewidths=1.6,
                zorder=5,
                label=f"{gname} P0",
            )
            for extra in range(1, len(pts)):
                ax.scatter(
                    pts[extra, i],
                    pts[extra, j],
                    marker=mk,
                    s=28,
                    c=col,
                    alpha=0.7,
                    zorder=4,
                    label=f"{gname} P{extra}" if ax is axes[0] else None,
                )
                ax.annotate(str(extra), (pts[extra, i], pts[extra, j]), fontsize=7, color=col)
            ax.annotate("P0", (pts[0, i], pts[0, j]), fontsize=8, color=col, fontweight="bold")
        if ax is axes[0]:
            ax.legend(fontsize=7, loc="best", markerscale=0.8)
    fig.tight_layout()
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest)
    plt.close(fig)


def _propose_and_write(output_dir: Path, sample: Mapping[str, np.ndarray]) -> None:
    groups = propose_click_candidates(sample["coords"], sample["colors"])
    cand_path = output_dir / CANDIDATES_NAME
    cand_path.write_text(json.dumps(groups, indent=2))
    try:
        write_preview_png(
            output_dir / PREVIEW_NAME,
            sample["coords"],
            sample["colors"],
            groups,
        )
    except ImportError:
        pass


def run_stage_clicks(
    model_path: PathLike,
    output_dir: PathLike,
    *,
    skip_if_exists: bool = True,
) -> Path:
    del model_path
    out = Path(output_dir)
    dest = clicks_json_path(out)
    if skip_if_exists and dest.exists():
        doc = load_clicks(dest)
        if clicks_are_complete(doc):
            return dest
    sample = load_sample_100k(sample_npz_path(out))
    out.mkdir(parents=True, exist_ok=True)
    _propose_and_write(out, sample)
    if dest.exists() and clicks_are_complete(load_clicks(dest)):
        return dest
    raise RuntimeError(
        f"wrote {CANDIDATES_NAME} and {PREVIEW_NAME}; MLLM or human must write {CLICKS_NAME} "
        "(accept / swap / resample labeled candidates only, no free-form xyz). "
        "Human after two failed annotated rounds."
    )
