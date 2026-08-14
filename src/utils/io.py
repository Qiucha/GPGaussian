"""
Common I/O helpers for loading/saving tags and other artifacts.
"""

import os
import torch


def load_tags(tags_path, device="cpu"):
    """Load material tags tensor from file."""
    tags = torch.load(tags_path, weights_only=True)
    return tags.to(device)


def save_tags(tags, output_path):
    """Save material tags tensor to file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torch.save(tags, output_path)
    print(f"Material tags saved to {output_path}")


def get_project_root():
    """Return the absolute path to the project root directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
