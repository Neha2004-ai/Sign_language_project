import numpy as np
import sys
import os

# Ensure backend root is accessible
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
from app.ml.feature_extractor import LandmarkFeatureExtractor

def extract_features_from_sample(landmarks_list):
    """Utility function to extract 93-dimensional feature vectors."""
    return LandmarkFeatureExtractor.extract_full_feature_vector(landmarks_list)
