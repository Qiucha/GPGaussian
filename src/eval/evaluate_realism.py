"""
Gold-Standard Realism Evaluation Engine for PhysGaussian animations.
Calculates SVD Kabsch-aligned 3D particle trajectory MSE, frame PSNR/SSIM/LPIPS,
render-frame sanity checks, FVD/KVD (named; not implemented), and 2AFC stats.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy import stats

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore


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


def _as_float_image(image: np.ndarray) -> np.ndarray:
    """Normalize HWC or CHW image to float32 RGB in [0, 1]."""
    arr = np.asarray(image)
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    if arr.ndim == 3 and arr.shape[0] in (1, 3) and arr.shape[-1] not in (1, 3):
        arr = np.transpose(arr, (1, 2, 0))
    if arr.shape[-1] == 1:
        arr = np.repeat(arr, 3, axis=-1)
    if arr.shape[-1] > 3:
        arr = arr[..., :3]
    arr = arr.astype(np.float64)
    if arr.max() > 1.0 + 1e-6:
        arr = arr / 255.0
    return np.clip(arr, 0.0, 1.0)


def load_image_rgb(path: str) -> np.ndarray:
    """Load an image file as float RGB in [0, 1], shape (H, W, 3)."""
    if Image is None:
        raise ImportError("Pillow is required to load images for render quality metrics")
    with Image.open(path) as img:
        return _as_float_image(np.asarray(img.convert("RGB")))


def compute_psnr(img_a: np.ndarray, img_b: np.ndarray, data_range: float = 1.0) -> float:
    """Peak signal-to-noise ratio between two images (higher is better)."""
    a = _as_float_image(img_a)
    b = _as_float_image(img_b)
    if a.shape != b.shape:
        raise ValueError(f"PSNR shape mismatch: {a.shape} vs {b.shape}")
    mse = float(np.mean((a - b) ** 2))
    if mse <= 0.0:
        return float("inf")
    return float(10.0 * np.log10((data_range ** 2) / mse))


def compute_ssim(img_a: np.ndarray, img_b: np.ndarray, data_range: float = 1.0) -> float:
    """
    Mean structural similarity (Wang et al.) over RGB channels.
    Returns a score in approximately [-1, 1]; 1 is identical.
    """
    from scipy.ndimage import gaussian_filter

    a = _as_float_image(img_a)
    b = _as_float_image(img_b)
    if a.shape != b.shape:
        raise ValueError(f"SSIM shape mismatch: {a.shape} vs {b.shape}")

    sigma = 1.5
    c1 = (0.01 * data_range) ** 2
    c2 = (0.03 * data_range) ** 2
    channel_scores: List[float] = []
    for ch in range(a.shape[-1]):
        x = a[..., ch]
        y = b[..., ch]
        mu_x = gaussian_filter(x, sigma)
        mu_y = gaussian_filter(y, sigma)
        mu_x2 = mu_x * mu_x
        mu_y2 = mu_y * mu_y
        mu_xy = mu_x * mu_y
        sigma_x2 = gaussian_filter(x * x, sigma) - mu_x2
        sigma_y2 = gaussian_filter(y * y, sigma) - mu_y2
        sigma_xy = gaussian_filter(x * y, sigma) - mu_xy
        num = (2.0 * mu_xy + c1) * (2.0 * sigma_xy + c2)
        den = (mu_x2 + mu_y2 + c1) * (sigma_x2 + sigma_y2 + c2)
        channel_scores.append(float(np.mean(num / den)))
    return float(np.mean(channel_scores))


def compute_lpips(img_a: np.ndarray, img_b: np.ndarray) -> float:
    """
    Learned perceptual image patch similarity (lower is better).

    Requires the optional ``lpips`` package (AlexNet backbone). Raises ImportError
    when the dependency is absent so callers can record ``lpips: null``.
    """
    try:
        import torch
        import lpips  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "compute_lpips requires the optional 'lpips' and 'torch' packages"
        ) from exc

    a = _as_float_image(img_a)
    b = _as_float_image(img_b)
    if a.shape != b.shape:
        raise ValueError(f"LPIPS shape mismatch: {a.shape} vs {b.shape}")

    loss_fn = getattr(compute_lpips, "_loss_fn", None)
    if loss_fn is None:
        loss_fn = lpips.LPIPS(net="alex")
        loss_fn.eval()
        compute_lpips._loss_fn = loss_fn  # type: ignore[attr-defined]

    def to_nchw(img: np.ndarray) -> "torch.Tensor":
        t = torch.from_numpy(img.astype(np.float32)).permute(2, 0, 1).unsqueeze(0)
        return t * 2.0 - 1.0

    with torch.no_grad():
        dist = loss_fn(to_nchw(a), to_nchw(b))
    return float(dist.item())


def evaluate_frame_sanity(image: np.ndarray) -> Dict[str, Any]:
    """
    Stability / crash-adjacent checks for a single rendered frame.

    Flags all-black, all-white, non-finite pixels, and empty dynamic range.
    """
    arr = np.asarray(image, dtype=np.float64)
    finite = bool(np.isfinite(arr).all())
    if arr.size == 0:
        return {
            "ok": False,
            "finite": False,
            "all_black": True,
            "all_white": False,
            "mean_luminance": 0.0,
            "std_luminance": 0.0,
            "reasons": ["empty_image"],
        }

    rgb = _as_float_image(arr)
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    mean_l = float(np.mean(lum))
    std_l = float(np.std(lum))
    all_black = bool(mean_l < 1e-4 and std_l < 1e-4)
    all_white = bool(mean_l > 1.0 - 1e-4 and std_l < 1e-4)
    reasons: List[str] = []
    if not finite:
        reasons.append("non_finite_pixels")
    if all_black:
        reasons.append("all_black")
    if all_white:
        reasons.append("all_white")
    if std_l < 1e-4 and not all_black and not all_white:
        reasons.append("zero_dynamic_range")
    return {
        "ok": len(reasons) == 0,
        "finite": finite,
        "all_black": all_black,
        "all_white": all_white,
        "mean_luminance": mean_l,
        "std_luminance": std_l,
        "reasons": reasons,
    }


def compare_image_pair(img_a: np.ndarray, img_b: np.ndarray) -> Dict[str, Any]:
    """Compute PSNR/SSIM and optional LPIPS for one image pair."""
    result: Dict[str, Any] = {
        "psnr": compute_psnr(img_a, img_b),
        "ssim": compute_ssim(img_a, img_b),
        "lpips": None,
        "lpips_error": None,
    }
    try:
        result["lpips"] = compute_lpips(img_a, img_b)
    except ImportError as exc:
        result["lpips_error"] = str(exc)
    except Exception as exc:  # pragma: no cover - backend-specific failures
        result["lpips_error"] = f"{type(exc).__name__}: {exc}"
    return result


def evaluate_render_directory(
    sim_dir: str,
    reference_dir: Optional[str] = None,
    max_frames: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Evaluate stability and (optionally) quality for a directory of ``%04d.png`` frames.

    When ``reference_dir`` is set, each sim frame is compared to the same-named
    reference image when that file exists.
    """
    if not os.path.isdir(sim_dir):
        return {
            "ok": False,
            "error": f"sim_dir does not exist: {sim_dir}",
            "frame_count": 0,
            "frames": [],
        }

    sim_frames = sorted(
        f for f in os.listdir(sim_dir) if f.endswith(".png") and f[:4].isdigit()
    )
    if max_frames is not None:
        sim_frames = sim_frames[:max_frames]

    frame_reports: List[Dict[str, Any]] = []
    quality_psnr: List[float] = []
    quality_ssim: List[float] = []
    quality_lpips: List[float] = []

    for name in sim_frames:
        path = os.path.join(sim_dir, name)
        image = load_image_rgb(path)
        sanity = evaluate_frame_sanity(image)
        entry: Dict[str, Any] = {"frame": name, "path": path, "sanity": sanity}
        if reference_dir:
            ref_path = os.path.join(reference_dir, name)
            if os.path.isfile(ref_path):
                ref = load_image_rgb(ref_path)
                metrics = compare_image_pair(image, ref)
                entry["vs_reference"] = metrics
                if metrics["psnr"] is not None and (
                    np.isfinite(metrics["psnr"]) or metrics["psnr"] == float("inf")
                ):
                    quality_psnr.append(float(metrics["psnr"]))
                quality_ssim.append(float(metrics["ssim"]))
                if metrics["lpips"] is not None:
                    quality_lpips.append(float(metrics["lpips"]))
            else:
                entry["vs_reference"] = {"missing_reference": ref_path}
        frame_reports.append(entry)

    sanity_ok = all(f["sanity"]["ok"] for f in frame_reports) if frame_reports else False
    summary: Dict[str, Any] = {
        "ok": sanity_ok and len(frame_reports) > 0,
        "frame_count": len(frame_reports),
        "sanity_pass_count": sum(1 for f in frame_reports if f["sanity"]["ok"]),
        "frames": frame_reports,
        "aggregate": {
            "mean_psnr": float(np.mean(quality_psnr)) if quality_psnr else None,
            "mean_ssim": float(np.mean(quality_ssim)) if quality_ssim else None,
            "mean_lpips": float(np.mean(quality_lpips)) if quality_lpips else None,
        },
    }
    return summary


def assert_expected_frame_count(sim_dir: str, expected: int) -> Tuple[bool, str]:
    """Return whether ``sim_dir`` contains exactly ``expected`` numbered PNG frames."""
    if not os.path.isdir(sim_dir):
        return False, f"missing directory {sim_dir}"
    count = sum(
        1 for f in os.listdir(sim_dir) if f.endswith(".png") and f[:4].isdigit()
    )
    if count != expected:
        return False, f"expected {expected} frames, found {count}"
    return True, f"found {count} frames"
