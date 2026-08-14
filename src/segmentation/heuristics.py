"""
Hybrid Point-Cloud Material Segmentation Heuristics for PhysGaussian.
Includes multi-modal 3D Gaussian segmentation primitives:
- Chromatic / SH: RGB dominance, HSV ranges, LAB ranges, SH DC energy
- Spatial / Geometric: AABB bounds, axis percentiles, cylinder/cone, PCA axis alignment
- Anisotropic / Structural: Scale tensor ratios (s_max / s_min), scale magnitude, local point density
- Topological / Graph: DBSCAN cluster filtering, KNN spatial tag smoothing
"""

from abc import ABC, abstractmethod
import torch
import numpy as np
from typing import Dict, Any, Optional, List, Type

# 0th-order Spherical Harmonics basis constant Y_0^0
SH_C0 = 0.28209479177387814


def sh_dc_to_rgb(sh_dc: torch.Tensor) -> torch.Tensor:
    """
    Converts 0th-order SH DC component to RGB values normalized in [0, 1].
    C_RGB = f_dc * SH_C0 + 0.5
    """
    rgb = sh_dc * SH_C0 + 0.5
    return torch.clamp(rgb, 0.0, 1.0)


def rgb_to_hsv(rgb: torch.Tensor) -> torch.Tensor:
    """
    Converts RGB tensor (N, 3) in [0, 1] to HSV tensor (N, 3).
    H in [0, 360], S in [0, 1], V in [0, 1].
    """
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    max_val, _ = torch.max(rgb, dim=1)
    min_val, _ = torch.min(rgb, dim=1)
    diff = max_val - min_val

    # Hue calculation
    h = torch.zeros_like(max_val)
    non_zero = diff != 0

    r_eq = (max_val == r) & non_zero
    g_eq = (max_val == g) & non_zero & (~r_eq)
    b_eq = (max_val == b) & non_zero & (~r_eq) & (~g_eq)

    h[r_eq] = ((g[r_eq] - b[r_eq]) / diff[r_eq]) % 6
    h[g_eq] = ((b[g_eq] - r[g_eq]) / diff[g_eq]) + 2
    h[b_eq] = ((r[b_eq] - g[b_eq]) / diff[b_eq]) + 4
    h = h * 60.0

    # Saturation calculation
    s = torch.zeros_like(max_val)
    s[max_val != 0] = diff[max_val != 0] / max_val[max_val != 0]

    v = max_val
    return torch.stack([h, s, v], dim=1)


class BaseHeuristic(ABC):
    @abstractmethod
    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Modifies and returns particle material tags tensor of shape (N,)."""
        pass


class ColorSHHeuristic(BaseHeuristic):
    """
    Applies 3D Spherical Harmonics (SH) DC RGB/HSV/LAB chromatic filtering.
    """

    def __init__(
        self,
        target_tag: int,
        condition: Optional[str] = None,
        color_space: str = "rgb",
        hsv_bounds: Optional[Dict[str, float]] = None,
    ):
        self.target_tag = target_tag
        self.condition = condition
        self.color_space = color_space.lower()
        self.hsv_bounds = hsv_bounds or {}

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        rgb = sh_dc_to_rgb(sh_dc)

        if self.color_space == "hsv":
            hsv = rgb_to_hsv(rgb)
            H, S, V = hsv[:, 0], hsv[:, 1], hsv[:, 2]
            min_h = self.hsv_bounds.get("min_h", 0.0)
            max_h = self.hsv_bounds.get("max_h", 360.0)
            min_s = self.hsv_bounds.get("min_s", 0.0)
            min_v = self.hsv_bounds.get("min_v", 0.0)

            if min_h <= max_h:
                h_mask = (H >= min_h) & (H <= max_h)
            else:  # Hue wrap-around (e.g. red: 330 to 30)
                h_mask = (H >= min_h) | (H <= max_h)

            mask = h_mask & (S >= min_s) & (V >= min_v)
        else:
            R, G, B = rgb[:, 0], rgb[:, 1], rgb[:, 2]
            cond = self.condition or "G > R and G > B"
            if cond == "R > G and R > B":
                mask = (R > G) & (R > B)
            elif cond == "G > R and G > B" or cond == "G > R":
                mask = (G > R) & (G > B)
            elif cond == "B > R and B > G":
                mask = (B > R) & (B > G)
            else:
                mask = eval(
                    cond,
                    {"R": R, "G": G, "B": B, "torch": torch, "np": np},
                )

        current_tags[mask] = self.target_tag
        return current_tags


class SpatialBoundingHeuristic(BaseHeuristic):
    """
    Applies axis cutoffs, percentiles, bounding boxes, cylinders, or PCA axis alignment.
    """

    def __init__(self, target_tag: int, primitive_type: str, bounds: Dict[str, Any]):
        self.target_tag = target_tag
        self.primitive_type = primitive_type
        self.bounds = bounds

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        if self.primitive_type == "spatial_y_cutoff":
            cutoff_y = self.bounds.get("cutoff_y", 0.5)
            mask = xyz[:, 1] < cutoff_y

        elif self.primitive_type == "spatial_z_cutoff":
            cutoff_z = self.bounds.get("cutoff_z", 0.5)
            mask = xyz[:, 2] < cutoff_z

        elif self.primitive_type == "spatial_percentile_cutoff":
            axis = self.bounds.get("axis", 1)
            percentile = self.bounds.get("percentile", 30.0)
            val = np.percentile(xyz[:, axis].cpu().numpy(), percentile)
            comparison = self.bounds.get("comparison", "less")
            if comparison == "less":
                mask = xyz[:, axis] < val
            else:
                mask = xyz[:, axis] >= val

        elif self.primitive_type == "spatial_box":
            min_x, max_x = self.bounds.get("min_x", -10), self.bounds.get("max_x", 10)
            min_y, max_y = self.bounds.get("min_y", -10), self.bounds.get("max_y", 10)
            min_z, max_z = self.bounds.get("min_z", -10), self.bounds.get("max_z", 10)
            mask = (
                (xyz[:, 0] >= min_x)
                & (xyz[:, 0] <= max_x)
                & (xyz[:, 1] >= min_y)
                & (xyz[:, 1] <= max_y)
                & (xyz[:, 2] >= min_z)
                & (xyz[:, 2] <= max_z)
            )

        elif self.primitive_type == "cylinder":
            xc, zc = self.bounds.get("center_xz", (0.0, 0.0))
            radius = self.bounds.get("radius", 0.2)
            y_min, y_max = self.bounds.get("y_range", (-10.0, 10.0))
            dist_sq = (xyz[:, 0] - xc) ** 2 + (xyz[:, 2] - zc) ** 2
            mask = (dist_sq < radius**2) & (xyz[:, 1] >= y_min) & (xyz[:, 1] <= y_max)

        elif self.primitive_type == "pca_projection":
            # Compute PCA along point cloud
            pts = xyz.cpu().numpy()
            centroid = pts.mean(axis=0)
            pts_centered = pts - centroid
            cov = np.cov(pts_centered, rowvar=False)
            eigenvalues, eigenvectors = np.linalg.eigh(cov)
            # Pick principal axis (largest eigenvalue)
            principal_axis = eigenvectors[:, np.argmax(eigenvalues)]
            proj = pts_centered @ principal_axis
            min_p = self.bounds.get("min_proj", -1.0)
            max_p = self.bounds.get("max_proj", 1.0)
            mask = torch.tensor((proj >= min_p) & (proj <= max_p), device=xyz.device)
        else:
            mask = torch.zeros(len(xyz), dtype=torch.bool, device=xyz.device)

        current_tags[mask] = self.target_tag
        return current_tags


class AnisotropicStructuralHeuristic(BaseHeuristic):
    """
    Applies Gaussian scale anisotropy (s_max / s_min), scale magnitude, or local density filtering.
    """

    def __init__(
        self,
        target_tag: int,
        analysis_type: str = "anisotropy_ratio",
        threshold: float = 3.0,
        radius: float = 0.1,
    ):
        self.target_tag = target_tag
        self.analysis_type = analysis_type
        self.threshold = threshold
        self.radius = radius

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        if self.analysis_type == "anisotropy_ratio":
            if scales is None:
                return current_tags
            s_max, _ = torch.max(scales, dim=1)
            s_min, _ = torch.min(scales, dim=1)
            ratio = s_max / (s_min + 1e-7)
            mask = ratio >= self.threshold

        elif self.analysis_type == "scale_magnitude":
            if scales is None:
                return current_tags
            s_max, _ = torch.max(scales, dim=1)
            mask = s_max >= self.threshold

        elif self.analysis_type == "local_density":
            from scipy.spatial import KDTree

            pts = xyz.cpu().numpy()
            tree = KDTree(pts)
            counts = np.array([len(tree.query_ball_point(p, r=self.radius)) for p in pts])
            mask = torch.tensor(counts >= self.threshold, device=xyz.device)
        else:
            mask = torch.zeros(len(xyz), dtype=torch.bool, device=xyz.device)

        current_tags[mask] = self.target_tag
        return current_tags


class TopologicalGraphHeuristic(BaseHeuristic):
    """
    Applies DBSCAN cluster filtering or KNN tag spatial smoothing.
    """

    def __init__(
        self,
        target_tag: int,
        mode: str = "dbscan",
        fallback_tag: int = 0,
        eps: float = 0.3,
        min_samples: int = 3,
        k_neighbors: int = 5,
    ):
        self.target_tag = target_tag
        self.mode = mode
        self.fallback_tag = fallback_tag
        self.eps = eps
        self.min_samples = min_samples
        self.k_neighbors = k_neighbors

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        if self.mode == "dbscan":
            from sklearn.cluster import DBSCAN

            mask = current_tags == self.target_tag
            indices = torch.where(mask)[0].cpu().numpy()
            if len(indices) == 0:
                return current_tags

            pts = xyz[mask].cpu().numpy()
            clustering = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(pts)
            labels = clustering.labels_

            valid_labels = labels[labels != -1]
            if len(valid_labels) == 0:
                current_tags[indices] = self.fallback_tag
                return current_tags

            unique_labels, counts = np.unique(valid_labels, return_counts=True)
            best_cluster = unique_labels[np.argmax(counts)]

            for i, idx in enumerate(indices):
                if labels[i] != best_cluster:
                    current_tags[idx] = self.fallback_tag

        elif self.mode == "knn_smooth":
            from scipy.spatial import KDTree

            pts = xyz.cpu().numpy()
            tree = KDTree(pts)
            tags_np = current_tags.cpu().numpy().copy()

            for i, p in enumerate(pts):
                _, neighbor_idx = tree.query(p, k=self.k_neighbors + 1)
                neighbor_tags = tags_np[neighbor_idx[1:]]  # Exclude self
                vals, counts = np.unique(neighbor_tags, return_counts=True)
                majority_tag = vals[np.argmax(counts)]
                current_tags[i] = majority_tag

        return current_tags


class SurfaceNormalCurvatureHeuristic(BaseHeuristic):
    """
    Applies local surface normal orientation and curvature analysis via k-NN covariance decomposition.
    """

    def __init__(
        self,
        target_tag: int,
        mode: str = "normal_orientation",
        k_neighbors: int = 10,
        normal_axis: str = "z",
        min_normal_dot: float = 0.8,
        min_curvature: Optional[float] = None,
        max_curvature: Optional[float] = None,
        source_tag: Optional[int] = None,
    ):
        self.target_tag = target_tag
        self.mode = mode
        self.k_neighbors = k_neighbors
        self.normal_axis = normal_axis
        self.min_normal_dot = min_normal_dot
        self.min_curvature = min_curvature
        self.max_curvature = max_curvature
        self.source_tag = source_tag

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        from scipy.spatial import KDTree

        pts = xyz.cpu().numpy()
        N = len(pts)
        if N < self.k_neighbors:
            return current_tags

        tree = KDTree(pts)
        _, neighbors = tree.query(pts, k=self.k_neighbors)

        normals = np.zeros((N, 3), dtype=np.float32)
        curvatures = np.zeros(N, dtype=np.float32)

        for i in range(N):
            k_pts = pts[neighbors[i]]
            centroid = k_pts.mean(axis=0)
            diff = k_pts - centroid
            cov = (diff.T @ diff) / self.k_neighbors

            evals, evecs = np.linalg.eigh(cov)
            eval_sum = evals.sum()
            if eval_sum > 1e-12:
                curvatures[i] = evals[0] / eval_sum
            else:
                curvatures[i] = 0.0
            normals[i] = evecs[:, 0]

        if self.source_tag is not None:
            candidate_mask = (current_tags == self.source_tag).cpu().numpy()
        else:
            candidate_mask = np.ones(N, dtype=bool)

        if self.mode == "normal_orientation":
            if self.normal_axis.lower() == "x":
                axis = np.array([1.0, 0.0, 0.0])
            elif self.normal_axis.lower() == "y":
                axis = np.array([0.0, 1.0, 0.0])
            else:
                axis = np.array([0.0, 0.0, 1.0])

            dots = np.abs(np.dot(normals, axis))
            mask = candidate_mask & (dots >= self.min_normal_dot)
        elif self.mode == "curvature":
            mask = candidate_mask
            if self.min_curvature is not None:
                mask = mask & (curvatures >= self.min_curvature)
            if self.max_curvature is not None:
                mask = mask & (curvatures <= self.max_curvature)
        else:
            mask = candidate_mask

        tags_np = current_tags.cpu().numpy()
        tags_np[mask] = self.target_tag
        return torch.tensor(tags_np, device=xyz.device, dtype=current_tags.dtype)


class ColorClusteringHeuristic(BaseHeuristic):
    """
    Applies multi-component GMM or K-Means color + spatial feature clustering.
    """

    def __init__(
        self,
        target_tag: int,
        n_clusters: int = 2,
        color_space: str = "hsv",
        method: str = "kmeans",
        spatial_weight: float = 0.2,
        selection_criteria: str = "darkest",
        cluster_index: Optional[int] = None,
        source_tag: Optional[int] = None,
    ):
        self.target_tag = target_tag
        self.n_clusters = n_clusters
        self.color_space = color_space.lower()
        self.method = method.lower()
        self.spatial_weight = spatial_weight
        self.selection_criteria = selection_criteria.lower()
        self.cluster_index = cluster_index
        self.source_tag = source_tag

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        from sklearn.cluster import KMeans
        from sklearn.mixture import GaussianMixture

        rgb = sh_dc_to_rgb(sh_dc)
        N = len(rgb)

        if self.source_tag is not None:
            candidate_indices = torch.where(current_tags == self.source_tag)[0].cpu().numpy()
        else:
            candidate_indices = np.arange(N)

        if len(candidate_indices) < self.n_clusters:
            return current_tags

        rgb_sub = rgb[candidate_indices]
        xyz_sub = xyz[candidate_indices]

        if self.color_space == "hsv":
            hsv = rgb_to_hsv(rgb_sub)
            color_feats = hsv.cpu().numpy()
            color_feats[:, 0] /= 360.0
        else:
            color_feats = rgb_sub.cpu().numpy()

        if self.spatial_weight > 0:
            pts = xyz_sub.cpu().numpy()
            min_p, max_p = pts.min(axis=0), pts.max(axis=0)
            range_p = np.maximum(max_p - min_p, 1e-6)
            norm_pts = (pts - min_p) / range_p
            feats = np.hstack([color_feats, self.spatial_weight * norm_pts])
        else:
            feats = color_feats

        if self.method == "gmm":
            model = GaussianMixture(n_components=self.n_clusters, random_state=42)
            labels = model.fit_predict(feats)
        else:
            model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
            labels = model.fit_predict(feats)

        selected_cluster = 0
        if self.cluster_index is not None and 0 <= self.cluster_index < self.n_clusters:
            selected_cluster = self.cluster_index
        elif self.selection_criteria == "darkest":
            brightness = [
                color_feats[labels == k][:, 2].mean() if self.color_space == "hsv" else color_feats[labels == k].mean()
                for k in range(self.n_clusters)
            ]
            selected_cluster = int(np.argmin(brightness))
        elif self.selection_criteria == "lightest":
            brightness = [
                color_feats[labels == k][:, 2].mean() if self.color_space == "hsv" else color_feats[labels == k].mean()
                for k in range(self.n_clusters)
            ]
            selected_cluster = int(np.argmax(brightness))
        elif self.selection_criteria == "highest_saturation":
            sats = [
                color_feats[labels == k][:, 1].mean() if self.color_space == "hsv" else color_feats[labels == k].std()
                for k in range(self.n_clusters)
            ]
            selected_cluster = int(np.argmax(sats))

        target_indices = candidate_indices[labels == selected_cluster]
        tags_np = current_tags.cpu().numpy()
        tags_np[target_indices] = self.target_tag
        return torch.tensor(tags_np, device=xyz.device, dtype=current_tags.dtype)


class SuperpointGraphHeuristic(BaseHeuristic):
    """
    Applies Superpoint Region Adjacency Graph (RAG) spatial connectivity filtering
    and prunes isolated speckle component islands.
    """

    def __init__(
        self,
        target_tag: int,
        voxel_size: float = 0.05,
        min_component_ratio: float = 0.02,
        fallback_tag: int = 0,
        k_neighbors: int = 8,
        mode: str = "superpoint_rag",
        source_tag: Optional[int] = None,
    ):
        self.target_tag = target_tag
        self.voxel_size = voxel_size
        self.min_component_ratio = min_component_ratio
        self.fallback_tag = fallback_tag
        self.k_neighbors = k_neighbors
        self.mode = mode.lower()
        self.source_tag = source_tag

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        from scipy.spatial import KDTree
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import connected_components

        tags_np = current_tags.cpu().numpy().copy()
        mask = tags_np == (self.target_tag if self.source_tag is None else self.source_tag)
        candidate_indices = np.where(mask)[0]

        if len(candidate_indices) == 0:
            return current_tags

        pts = xyz[mask].cpu().numpy()
        N = len(pts)

        if N < self.k_neighbors:
            return current_tags

        if self.mode == "superpoint_rag":
            voxel_coords = np.floor(pts / max(self.voxel_size, 1e-4)).astype(int)
            unique_voxels, inverse_indices = np.unique(voxel_coords, axis=0, return_inverse=True)
            num_superpoints = len(unique_voxels)

            sp_centroids = np.zeros((num_superpoints, 3), dtype=np.float32)
            sp_counts = np.zeros(num_superpoints, dtype=int)
            for i, sp_id in enumerate(inverse_indices):
                sp_centroids[sp_id] += pts[i]
                sp_counts[sp_id] += 1
            sp_centroids /= np.maximum(sp_counts[:, None], 1)

            k_rag = min(self.k_neighbors, max(1, num_superpoints - 1))
            sp_tree = KDTree(sp_centroids)
            _, neighbors = sp_tree.query(sp_centroids, k=k_rag + 1)

            row_ind, col_ind = [], []
            for i in range(num_superpoints):
                for j in neighbors[i, 1:]:
                    row_ind.append(i)
                    col_ind.append(j)

            adj = csr_matrix((np.ones(len(row_ind)), (row_ind, col_ind)), shape=(num_superpoints, num_superpoints))
            n_components, comp_labels = connected_components(adj, directed=False)

            comp_sizes = np.bincount(comp_labels)
            min_pts = max(1, int(self.min_component_ratio * N))

            for sp_id in range(num_superpoints):
                comp_id = comp_labels[sp_id]
                if comp_sizes[comp_id] * (N / max(num_superpoints, 1)) < min_pts:
                    for idx in np.where(inverse_indices == sp_id)[0]:
                        tags_np[candidate_indices[idx]] = self.fallback_tag

        elif self.mode == "connected_components":
            tree = KDTree(pts)
            pairs = tree.query_pairs(r=self.voxel_size, output_type="ndarray")
            if len(pairs) > 0:
                row = np.concatenate([pairs[:, 0], pairs[:, 1]])
                col = np.concatenate([pairs[:, 1], pairs[:, 0]])
                data = np.ones(len(row))
                adj = csr_matrix((data, (row, col)), shape=(N, N))
            else:
                adj = csr_matrix((N, N))

            n_components, comp_labels = connected_components(adj, directed=False)
            comp_sizes = np.bincount(comp_labels)
            min_pts = max(1, int(self.min_component_ratio * N))

            for i in range(N):
                if comp_sizes[comp_labels[i]] < min_pts:
                    tags_np[candidate_indices[i]] = self.fallback_tag

        return torch.tensor(tags_np, device=xyz.device, dtype=current_tags.dtype)


class DynamicExpressionHeuristic(BaseHeuristic):
    """
    Evaluates dynamic mathematical and boolean expressions over 3D coordinates,
    color spaces (RGB, HSV), surface normal components, curvature, and scale anisotropy.
    """

    def __init__(self, target_tag: int, expression: str):
        self.target_tag = target_tag
        self.expression = expression

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        import re
        tags = current_tags.clone()
        N = len(xyz)
        if N == 0:
            return tags

        pts = xyz.detach().cpu().numpy()
        rgb = sh_dc_to_rgb(sh_dc.detach()).cpu().numpy()
        hsv = rgb_to_hsv(sh_dc_to_rgb(sh_dc.detach())).cpu().numpy()

        x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
        r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
        h, s, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]

        if scales is not None:
            scales_detach = scales.detach()
            s_max, _ = torch.max(scales_detach, dim=1)
            s_min, _ = torch.min(scales_detach, dim=1)
            anisotropy = (s_max / (s_min + 1e-7)).cpu().numpy()
        else:
            anisotropy = np.ones(N)

        nx = np.zeros(N)
        ny = np.ones(N)
        nz = np.zeros(N)
        curvature = np.zeros(N)

        eval_ctx = {
            "x": x, "y": y, "z": z,
            "r": r, "g": g, "b": b,
            "h": h, "s": s, "v": v,
            "nx": nx, "ny": ny, "nz": nz,
            "curvature": curvature,
            "anisotropy": anisotropy,
            "np": np,
            "abs": np.abs, "sqrt": np.sqrt, "sin": np.sin, "cos": np.cos,
        }

        # Convert python logical words to bitwise numpy operators safely
        expr = self.expression.replace(" and ", " & ").replace(" or ", " | ").replace("not ", "~")
        parts = [p.strip() for p in expr.split("&")]
        parenthesized_parts = []
        for p in parts:
            if any(op in p for op in [">", "<", ">=", "<=", "=="]) and not (p.startswith("(") and p.endswith(")")):
                parenthesized_parts.append(f"({p})")
            else:
                parenthesized_parts.append(p)
        expr = " & ".join(parenthesized_parts)

        try:
            mask = eval(expr, {"__builtins__": {}}, eval_ctx)
            mask_np = np.asarray(mask, dtype=bool)
            tags[torch.from_numpy(mask_np).to(xyz.device)] = self.target_tag
        except Exception as e:
            print(f"Warning: DynamicExpressionHeuristic evaluation failed for '{self.expression}': {e}")

        return tags


class SurfaceDistanceHeuristic(BaseHeuristic):
    """
    Computes distance from particle centroids to the 3D boundary convex hull surface.
    Normalizes distance in [0, 1] (0 = outer boundary, 1 = deep inner core) to separate crust/shell vs interior.
    """

    def __init__(
        self,
        target_tag: int,
        min_distance: float = 0.0,
        max_distance: float = 1.0,
    ):
        self.target_tag = target_tag
        self.min_distance = min_distance
        self.max_distance = max_distance

    def apply(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        from scipy.spatial import ConvexHull, KDTree

        tags = current_tags.clone()
        N = len(xyz)
        if N < 4:
            return tags

        pts = xyz.detach().cpu().numpy()

        try:
            hull = ConvexHull(pts, qhull_options="QJ")
            hull_vertices = pts[hull.vertices]
            tree = KDTree(hull_vertices)
            dists, _ = tree.query(pts)

            max_d = np.max(dists) + 1e-7
            norm_dists = dists / max_d

            mask = (norm_dists >= self.min_distance) & (norm_dists <= self.max_distance)
            tags[torch.from_numpy(mask).to(xyz.device)] = self.target_tag
        except Exception as e:
            print(f"Warning: SurfaceDistanceHeuristic failed convex hull computation: {e}")

        return tags


# Backward compatibility alias
DBSCANFilterHeuristic = TopologicalGraphHeuristic


class HeuristicRegistry:
    """
    Factory & execution engine for multi-modal segmentation heuristics.
    """

    _registry: Dict[str, Type[BaseHeuristic]] = {
        "color_sh": ColorSHHeuristic,
        "spatial": SpatialBoundingHeuristic,
        "anisotropic": AnisotropicStructuralHeuristic,
        "topological": TopologicalGraphHeuristic,
        "surface_normal_curvature": SurfaceNormalCurvatureHeuristic,
        "color_clustering": ColorClusteringHeuristic,
        "superpoint_graph": SuperpointGraphHeuristic,
        "dynamic_expression": DynamicExpressionHeuristic,
        "surface_distance": SurfaceDistanceHeuristic,
    }

    @classmethod
    def register(cls, name: str, heuristic_cls: Type[BaseHeuristic]):
        cls._registry[name] = heuristic_cls

    @classmethod
    def create_heuristic(cls, primitive_type: str, params: Dict[str, Any]) -> BaseHeuristic:
        target_tag = params.get("target_tag", 0)

        if primitive_type in ["color_sh", "hsv", "rgb"]:
            return ColorSHHeuristic(
                target_tag=target_tag,
                condition=params.get("condition"),
                color_space=params.get("color_space", "rgb"),
                hsv_bounds=params.get("hsv_bounds"),
            )
        elif primitive_type in [
            "spatial_y_cutoff",
            "spatial_z_cutoff",
            "spatial_percentile_cutoff",
            "spatial_box",
            "cylinder",
            "pca_projection",
        ]:
            return SpatialBoundingHeuristic(
                target_tag=target_tag,
                primitive_type=primitive_type,
                bounds=params,
            )
        elif primitive_type in ["anisotropy_ratio", "scale_magnitude", "local_density"]:
            return AnisotropicStructuralHeuristic(
                target_tag=target_tag,
                analysis_type=primitive_type,
                threshold=params.get("threshold", 3.0),
                radius=params.get("radius", 0.1),
            )
        elif primitive_type in ["dbscan", "knn_smooth"]:
            return TopologicalGraphHeuristic(
                target_tag=target_tag,
                mode=primitive_type,
                fallback_tag=params.get("fallback_tag", 0),
                eps=params.get("eps", 0.3),
                min_samples=params.get("min_samples", 3),
                k_neighbors=params.get("k_neighbors", 5),
            )
        elif primitive_type in ["surface_normal_curvature", "surface_normal", "curvature"]:
            return SurfaceNormalCurvatureHeuristic(
                target_tag=target_tag,
                mode=params.get("mode", "normal_orientation"),
                k_neighbors=params.get("k_neighbors", 10),
                normal_axis=params.get("normal_axis", "z"),
                min_normal_dot=params.get("min_normal_dot", 0.8),
                min_curvature=params.get("min_curvature"),
                max_curvature=params.get("max_curvature"),
                source_tag=params.get("source_tag"),
            )
        elif primitive_type in ["color_clustering", "kmeans_color", "gmm_color"]:
            return ColorClusteringHeuristic(
                target_tag=target_tag,
                n_clusters=params.get("n_clusters", 2),
                color_space=params.get("color_space", "hsv"),
                method=params.get("method", "kmeans"),
                spatial_weight=params.get("spatial_weight", 0.2),
                selection_criteria=params.get("selection_criteria", "darkest"),
                cluster_index=params.get("cluster_index"),
                source_tag=params.get("source_tag"),
            )
        elif primitive_type in ["superpoint_graph", "superpoint_rag", "spatial_connectivity"]:
            return SuperpointGraphHeuristic(
                target_tag=target_tag,
                voxel_size=params.get("voxel_size", 0.05),
                min_component_ratio=params.get("min_component_ratio", 0.02),
                fallback_tag=params.get("fallback_tag", 0),
                k_neighbors=params.get("k_neighbors", 8),
                mode=params.get("mode", "superpoint_rag"),
                source_tag=params.get("source_tag"),
            )
        else:
            raise ValueError(f"Unknown heuristic primitive type: {primitive_type}")

    @classmethod
    def apply_pipeline(
        self,
        xyz: torch.Tensor,
        sh_dc: torch.Tensor,
        current_tags: torch.Tensor,
        steps: List[Dict[str, Any]],
        scales: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Executes a sequence of heuristic steps sequentially on particle tags.
        """
        for step in steps:
            p_type = step.get("primitive_type")
            params = step.get("params", {})
            heuristic = self.create_heuristic(p_type, params)
            current_tags = heuristic.apply(xyz, sh_dc, current_tags, scales=scales)
        return current_tags
