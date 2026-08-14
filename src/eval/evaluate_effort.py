"""
User Configuration Effort Instrumentation & NASA-TLX Workload Tracker.
"""

import time
from typing import Dict, Any, List


class ConfigurationEffortTracker:
    def __init__(self):
        self.session_id: str = ""
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.loc_manual: int = 0
        self.n_iter: int = 0
        self.logs: List[Dict[str, Any]] = []

    def start_session(self, session_id: str):
        self.session_id = session_id
        self.start_time = time.time()
        self.loc_manual = 0
        self.n_iter = 0
        self.logs.append({"event": "start_session", "timestamp": self.start_time})

    def record_code_change(self, code_snippet: str):
        lines = [line.strip() for line in code_snippet.splitlines() if line.strip()]
        self.loc_manual += len(lines)
        self.logs.append({"event": "code_change", "added_lines": len(lines)})

    def record_simulation_run(self):
        self.n_iter += 1
        self.logs.append({"event": "simulation_run", "iteration": self.n_iter})

    def end_session(self) -> Dict[str, Any]:
        self.end_time = time.time()
        t_setup_seconds = self.end_time - self.start_time
        return {
            "session_id": self.session_id,
            "t_setup_seconds": t_setup_seconds,
            "t_setup_minutes": t_setup_seconds / 60.0,
            "loc_manual": self.loc_manual,
            "n_iter": self.n_iter,
        }
