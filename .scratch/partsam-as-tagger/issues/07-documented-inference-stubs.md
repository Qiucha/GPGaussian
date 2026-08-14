# 07 - May the documented inference path use the trial stubs

Type: grilling
Status: resolved
Blocked by: 02

## Question

May the spec document the ficus trial’s inference substitutes (PyTorch `torkit3d` FPS stub; apex/pointops not compiled) as the **supported** path, or is “stubs as if they were official” a **NO**?

Use [Which CUDA extensions PartSAM inference actually needs](02-inference-cuda-extensions.md). Map Notes: **NO** if inference depends on unreproducible stubs as the official path. Do not compile extensions in this ticket.

## Answer

The spec **may** document the trial substitutes as **this repo’s** supported three-click path. That is **not** a standing NO.

**torkit3d:** The in-repo PyTorch FPS stand-in (deterministic, first seed index 0; [torkit3d_stub.py](../../partsam-ficus-trial/torkit3d_stub.py)) is the **contract**. Compiling real torkit3d is outside this path. The spec says this is a local stand-in, not what PartSAM ships.

**apex / pointops:** The supported three-click `predict_masks` path does **not** compile them. They are unused on that driver ([Which CUDA extensions PartSAM inference actually needs](02-inference-cuda-extensions.md)), not stubbed.

The map’s NO (“unreproducible stubs as if they were the official path”) does not fire: the stub is checked-in Python (reproducible); “official” means PartSAM upstream, which we do not claim.
