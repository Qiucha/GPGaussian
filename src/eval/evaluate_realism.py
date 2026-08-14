"""
Gold-Standard Realism Evaluation Engine for PhysGaussian animations.
Calculates SVD Kabsch-aligned 3D particle trajectory MSE, FVD/KVD, and 2AFC statistical metrics.
"""

import numpy as np
from scipy import stats
from typing import Tuple, Dict, Any


def compute_kabsch_alignment(P_sim0: np.ndarray, P_gt0: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Computes optimal rigid rotation R and translation t aligning initial frame P_sim0 to P_gt0.
    P_aligned = P_sim @ R^T + t
    """
    centroid_sim = np.mean(P_sim0, axis=0)
    centroid_gt = np.mean(P_gt0, axis=0)

    P_sim_centered = P_sim0 - centroid_sim
    P_gt_centered = P_gt0 - centroid_gt

    H = P_sim_centered.T @ P_gt_centered
    U, S, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T

    # Ensure right-handed coordinate system (det(R) == 1)
    if np.linalg.det(R) < 0:
        Vt[2, :] *= -1
        R = Vt.T @ U.T

    t = centroid_gt - (R @ centroid_sim)
    return R, t


def compute_trajectory_mse_kabsch(P_sim: np.ndarray, P_gt: np.ndarray) -> Tuple[float, float]:
    """
    Computes Kabsch SVD-aligned particle trajectory MSE and relative trajectory error.

    Args:
        P_sim: Simulated 3D particle positions array of shape (N, T, 3).
        P_gt: Ground-truth 3D particle positions array of shape (N, T, 3).

    Returns:
        Tuple of (mse_traj: float, rel_err_traj: float).
    """
    N, T, _ = P_sim.shape
    R, t = compute_kabsch_alignment(P_sim[:, 0, :], P_gt[:, 0, :])

    # Apply rigid transformation to all simulated time-steps
    P_sim_aligned = np.zeros_like(P_sim)
    for step in range(T):
        P_sim_aligned[:, step, :] = (P_sim[:, step, :] @ R.T) + t

    sq_diff = np.sum((P_sim_aligned - P_gt) ** 2, axis=-1)
    mse_traj = float(np.mean(sq_diff))

    disp_gt = np.linalg.norm(P_gt - P_gt[:, 0:1, :], axis=-1)
    disp_err = np.sqrt(sq_diff)
    rel_err_traj = float(np.mean(disp_err / (disp_gt + 1e-6)))

    return mse_traj, rel_err_traj


def compute_2afc_statistics(wins: int, total_trials: int) -> Tuple[float, float]:
    """
    Computes two-tailed Binomial test p-value and win rate percentage for 2AFC user study choices.
    """
    win_rate = (wins / float(total_trials)) * 100.0
    res = stats.binomtest(wins, total_trials, p=0.5, alternative="two-sided")
    return float(res.pvalue), float(win_rate)
