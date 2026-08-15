"""Stage 1: Screened Poisson from Gaussian means → 100k P_in with baked SH RGB."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping, Union

import numpy as np
import torch
from plyfile import PlyData

from src.segmentation.heuristics import sh_dc_to_rgb

SAMPLE_NAME = "sample_100k.npz"
MESH_NAME = "poisson_mesh.ply"
SAMPLE_ID_KEY = "sample_id"
NUM_SURFACE_POINTS = 100_000
SAMPLE_SEED = 666
NN_CHUNK = 2048
MIN_POISSON_FACES = 1000

PathLike = Union[str, Path]


def sample_npz_path(output_dir: PathLike) -> Path:
    return Path(output_dir) / SAMPLE_NAME


def sample_id_from_coords(coords: np.ndarray) -> str:
    blob = np.ascontiguousarray(coords, dtype=np.float32).tobytes()
    return hashlib.sha256(blob).hexdigest()


def stored_sample_id(sample: Mapping[str, np.ndarray]) -> str | None:
    if SAMPLE_ID_KEY not in sample:
        return None
    raw = sample[SAMPLE_ID_KEY]
    if raw is None:
        return None
    value = str(np.asarray(raw).item())
    return value or None


def write_sample_100k(
    path: PathLike,
    coords: np.ndarray,
    normals: np.ndarray,
    colors: np.ndarray,
    point_to_face: np.ndarray,
) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    coords_f = np.asarray(coords, dtype=np.float32)
    np.savez(
        dest,
        coords=coords_f,
        normals=np.asarray(normals, dtype=np.float32),
        colors=np.asarray(colors, dtype=np.uint8),
        point_to_face=np.asarray(point_to_face, dtype=np.int32),
        **{SAMPLE_ID_KEY: np.array(sample_id_from_coords(coords_f))},
    )


def load_sample_100k(path: PathLike) -> Mapping[str, np.ndarray]:
    with np.load(path) as packed:
        out: dict[str, np.ndarray] = {
            "coords": packed["coords"],
            "normals": packed["normals"],
            "colors": packed["colors"],
            "point_to_face": packed["point_to_face"],
        }
        if SAMPLE_ID_KEY in packed.files:
            out[SAMPLE_ID_KEY] = packed[SAMPLE_ID_KEY]
        return out


def resolve_checkpoint_ply(model_path: PathLike) -> Path:
    root = Path(model_path)
    if root.is_file() and root.suffix == ".ply":
        return root
    cloud = root / "point_cloud"
    iterations = []
    if cloud.is_dir():
        for child in cloud.iterdir():
            if child.is_dir() and child.name.startswith("iteration_"):
                iterations.append(int(child.name.split("_", 1)[1]))
    if not iterations:
        raise FileNotFoundError(f"no point_cloud/iteration_*/point_cloud.ply under {root}")
    return cloud / f"iteration_{max(iterations)}" / "point_cloud.ply"


def load_gaussian_means_rgb(model_path: PathLike) -> tuple[np.ndarray, np.ndarray]:
    ply = PlyData.read(str(resolve_checkpoint_ply(model_path)))
    vertex = ply["vertex"]
    xyz = np.column_stack([vertex["x"], vertex["y"], vertex["z"]]).astype(np.float32)
    sh_dc = np.column_stack(
        [vertex["f_dc_0"], vertex["f_dc_1"], vertex["f_dc_2"]]
    ).astype(np.float32)
    rgb = sh_dc_to_rgb(torch.from_numpy(sh_dc)).numpy().astype(np.float32)
    return xyz, rgb


def reconstruct_screened_poisson(xyz: np.ndarray, mesh_path: PathLike) -> Path:
    import pymeshlab

    dest = Path(mesh_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    mesh_set = pymeshlab.MeshSet()
    mesh_set.add_mesh(pymeshlab.Mesh(vertex_matrix=np.asarray(xyz, dtype=np.float64)))
    mesh_set.compute_normal_for_point_clouds()
    mesh_set.generate_surface_reconstruction_screened_poisson()
    mesh = mesh_set.current_mesh()
    if mesh.face_number() < MIN_POISSON_FACES:
        raise RuntimeError(
            f"Screened Poisson produced too few faces ({mesh.face_number()})"
        )
    mesh_set.save_current_mesh(str(dest))
    return dest


def sample_surface_100k(mesh_path: PathLike) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    import trimesh

    mesh = trimesh.load(str(mesh_path), force="mesh", file_type="ply")
    if not isinstance(mesh, trimesh.Trimesh) or mesh.faces is None or len(mesh.faces) == 0:
        raise RuntimeError(f"not a triangle mesh: {mesh_path}")
    points, point_to_face = trimesh.sample.sample_surface(
        mesh, count=NUM_SURFACE_POINTS, seed=SAMPLE_SEED
    )
    normals = mesh.face_normals[point_to_face]
    return (
        np.asarray(points, dtype=np.float32),
        np.asarray(normals, dtype=np.float32),
        np.asarray(point_to_face, dtype=np.int32),
    )


def nearest_rgb(
    query: np.ndarray, ref_xyz: np.ndarray, ref_rgb: np.ndarray
) -> np.ndarray:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ref = torch.from_numpy(np.asarray(ref_xyz, dtype=np.float32)).to(device)
    rgb = torch.from_numpy(np.asarray(ref_rgb, dtype=np.float32)).to(device)
    out = np.empty((len(query), 3), dtype=np.float32)
    for start in range(0, len(query), NN_CHUNK):
        chunk = torch.from_numpy(query[start : start + NN_CHUNK].astype(np.float32)).to(
            device
        )
        idx = torch.cdist(chunk, ref).argmin(dim=1)
        out[start : start + NN_CHUNK] = rgb[idx].cpu().numpy()
    return out


def run_stage_surface(
    model_path: PathLike,
    output_dir: PathLike,
    *,
    skip_if_exists: bool = True,
) -> Path:
    dest = sample_npz_path(output_dir)
    if skip_if_exists and dest.exists():
        return dest
    xyz, gaussian_rgb = load_gaussian_means_rgb(model_path)
    mesh_path = Path(output_dir) / MESH_NAME
    reconstruct_screened_poisson(xyz, mesh_path)
    coords, normals, point_to_face = sample_surface_100k(mesh_path)
    colors = np.clip(
        np.round(nearest_rgb(coords, xyz, gaussian_rgb) * 255.0), 0, 255
    ).astype(np.uint8)
    write_sample_100k(dest, coords, normals, colors, point_to_face)
    return dest
