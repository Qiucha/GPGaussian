"""Merge PartSAM masks by chosen IoU and NN-lift onto every Gaussian."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Union

import numpy as np
import torch

TAG_POT = 1
TAG_TRUNK = 2
TAG_LEAVES = 3
GROUP_TAGS = {"pot": TAG_POT, "trunk": TAG_TRUNK, "leaves": TAG_LEAVES}
GROUP_NAMES = ("pot", "trunk", "leaves")
PART_MASKS_NAME = "part_masks.npz"
CHOSEN_IOU_NAME = "chosen_iou.json"
DEFAULT_TAGS_PATH = Path("data/outputs/tags/material_tags.pt")
NN_CHUNK = 4096
PathLike = Union[str, Path]


def merge_masks(
    pot: np.ndarray,
    trunk: np.ndarray,
    leaves: np.ndarray,
    chosen_iou: Mapping[str, float],
) -> np.ndarray:
    masks = {
        "pot": np.asarray(pot) > 0,
        "trunk": np.asarray(trunk) > 0,
        "leaves": np.asarray(leaves) > 0,
    }
    sizes = {name: int(mask.sum()) for name, mask in masks.items()}
    n = masks["pot"].shape[0]
    merged = np.zeros(n, dtype=np.int32)
    for i in range(n):
        claimants = [name for name in GROUP_NAMES if masks[name][i]]
        if not claimants:
            continue
        winner = min(
            claimants,
            key=lambda name: (-float(chosen_iou[name]), sizes[name], name),
        )
        merged[i] = GROUP_TAGS[winner]
    return merged


def lift_tags(
    gaussian_xyz: np.ndarray,
    sample_xyz: np.ndarray,
    sample_tags: np.ndarray,
) -> np.ndarray:
    labeled = np.asarray(sample_tags) != 0
    if not np.any(labeled):
        raise RuntimeError("no labeled 100k samples to lift")
    ref_xyz = np.asarray(sample_xyz, dtype=np.float32)[labeled]
    ref_tags = np.asarray(sample_tags, dtype=np.int64)[labeled]
    query = np.asarray(gaussian_xyz, dtype=np.float32)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ref = torch.from_numpy(ref_xyz).to(device)
    tags = torch.from_numpy(ref_tags).to(device)
    out = np.empty(len(query), dtype=np.int32)
    for start in range(0, len(query), NN_CHUNK):
        chunk = torch.from_numpy(query[start : start + NN_CHUNK]).to(device)
        idx = torch.cdist(chunk, ref).argmin(dim=1)
        out[start : start + NN_CHUNK] = tags[idx].cpu().numpy().astype(np.int32)
    return out


def occupancy_ok(
    tags: np.ndarray, n: int, prompted_ids: Iterable[int]
) -> bool:
    arr = np.asarray(tags)
    if arr.ndim != 1 or int(arr.shape[0]) != int(n):
        return False
    for pid in prompted_ids:
        if int((arr == int(pid)).sum()) <= 0:
            return False
    return True


def prompted_tag_ids(clicks: Mapping) -> tuple[int, ...]:
    groups = clicks.get("groups") if isinstance(clicks, Mapping) else None
    if not isinstance(groups, Mapping):
        return ()
    ids: list[int] = []
    for name in GROUP_NAMES:
        group = groups.get(name) or {}
        positives = group.get("positives") or []
        if isinstance(positives, list) and len(positives) >= 1:
            ids.append(GROUP_TAGS[name])
    return tuple(ids)


def apply_survival(
    pot: np.ndarray,
    trunk: np.ndarray,
    leaves: np.ndarray,
    chosen_iou: Mapping[str, float],
    sample_xyz: np.ndarray,
    gaussian_xyz: np.ndarray,
) -> np.ndarray:
    masks = {
        "pot": np.asarray(pot) > 0,
        "trunk": np.asarray(trunk) > 0,
        "leaves": np.asarray(leaves) > 0,
    }
    merged = merge_masks(pot, trunk, leaves, chosen_iou)
    lifted = lift_tags(gaussian_xyz, sample_xyz, merged)
    empty = []
    for name in GROUP_NAMES:
        if int(masks[name].sum()) == 0:
            continue
        tag = GROUP_TAGS[name]
        if int((lifted == tag).sum()) == 0:
            empty.append(name)
    empty.sort(key=lambda name: (float(chosen_iou[name]), name))
    for name in empty:
        merged = np.array(merged, copy=True)
        merged[masks[name]] = GROUP_TAGS[name]
        lifted = lift_tags(gaussian_xyz, sample_xyz, merged)
    return lifted


def rematerialize_tags(
    output_dir: PathLike,
    tags_path: PathLike,
    gaussian_xyz: np.ndarray,
) -> Path:
    from src.segmentation.partsam.surface import load_sample_100k, sample_npz_path

    out = Path(output_dir)
    with np.load(out / PART_MASKS_NAME) as packed:
        pot = packed["pot"]
        trunk = packed["trunk"]
        leaves = packed["leaves"]
    chosen_iou = json.loads((out / CHOSEN_IOU_NAME).read_text())
    sample = load_sample_100k(sample_npz_path(out))
    lifted = apply_survival(
        pot, trunk, leaves, chosen_iou, np.asarray(sample["coords"]), gaussian_xyz
    )
    write_material_tags(tags_path, lifted)
    return Path(tags_path)


def check_occupancy(
    tags_path: PathLike, model_path: PathLike, clicks_path: PathLike
) -> bool:
    from src.segmentation.partsam.surface import load_gaussian_means_rgb

    dest = Path(tags_path)
    if not dest.is_file():
        return False
    tags = torch.load(dest, weights_only=True).cpu().numpy()
    xyz, _ = load_gaussian_means_rgb(model_path)
    clicks = json.loads(Path(clicks_path).read_text())
    return occupancy_ok(tags, len(xyz), prompted_tag_ids(clicks))


def write_part_masks(
    path: PathLike,
    pot: np.ndarray,
    trunk: np.ndarray,
    leaves: np.ndarray,
) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        dest,
        pot=np.asarray(pot, dtype=np.uint8),
        trunk=np.asarray(trunk, dtype=np.uint8),
        leaves=np.asarray(leaves, dtype=np.uint8),
    )


def write_chosen_iou(path: PathLike, chosen_iou: Mapping[str, float]) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps({name: float(chosen_iou[name]) for name in GROUP_NAMES}, indent=2)
    )


def write_material_tags(path: PathLike, tags: np.ndarray) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tensor = torch.from_numpy(np.asarray(tags, dtype=np.int32))
    if tensor.ndim != 1:
        raise ValueError(f"material tags must be (N,), got {tuple(tensor.shape)}")
    torch.save(tensor, dest)
