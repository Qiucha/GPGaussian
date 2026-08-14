"""
Quantitative 3DGS Segmentation Quality Evaluator & Diagnostic Metrics Engine.
Computes intra-material color/spatial variances, Silhouette score, spatial contiguity index,
and isolated speckle noise percentages for LLM agent self-correction feedback.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import torch
from scipy.spatial import KDTree
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from src.segmentation.heuristics import sh_dc_to_rgb


@dataclass
class MaterialClassMetric:
    tag_id: int
    name: str
    particle_count: int
    percentage: float
    color_std: Tuple[float, float, float]
    spatial_std: Tuple[float, float, float]
    connected_components: int
    speckle_count: int
    speckle_percentage: float


@dataclass
class SegmentationMetrics:
    total_particles: int
    num_tags: int
    silhouette_score: float
    speckle_total_pct: float
    tag_metrics: List[MaterialClassMetric]
    overall_quality_rating: str  # "EXCELLENT", "GOOD", "NEEDS_REFINEMENT", "POOR"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def format_llm_feedback(self) -> str:
        """
        Formats metrics into a structured diagnostic feedback text block for LLM prompt consumption.
        """
        lines = [
            "=== QUANTITATIVE SEGMENTATION EVALUATION REPORT ===",
            f"Overall Quality Rating: {self.overall_quality_rating}",
            f"Total Particles: {self.total_particles:,} | Unique Material Tags: {self.num_tags}",
            f"Approx. Spatial-Color Silhouette Score: {self.silhouette_score:.3f} (-1 to +1, higher is cleaner)",
            f"Total Speckle Noise Ratio: {self.speckle_total_pct:.1f}%",
            "",
            "Per-Material Tag Diagnostics:",
        ]

        for m in self.tag_metrics:
            lines.append(
                f" - Tag {m.tag_id} ({m.name}): {m.particle_count:,} pts ({m.percentage:.1f}%) | "
                f"Components: {m.connected_components} | Speckles: {m.speckle_count} ({m.speckle_percentage:.1f}%) | "
                f"Spatial Std: [{m.spatial_std[0]:.2f}, {m.spatial_std[1]:.2f}, {m.spatial_std[2]:.2f}] | "
                f"Color Std: [{m.color_std[0]:.2f}, {m.color_std[1]:.2f}, {m.color_std[2]:.2f}]"
            )

        lines.append("")
        lines.append("DIAGNOSTIC CRITIQUE:")
        if self.speckle_total_pct > 5.0:
            lines.append(" - WARNING: High speckle noise detected. Recommend adding a 'superpoint_graph' or 'dbscan' filtering step.")

        for m in self.tag_metrics:
            if m.particle_count == 0:
                lines.append(f" - CRITICAL: Tag {m.tag_id} ({m.name}) contains 0 particles! Re-adjust cutoff parameters or expression bounds.")
            elif m.percentage > 95.0 and self.num_tags > 1:
                lines.append(f" - WARNING: Tag {m.tag_id} occupies {m.percentage:.1f}% of object. Other materials are under-segmented.")
            elif m.connected_components > 20:
                lines.append(f" - WARNING: Tag {m.tag_id} is heavily fragmented into {m.connected_components} disconnected components.")

        return "\n".join(lines)


class SegmentationEvaluator:
    """
    Computes spatial, chromatic, and graph-topological quality metrics on material tag assignments.
    """

    @staticmethod
    def evaluate(
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        tags: torch.Tensor,
        material_names: Optional[Dict[int, str]] = None,
        voxel_size: float = 0.08,
    ) -> SegmentationMetrics:
        N = len(xyz)
        if N == 0:
            raise ValueError("Cannot evaluate metrics on empty point cloud.")

        pts = xyz.detach().cpu().numpy()
        rgb = sh_dc_to_rgb(sh_dc.detach()).cpu().numpy()
        tags_np = tags.detach().cpu().numpy()

        unique_tags = np.unique(tags_np)
        num_tags = len(unique_tags)

        tag_names = material_names or {int(t): f"Material_{t}" for t in unique_tags}

        tag_metrics_list = []
        total_speckles = 0

        # Compute per-tag metrics
        for tag in unique_tags:
            idx = np.where(tags_np == tag)[0]
            count = len(idx)
            pct = (count / N) * 100.0

            if count == 0:
                tag_metrics_list.append(
                    MaterialClassMetric(
                        tag_id=int(tag),
                        name=tag_names.get(int(tag), f"Tag_{tag}"),
                        particle_count=0,
                        percentage=0.0,
                        color_std=(0.0, 0.0, 0.0),
                        spatial_std=(0.0, 0.0, 0.0),
                        connected_components=0,
                        speckle_count=0,
                        speckle_percentage=0.0,
                    )
                )
                continue

            tag_pts = pts[idx]
            tag_rgb = rgb[idx]

            spatial_std = tuple(np.std(tag_pts, axis=0).astype(float))
            color_std = tuple(np.std(tag_rgb, axis=0).astype(float))

            # Graph connected components & speckle calculation
            if count > 1:
                voxels = np.floor(tag_pts / voxel_size).astype(int)
                u_vox, vox_inv = np.unique(voxels, axis=0, return_inverse=True)
                v_N = len(u_vox)

                if v_N > 1:
                    v_tree = KDTree(u_vox)
                    pairs = v_tree.query_pairs(r=1.5, output_type="ndarray")
                    if len(pairs) > 0:
                        row = np.concatenate([pairs[:, 0], pairs[:, 1]])
                        col = np.concatenate([pairs[:, 1], pairs[:, 0]])
                        adj = csr_matrix((np.ones(len(row)), (row, col)), shape=(v_N, v_N))
                    else:
                        adj = csr_matrix((v_N, v_N))

                    n_comps, comp_labels = connected_components(adj, directed=False)
                    v_sizes = np.bincount(comp_labels)
                    min_speckle = max(1, int(0.01 * count))

                    point_comp_sizes = v_sizes[comp_labels[vox_inv]]
                    speckle_pts = np.sum(point_comp_sizes < min_speckle)
                else:
                    n_comps = 1
                    speckle_pts = 0
            else:
                n_comps = 1
                speckle_pts = 1

            total_speckles += speckle_pts
            speckle_pct = (speckle_pts / count) * 100.0 if count > 0 else 0.0

            tag_metrics_list.append(
                MaterialClassMetric(
                    tag_id=int(tag),
                    name=tag_names.get(int(tag), f"Tag_{tag}"),
                    particle_count=count,
                    percentage=float(pct),
                    color_std=color_std,
                    spatial_std=spatial_std,
                    connected_components=int(n_comps),
                    speckle_count=int(speckle_pts),
                    speckle_percentage=float(speckle_pct),
                )
            )

        speckle_total_pct = (total_speckles / N) * 100.0

        # Compute fast spatial-color Silhouette proxy score
        if N > 500:
            sample_idx = np.random.choice(N, 500, replace=False)
        else:
            sample_idx = np.arange(N)

        sample_pts = pts[sample_idx]
        sample_rgb = rgb[sample_idx]
        sample_tags = tags_np[sample_idx]

        features = np.hstack([sample_pts, sample_rgb * 0.5])
        sil_score = float(SegmentationEvaluator._compute_silhouette_proxy(features, sample_tags))

        # Overall rating assignment
        if speckle_total_pct < 3.0 and sil_score > 0.3:
            rating = "EXCELLENT"
        elif speckle_total_pct < 8.0 and sil_score > 0.1:
            rating = "GOOD"
        elif speckle_total_pct < 15.0:
            rating = "NEEDS_REFINEMENT"
        else:
            rating = "POOR"

        return SegmentationMetrics(
            total_particles=N,
            num_tags=num_tags,
            silhouette_score=sil_score,
            speckle_total_pct=float(speckle_total_pct),
            tag_metrics=tag_metrics_list,
            overall_quality_rating=rating,
        )

    @staticmethod
    def _compute_silhouette_proxy(features: np.ndarray, tags: np.ndarray) -> float:
        unique_tags = np.unique(tags)
        if len(unique_tags) < 2:
            return 0.0

        N = len(features)
        a = np.zeros(N)
        b = np.full(N, np.inf)

        for i in range(N):
            same_mask = (tags == tags[i])

            if np.sum(same_mask) > 1:
                a[i] = np.mean(np.linalg.norm(features[same_mask] - features[i], axis=1))

            for other_tag in unique_tags:
                if other_tag == tags[i]:
                    continue
                other_mask = (tags == other_tag)
                if np.sum(other_mask) > 0:
                    dist_other = np.mean(np.linalg.norm(features[other_mask] - features[i], axis=1))
                    b[i] = min(b[i], dist_other)

        max_ab = np.maximum(a, b) + 1e-7
        s = (b - a) / max_ab
        return float(np.mean(s))
