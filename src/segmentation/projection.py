import os
import json
import numpy as np
import cv2
from plyfile import PlyData

class Projector3D:
    def __init__(self, ply_file: str, camera_params_dict: dict, masks_dir: str):
        self.ply_file = ply_file
        self.camera_params_dict = camera_params_dict
        self.masks_dir = masks_dir
        
        self.points = self._load_ply()
        self.num_points = self.points.shape[0]

    def _load_ply(self):
        print(f"Loading point cloud from {self.ply_file}...")
        plydata = PlyData.read(self.ply_file)
        v = plydata['vertex']
        points = np.vstack([v['x'], v['y'], v['z']]).T
        return points

    def _project_points(self, W2C, K, width, height):
        """ Projects 3D points to 2D image plane for a specific camera. """
        pts_h = np.hstack((self.points, np.ones((self.num_points, 1))))
        pts_c = (W2C @ pts_h.T).T
        valid_depth = pts_c[:, 2] > 0
        
        if K.shape == (4, 4):
            pts_ndc_h = (K @ pts_c.T).T
            pts_ndc = pts_ndc_h[:, :3] / pts_ndc_h[:, 3:]
            pts_2d = np.zeros((self.num_points, 2))
            pts_2d[:, 0] = (pts_ndc[:, 0] + 1.0) * width * 0.5
            pts_2d[:, 1] = (1.0 - pts_ndc[:, 1]) * height * 0.5 
        else:
            pts_2d_h = (K @ pts_c[:, :3].T).T
            pts_2d = pts_2d_h[:, :2] / pts_2d_h[:, 2:]
            
        return pts_2d, valid_depth

    def assign_labels(self, text_prompts: list):
        """
        Assign semantic labels to 3D points using multi-view voting.
        """
        print("Assigning labels via multi-view projection...")
        
        votes = {prompt: np.zeros(self.num_points, dtype=int) for prompt in text_prompts}
        
        for img_name, cam in self.camera_params_dict.items():
            pts_2d, valid_depth = self._project_points(cam['W2C'], cam['K'], cam['width'], cam['height'])
            
            width = cam['width']
            height = cam['height']
            
            base_name = os.path.splitext(img_name)[0]
            
            # Load all masks and compute their areas
            masks = {}
            for prompt in text_prompts:
                mask_name = f"{base_name}_{prompt}.png"
                mask_path = os.path.join(self.masks_dir, mask_name)
                if os.path.exists(mask_path):
                    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                    if mask is not None:
                        masks[prompt] = mask > 128
            
            if not masks:
                continue
                
            # Sort prompts by area (largest to smallest)
            prompts_by_area = sorted(masks.keys(), key=lambda p: np.sum(masks[p]), reverse=True)
            
            u = np.round(pts_2d[:, 0]).astype(int)
            v = np.round(pts_2d[:, 1]).astype(int)
            
            valid_uv = (u >= 0) & (u < width) & (v >= 0) & (v < height)
            valid = valid_depth & valid_uv
            
            u_valid = u[valid]
            v_valid = v[valid]
            valid_indices = np.where(valid)[0]
            
            # Start by assigning 'none'
            point_labels = np.array(['none'] * len(valid_indices), dtype=object)
            
            # Apply masks in order of largest to smallest area, so smaller masks overwrite larger ones
            for prompt in prompts_by_area:
                mask_values = masks[prompt][v_valid, u_valid]
                point_labels[mask_values] = prompt
                
            # Add votes based on the winning 2D label for this view
            for prompt in masks.keys():
                hit_indices = valid_indices[point_labels == prompt]
                votes[prompt][hit_indices] += 1
                
        # Determine the label with the max votes for each point
        labels = np.array(['none'] * self.num_points, dtype=object)
        max_votes = np.zeros(self.num_points, dtype=int)
        
        for prompt in text_prompts:
            better = votes[prompt] > max_votes
            labels[better] = prompt
            max_votes[better] = votes[prompt][better]
            
        return labels, self.points

if __name__ == "__main__":
    pass
