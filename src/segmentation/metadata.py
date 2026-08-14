"""
3DGS Scene Metadata Extractor for PhysGaussian Segmenter Agent.
Extracts spatial extents, color channel statistics, and anisotropy distribution
from trained Gaussian Splatting point cloud tensors to enable LLM-driven heuristic selection.
"""

import torch
import numpy as np
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from src.segmentation.heuristics import sh_dc_to_rgb, rgb_to_hsv


@dataclass
class SceneMetadata:
    num_particles: int
    min_xyz: Tuple[float, float, float]
    max_xyz: Tuple[float, float, float]
    extents: Tuple[float, float, float]
    centroid: Tuple[float, float, float]
    y_percentiles: Dict[str, float]
    z_percentiles: Dict[str, float]
    mean_rgb: Tuple[float, float, float]
    color_dominance_pct: Dict[str, float]
    mean_hsv: Tuple[float, float, float]
    mean_anisotropy_ratio: float
    max_anisotropy_ratio: float
    pct_anisotropic: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def format_prompt_summary(self, scene_name: str = "Target Object") -> str:
        """
        Formats scene metadata into a concise text prompt block for LLM consumption.
        """
        return f"""=== 3DGS Scene Metadata: {scene_name} ===
- Total Particles: {self.num_particles}
- Spatial Extents: X=[{self.min_xyz[0]:.2f}, {self.max_xyz[0]:.2f}] (span: {self.extents[0]:.2f}), Y=[{self.min_xyz[1]:.2f}, {self.max_xyz[1]:.2f}] (span: {self.extents[1]:.2f}), Z=[{self.min_xyz[2]:.2f}, {self.max_xyz[2]:.2f}] (span: {self.extents[2]:.2f})
- Centroid: [{self.centroid[0]:.2f}, {self.centroid[1]:.2f}, {self.centroid[2]:.2f}]
- Vertical (Y) Percentiles: p10={self.y_percentiles['p10']:.2f}, p25={self.y_percentiles['p25']:.2f}, p50={self.y_percentiles['p50']:.2f}, p75={self.y_percentiles['p75']:.2f}, p90={self.y_percentiles['p90']:.2f}
- Depth (Z) Percentiles: p10={self.z_percentiles['p10']:.2f}, p25={self.z_percentiles['p25']:.2f}, p50={self.z_percentiles['p50']:.2f}, p75={self.z_percentiles['p75']:.2f}, p90={self.z_percentiles['p90']:.2f}
- Color Dominance: Red-Dominant={self.color_dominance_pct['red_dominant']:.1f}%, Green-Dominant={self.color_dominance_pct['green_dominant']:.1f}%, Blue-Dominant={self.color_dominance_pct['blue_dominant']:.1f}%
- Mean Color (RGB): R={self.mean_rgb[0]:.2f}, G={self.mean_rgb[1]:.2f}, B={self.mean_rgb[2]:.2f}
- Mean HSV: H={self.mean_hsv[0]:.1f}°, S={self.mean_hsv[1]:.2f}, V={self.mean_hsv[2]:.2f}
- Gaussian Anisotropy (Scale Max / Scale Min): Mean={self.mean_anisotropy_ratio:.2f}, Max={self.max_anisotropy_ratio:.2f}, % Highly Anisotropic (>3x): {self.pct_anisotropic:.1f}%
"""


def extract_scene_metadata(
    xyz: torch.Tensor,
    sh_dc: torch.Tensor,
    scales: Optional[torch.Tensor] = None,
) -> SceneMetadata:
    """
    Extracts statistical SceneMetadata from point cloud tensors.
    xyz: (N, 3) tensor of particle positions
    sh_dc: (N, 3) tensor of 0th order Spherical Harmonics DC coefficients
    scales: Optional (N, 3) tensor of Gaussian scale vectors
    """
    N = len(xyz)
    if N == 0:
        raise ValueError("Cannot extract metadata from empty point cloud tensor.")

    pts = xyz.detach().cpu().numpy()
    min_xyz = tuple(np.min(pts, axis=0).astype(float))
    max_xyz = tuple(np.max(pts, axis=0).astype(float))
    extents = (max_xyz[0] - min_xyz[0], max_xyz[1] - min_xyz[1], max_xyz[2] - min_xyz[2])
    centroid = tuple(np.mean(pts, axis=0).astype(float))

    # Spatial percentiles along Y (axis 1) and Z (axis 2)
    y_vals = pts[:, 1]
    z_vals = pts[:, 2]
    y_percentiles = {
        "p10": float(np.percentile(y_vals, 10)),
        "p25": float(np.percentile(y_vals, 25)),
        "p50": float(np.percentile(y_vals, 50)),
        "p75": float(np.percentile(y_vals, 75)),
        "p90": float(np.percentile(y_vals, 90)),
    }
    z_percentiles = {
        "p10": float(np.percentile(z_vals, 10)),
        "p25": float(np.percentile(z_vals, 25)),
        "p50": float(np.percentile(z_vals, 50)),
        "p75": float(np.percentile(z_vals, 75)),
        "p90": float(np.percentile(z_vals, 90)),
    }

    # Color analysis
    rgb = sh_dc_to_rgb(sh_dc.detach())
    rgb_np = rgb.cpu().numpy()
    mean_rgb = tuple(np.mean(rgb_np, axis=0).astype(float))

    r, g, b = rgb_np[:, 0], rgb_np[:, 1], rgb_np[:, 2]
    red_dom = np.sum((r > g) & (r > b)) / N * 100.0
    green_dom = np.sum((g > r) & (g > b)) / N * 100.0
    blue_dom = np.sum((b > r) & (b > g)) / N * 100.0

    color_dominance_pct = {
        "red_dominant": float(red_dom),
        "green_dominant": float(green_dom),
        "blue_dominant": float(blue_dom),
    }

    hsv = rgb_to_hsv(rgb)
    mean_hsv = tuple(np.mean(hsv.cpu().numpy(), axis=0).astype(float))

    # Anisotropy analysis
    if scales is not None:
        scales_detach = scales.detach()
        s_max, _ = torch.max(scales_detach, dim=1)
        s_min, _ = torch.min(scales_detach, dim=1)
        ratio = (s_max / (s_min + 1e-7)).cpu().numpy()
        mean_aniso = float(np.mean(ratio))
        max_aniso = float(np.max(ratio))
        pct_aniso = float(np.sum(ratio > 3.0) / N * 100.0)
    else:
        mean_aniso = 1.0
        max_aniso = 1.0
        pct_aniso = 0.0

    return SceneMetadata(
        num_particles=N,
        min_xyz=min_xyz,
        max_xyz=max_xyz,
        extents=extents,
        centroid=centroid,
        y_percentiles=y_percentiles,
        z_percentiles=z_percentiles,
        mean_rgb=mean_rgb,
        color_dominance_pct=color_dominance_pct,
        mean_hsv=mean_hsv,
        mean_anisotropy_ratio=mean_aniso,
        max_anisotropy_ratio=max_aniso,
        pct_anisotropic=pct_aniso,
    )
