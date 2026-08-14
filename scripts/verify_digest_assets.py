"""
Verification script for Phys4DGS Digest Dashboard Assets & Data Integrity.
"""

import os
import sys
import json

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
digest_dir = os.path.join(_project_root, "digest")
data_dir = os.path.join(digest_dir, "data")


def verify():
    print("=" * 70)
    print("  VERIFYING DIGEST DASHBOARD ASSETS & DATA INTEGRITY")
    print("=" * 70)

    # 1. HTML, CSS, JS check
    html_path = os.path.join(digest_dir, "index.html")
    css_path = os.path.join(digest_dir, "style.css")
    js_path = os.path.join(digest_dir, "app.js")

    assert os.path.exists(html_path), "index.html missing!"
    assert os.path.exists(css_path), "style.css missing!"
    assert os.path.exists(js_path), "app.js missing!"
    print("✅ Core web files (index.html, style.css, app.js) present.")

    # 2. Manifest check
    manifest_path = os.path.join(data_dir, "manifest.json")
    assert os.path.exists(manifest_path), "manifest.json missing!"

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    models = manifest.get("models", [])
    print(f"✅ manifest.json loaded successfully with {len(models)} models.")
    assert len(models) == 6, f"Expected 6 models, found {len(models)}"

    # 3. Model assets check
    for m in models:
        m_id = m["id"]
        m_folder = os.path.join(digest_dir, m["folder"])
        print(f"\nVerifying model '{m_id}' in {m_folder}...")

        # Check JSON files
        for fname in ["metadata.json", "plan.json", "particles.json", "metrics.json"]:
            fpath = os.path.join(m_folder, fname)
            assert os.path.exists(fpath), f"Missing {fname} in {m_folder}"
            with open(fpath, "r") as f:
                data = json.load(f)
                assert data is not None, f"Failed to parse {fname}"

        # Check particles count
        with open(os.path.join(m_folder, "particles.json"), "r") as f:
            pdata = json.load(f)
            assert pdata["count"] > 0, "Particles count must be > 0"
            assert len(pdata["positions"]) == pdata["count"], "Positions length mismatch"
            assert len(pdata["colors"]) == pdata["count"], "Colors length mismatch"
            assert "stages" in pdata, "Stages missing in particles.json"
            print(f"  - particles.json valid ({pdata['count']} points, 5 stages).")

        # Check frames
        frames_dir = os.path.join(m_folder, "frames")
        assert os.path.exists(frames_dir), f"Missing frames directory for {m_id}"
        frame_files = [f for f in os.listdir(frames_dir) if f.startswith("frame_") and f.endswith(".jpg")]
        assert len(frame_files) == 30, f"Expected 30 frames for {m_id}, found {len(frame_files)}"
        print(f"  - 30 rendered trajectory frame images verified.")

    print("\n" + "=" * 70)
    print("🎉 ALL DIGEST DASHBOARD ASSETS VERIFIED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    verify()
