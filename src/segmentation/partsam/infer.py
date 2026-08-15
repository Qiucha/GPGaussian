"""Stage 3: PartSAM predict_masks (PartSAM env), then merge + lift."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Union

import numpy as np
import torch

from src.segmentation.partsam.clicks import clicks_json_path, load_clicks, validate_clicks
from src.segmentation.partsam.merge import (
    CHOSEN_IOU_NAME,
    DEFAULT_TAGS_PATH,
    GROUP_NAMES,
    PART_MASKS_NAME,
    apply_survival,
    rematerialize_tags,
    write_chosen_iou,
    write_material_tags,
    write_part_masks,
)
from src.segmentation.partsam.surface import (
    MESH_NAME,
    load_gaussian_means_rgb,
    load_sample_100k,
    sample_npz_path,
)

PathLike = Union[str, Path]


def _load_mesh(path: Path) -> tuple[np.ndarray, np.ndarray]:
    import trimesh

    mesh = trimesh.load(str(path), force="mesh", file_type="ply")
    if not isinstance(mesh, trimesh.Trimesh) or mesh.faces is None or len(mesh.faces) == 0:
        raise RuntimeError(f"not a triangle mesh: {path}")
    return np.asarray(mesh.vertices), np.asarray(mesh.faces)


def mesh_normalize(
    xyz: np.ndarray, clicks: np.ndarray, verts: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    bbmin, bbmax = verts.min(0), verts.max(0)
    center = (bbmin + bbmax) * 0.5
    scale = 2.0 * 0.9 / (bbmax - bbmin).max()
    return (xyz - center) * scale, (clicks - center) * scale, (verts - center) * scale


def clicks_through_prep(xyz: np.ndarray, clicks: np.ndarray) -> np.ndarray:
    x_min, y_min, z_min = xyz.min(axis=0)
    x_max, y_max, z_max = xyz.max(axis=0)
    shift = np.array([(x_min + x_max) / 2, (y_min + y_max) / 2, (z_min + z_max) / 2])
    xyz_s = xyz - shift
    clk_s = clicks - shift
    bbmin, bbmax = xyz_s.min(0), xyz_s.max(0)
    center, scale = (bbmin + bbmax) * 0.5, 2.0 * 0.9 / (bbmax - bbmin).max()
    return (clk_s - center) * scale


def world_to_prompt(
    world_xyz: np.ndarray, xyz: np.ndarray, mesh_verts: np.ndarray
) -> np.ndarray:
    xyz_n, clk_mesh, _ = mesh_normalize(xyz, world_xyz, mesh_verts)
    return clicks_through_prep(xyz_n, clk_mesh)


def pick_best(masks: torch.Tensor, iou: torch.Tensor) -> tuple[np.ndarray, float]:
    iou_d = iou.detach()
    best = iou_d.argmax(dim=-1)
    if masks.dim() == 3:
        chosen_idx = int(best.reshape(-1)[0].item())
        mask = masks[0, chosen_idx]
        chosen_iou = float(iou_d.reshape(-1)[chosen_idx].item())
    else:
        mask = masks[0]
        chosen_iou = float(iou_d.reshape(-1).max().item())
    return (mask > 0).cpu().numpy().astype(np.uint8), chosen_iou


def _load_partsam_model(root: Path):
    import hydra
    from omegaconf import OmegaConf
    from safetensors.torch import load_model

    from src.segmentation.partsam.fps import install

    install()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    with hydra.initialize_config_dir(str(root / "configs"), version_base=None):
        cfg = hydra.compose(config_name="partsam")
        OmegaConf.resolve(cfg)
    model = hydra.utils.instantiate(cfg.model)
    weights = root / "pretrained" / "model.safetensors"
    if not weights.is_file():
        raise FileNotFoundError(f"PartSAM weights not found: {weights}")
    load_model(model, str(weights))
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return model, device


def _prep_points_train(xyz, color, normal, vertices):
    from utils.aug import CenterShift, NormalizeColor, NormalizeMy, ToTensor

    data_dict = {"coord": xyz, "color": color, "normal": normal, "vertices": vertices}
    data_dict = CenterShift(apply_z=True)(data_dict)
    data_dict = NormalizeMy()(data_dict)
    data_dict = NormalizeColor()(data_dict)
    data_dict = ToTensor()(data_dict)
    return data_dict


def predict_group_masks(
    sample: dict[str, np.ndarray],
    clicks: dict[str, Any],
    mesh_verts: np.ndarray,
    faces: np.ndarray,
    model,
    device: torch.device,
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    xyz = sample["coords"].astype(np.float64)
    color = sample["colors"]
    normal = sample["normals"].astype(np.float64)
    p2f = sample["point_to_face"]
    world_pos = {}
    for name in GROUP_NAMES:
        pts = np.array(clicks["groups"][name]["positives"], dtype=np.float64)
        world_pos[name] = pts
    xyz_n, _, verts_n = mesh_normalize(xyz, world_pos["pot"][:1], mesh_verts)
    data = _prep_points_train(xyz_n, color, normal, verts_n)
    coords = data["coord"].float().to(device).unsqueeze(0)
    col = data["color"].float().to(device).unsqueeze(0)
    nor = data["normal"].float().to(device).unsqueeze(0)
    dummy_p2f = torch.from_numpy(p2f.astype(np.int64)).to(device).unsqueeze(0)
    dummy_v = data["vertices"].float().to(device).unsqueeze(0)
    dummy_f = torch.from_numpy(faces[:1].astype(np.int64)).to(device).unsqueeze(0)

    def run_prompt(pos_world: np.ndarray, neg_world: np.ndarray | None) -> tuple[np.ndarray, float]:
        pos_n = world_to_prompt(np.atleast_2d(pos_world), xyz, mesh_verts)
        if neg_world is None or len(np.atleast_2d(neg_world)) == 0:
            prompt_np = pos_n
            labels_np = np.ones(len(pos_n), dtype=np.int64)
        else:
            neg_n = world_to_prompt(np.atleast_2d(neg_world), xyz, mesh_verts)
            prompt_np = np.concatenate([pos_n, neg_n], axis=0)
            labels_np = np.concatenate(
                [
                    np.ones(len(pos_n), dtype=np.int64),
                    np.zeros(len(neg_n), dtype=np.int64),
                ]
            )
        prompt = torch.from_numpy(prompt_np).float().to(device).view(1, -1, 3)
        labels = torch.from_numpy(labels_np).to(device=device).view(1, -1)
        sel = torch.zeros(1, dtype=torch.long, device=device)
        masks, iou = model.predict_masks(
            coords=coords,
            color=col,
            normal=nor,
            point_to_face=dummy_p2f,
            vertices=dummy_v,
            faces=dummy_f,
            prompt_coords=prompt,
            selected_indices=sel,
            prompt_labels=labels,
            multimask_output=True,
        )
        return pick_best(masks, iou)

    out: dict[str, np.ndarray] = {}
    ious: dict[str, float] = {}
    with torch.no_grad():
        for name in GROUP_NAMES:
            negatives = np.array(
                clicks["groups"][name].get("negatives") or [], dtype=np.float64
            )
            mask, iou = run_prompt(
                world_pos[name],
                negatives if negatives.size else None,
            )
            out[name] = mask
            ious[name] = iou
    return out, ious


def run_stage_lift(
    model_path: PathLike,
    output_dir: PathLike,
    tags_path: PathLike = DEFAULT_TAGS_PATH,
    *,
    reuse_tags: bool = False,
) -> Path:
    dest = Path(tags_path)
    if reuse_tags and dest.exists():
        return dest
    out = Path(output_dir)
    gaussian_xyz, _ = load_gaussian_means_rgb(model_path)
    masks_path = out / PART_MASKS_NAME
    iou_path = out / CHOSEN_IOU_NAME
    if masks_path.is_file() and iou_path.is_file():
        return rematerialize_tags(out, dest, gaussian_xyz)

    from src.upstream import get_partsam_root

    sample = load_sample_100k(sample_npz_path(out))
    clicks = load_clicks(clicks_json_path(out))
    validate_clicks(clicks)
    mesh_verts, faces = _load_mesh(out / MESH_NAME)
    model, device = _load_partsam_model(Path(get_partsam_root()))
    masks, ious = predict_group_masks(dict(sample), clicks, mesh_verts, faces, model, device)
    write_part_masks(out / PART_MASKS_NAME, masks["pot"], masks["trunk"], masks["leaves"])
    write_chosen_iou(out / CHOSEN_IOU_NAME, ious)
    lifted = apply_survival(
        masks["pot"],
        masks["trunk"],
        masks["leaves"],
        ious,
        np.asarray(sample["coords"]),
        gaussian_xyz,
    )
    write_material_tags(dest, lifted)
    return dest
