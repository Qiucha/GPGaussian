import numpy as np

class BBoxExtractor:
    def __init__(self):
        pass
        
    def extract_bounding_boxes(self, points: np.ndarray, labels: np.ndarray, target_labels: list):
        """
        Groups points by their labels and computes axis-aligned bounding boxes.
        
        Args:
            points: numpy array of shape (N, 3)
            labels: numpy array of shape (N,) containing label strings
            target_labels: list of strings (e.g., ["pot", "trunk", "leaves"])
            
        Returns:
            A dictionary mapping each label to its bounding box [xmin, xmax, ymin, ymax, zmin, zmax].
            If a label has no points, it will not be included in the dictionary.
        """
        bboxes = {}
        
        for label in target_labels:
            mask = labels == label
            if not np.any(mask):
                continue
                
            group_points = points[mask]
            
            xmin = np.min(group_points[:, 0])
            xmax = np.max(group_points[:, 0])
            ymin = np.min(group_points[:, 1])
            ymax = np.max(group_points[:, 1])
            zmin = np.min(group_points[:, 2])
            zmax = np.max(group_points[:, 2])
            
            bboxes[label] = [float(xmin), float(xmax), float(ymin), float(ymax), float(zmin), float(zmax)]
            
        return bboxes

if __name__ == "__main__":
    # Example usage
    # points = np.random.rand(100, 3)
    # labels = np.array(['pot'] * 50 + ['leaves'] * 50)
    # extractor = BBoxExtractor()
    # bboxes = extractor.extract_bounding_boxes(points, labels, ["pot", "leaves"])
    # print(bboxes)
    pass
