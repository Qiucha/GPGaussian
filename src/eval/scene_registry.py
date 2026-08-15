"""Canonical multi-material 3DGS scenes for batch pipeline QA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class SceneSpec:
    """One multi-material scene in the digest / pipeline QA set."""

    id: str
    model_dir: str
    config: str
    tagger: str  # partsam | vasedeck_heuristic | segmenter_agent
    category: str
    description: str


CANONICAL_SCENES: List[SceneSpec] = [
    SceneSpec(
        id="ficus",
        model_dir="ficus_whitebg",
        config="configs/ficus.json",
        tagger="partsam",
        category="ficus",
        description="Plant with pot / trunk / leaves (PartSAM tags 1–3)",
    ),
    SceneSpec(
        id="vasedeck",
        model_dir="vasedeck_whitebg",
        config="configs/vasedeck_multi_material.json",
        tagger="vasedeck_heuristic",
        category="vasedeck",
        description="Vase on deck with multi-tag color/spatial heuristic",
    ),
    SceneSpec(
        id="bread",
        model_dir="bread-trained",
        config="configs/tear_bread_multi_material.json",
        tagger="segmenter_agent",
        category="tear_bread",
        description="Tear-bread crust/crumb materials",
    ),
    SceneSpec(
        id="plane",
        model_dir="plane-trained",
        config="configs/plane_multi_material.json",
        tagger="segmenter_agent",
        category="plane",
        description="Aircraft fuselage/wings materials",
    ),
    SceneSpec(
        id="pillow2sofa",
        model_dir="pillow2sofa_whitebg-trained",
        config="configs/pillow2sofa_multi_material.json",
        tagger="segmenter_agent",
        category="pillow2sofa",
        description="Pillow/sofa structure vs cushion materials",
    ),
    SceneSpec(
        id="wolf",
        model_dir="wolf_whitebg-trained",
        config="configs/wolf_multi_material.json",
        tagger="segmenter_agent",
        category="wolf",
        description="Wolf base / detail / body materials",
    ),
]


def get_scene(scene_id: str) -> SceneSpec:
    for scene in CANONICAL_SCENES:
        if scene.id == scene_id:
            return scene
    known = ", ".join(s.id for s in CANONICAL_SCENES)
    raise KeyError(f"Unknown scene id {scene_id!r}. Known: {known}")


def select_scenes(ids: Optional[Sequence[str]] = None) -> List[SceneSpec]:
    if not ids:
        return list(CANONICAL_SCENES)
    return [get_scene(scene_id) for scene_id in ids]
