import os
import json
import time
from typing import Dict, Any, List, Optional
import numpy as np

# Model Registry and Metadata
class ModelRegistry:
    def __init__(self, model_dir: str = "../models"):
        self.model_dir = model_dir
        self.metadata_file = os.path.join(model_dir, "model_metadata.json")
        self.metadata = self.load_metadata()

    def load_metadata(self) -> Dict[str, Any]:
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default metadata
        return {
            "active_model": "demo_baseline_v1",
            "model_version": "1.0.0-mvp",
            "confidence_threshold": 0.65,
            "supported_gestures": [
                "HELLO", "THANK YOU", "YES", "NO", "HELP", 
                "GOODBYE", "PLEASE", "SORRY", "I LOVE YOU",
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
            ],
            "is_demo_model": True,
            "model_type": "Geometric Random Forest & Deep MLP Baseline",
            "last_trained": "2026-09-09",
            "hardware_accelerator": "CPU (Optimized for Laptop Deployment)",
            "dataset_samples_count": 1500
        }

    def save_metadata(self, metadata: Dict[str, Any]):
        os.makedirs(self.model_dir, exist_ok=True)
        self.metadata = metadata
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

model_registry = ModelRegistry()
