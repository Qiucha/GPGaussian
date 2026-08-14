import os
import json
import numpy as np

from bbox_extraction import BBoxExtractor
from llm_generator import ConfigGenerator

def test_bbox_and_llm():
    print("Testing Bounding Box Extraction and LLM Config Generation...")
    
    # 1. Create dummy 3D points and labels
    points = np.array([
        # Pot points (centered around 0, 0, 0.25)
        [0.1, 0.1, 0.1],
        [-0.1, -0.1, 0.4],
        # Trunk points (centered around 0, 0, 1.0)
        [0.05, 0.05, 0.5],
        [-0.05, -0.05, 1.5],
        # Leaves points (centered around 0, 0, 2.5)
        [0.5, 0.5, 2.0],
        [-0.5, -0.5, 3.0]
    ])
    
    labels = np.array(['pot', 'pot', 'trunk', 'trunk', 'leaves', 'leaves'])
    
    # 2. Extract bounding boxes
    extractor = BBoxExtractor()
    bboxes = extractor.extract_bounding_boxes(points, labels, ["pot", "trunk", "leaves"])
    
    print("\nExtracted Bounding Boxes:")
    for label, bbox in bboxes.items():
        print(f"  {label}: {bbox}")
        
    assert 'pot' in bboxes
    assert 'trunk' in bboxes
    assert 'leaves' in bboxes
    
    # 3. Test LLM generation (using local Ollama)
    print("\nTesting LLM Config Generation via Ollama...")
    generator = ConfigGenerator()
    output_file = "test_output_config.json"
    
    try:
        generator.generate_config(bboxes, output_file)
        
        with open(output_file, 'r') as f:
            config = json.load(f)
            
        print(f"Config successfully generated and loaded. Keys: {list(config.keys())}")
        if "additional_material_params" in config:
            print(f"Number of additional_material_params: {len(config['additional_material_params'])}")
        
        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)
            
    except Exception as e:
        print(f"Error during LLM generation (is Ollama running?): {e}")

if __name__ == "__main__":
    test_bbox_and_llm()
