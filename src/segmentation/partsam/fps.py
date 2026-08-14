"""In-repo PyTorch FPS stand-in for three-click PartSAM (not PartSAM-official)."""
from __future__ import annotations

import sys
import types

import torch


def batch_index_select(input: torch.Tensor, index: torch.Tensor, dim: int) -> torch.Tensor:
    while index.dim() < input.dim():
        index = index.unsqueeze(-1)
    index = index.expand(*input.shape[:dim], index.shape[dim], *input.shape[dim + 1 :])
    return torch.gather(input, dim, index)


def sample_farthest_points(points: torch.Tensor, num_samples: int) -> torch.Tensor:
    b, n, _ = points.shape
    device = points.device
    centroids = torch.zeros(b, num_samples, dtype=torch.long, device=device)
    distance = torch.full((b, n), 1e10, device=device)
    farthest = torch.zeros(b, dtype=torch.long, device=device)
    batch = torch.arange(b, device=device)
    for i in range(num_samples):
        centroids[:, i] = farthest
        centroid = points[batch, farthest].unsqueeze(1)
        dist = torch.sum((points - centroid) ** 2, dim=-1)
        distance = torch.minimum(distance, dist)
        farthest = distance.argmax(dim=-1)
    return centroids


def chamfer_distance(*_a, **_k):
    raise NotImplementedError("chamfer_distance stand-in")


def install() -> None:
    torkit3d = types.ModuleType("torkit3d")
    nn = types.ModuleType("torkit3d.nn")
    functional = types.ModuleType("torkit3d.nn.functional")
    functional.batch_index_select = batch_index_select
    ops = types.ModuleType("torkit3d.ops")
    sfp = types.ModuleType("torkit3d.ops.sample_farthest_points")
    sfp.sample_farthest_points = sample_farthest_points
    cd = types.ModuleType("torkit3d.ops.chamfer_distance")
    cd.chamfer_distance = chamfer_distance
    sys.modules["torkit3d"] = torkit3d
    sys.modules["torkit3d.nn"] = nn
    sys.modules["torkit3d.nn.functional"] = functional
    sys.modules["torkit3d.ops"] = ops
    sys.modules["torkit3d.ops.sample_farthest_points"] = sfp
    sys.modules["torkit3d.ops.chamfer_distance"] = cd
    torkit3d.nn = nn
    nn.functional = functional
    torkit3d.ops = ops
    ops.sample_farthest_points = sfp
    ops.chamfer_distance = cd
