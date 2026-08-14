import torch
tags = torch.load("output/config/material_tags.pt")
print("Unique tags:", torch.unique(tags, return_counts=True))
