import torch
import numpy as np
from PIL import Image
from ultralytics import YOLO
from pathlib import Path
import cv2
import joblib
from typing import Dict, List, Tuple, Union

class DamageDetector:
    def __init__(self, model_dir=None):
        """
        Initialize the damage detector with YOLOv8 model
        
        Args:
            model_dir (str, optional): Path to directory containing model files
        """
        if model_dir is None:
            model_dir = Path(__file__).parent.parent.parent / 'models' / 'damage_detector'
        else:
            model_dir = Path(model_dir)
            
        # Load YOLO model for damage detection
        self.model = YOLO(model_dir / 'weights' / 'best.pt')
        
        # Load cost estimator model and components
        cost_estimator_dir = Path(__file__).parent.parent.parent / 'models' / 'cost_estimator'
        self.cost_model = joblib.load(cost_estimator_dir / 'model.joblib')
        self.feature_scaler = joblib.load(cost_estimator_dir / 'scaler.joblib')
        
        # Define damage types and severity levels
        self.damage_types = {
            0: 'scratch',
            1: 'dent',
            2: 'broken',
            3: 'crack',
            4: 'glass_shatter'
        }
        
        self.severity_thresholds = {
            'minor': 0.3,
            'moderate': 0.6,
            'severe': 0.8
        }
        
    def preprocess_image(self, image: Union[str, Image.Image]) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image: Path to image or PIL Image object
            
        Returns:
            np.ndarray: Preprocessed image
        """
        if isinstance(image, str):
            image = Image.open(image)
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
            
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Convert to numpy array
        img_array = np.array(image)
        
        return img_array
    
    def detect_damage(self, image: Union[str, Image.Image]) -> Dict:
        """
        Detect vehicle damage in image
        
        Args:
            image: Path to image or PIL Image object
            
        Returns:
            dict: Detection results with damage types, locations, and cost estimate
        """
        # Preprocess image
        img_array = self.preprocess_image(image)
        
        # Run detection
        results = self.model(img_array)[0]
        
        # Process detections
        damages = []
        total_severity = 0
        max_confidence = 0
        
        if len(results.boxes) > 0:
            boxes = results.boxes.cpu().numpy()
            
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].astype(int)
                confidence = box.conf[0]
                class_id = int(box.cls[0])
                
                # Calculate damage area and severity
                area = (x2 - x1) * (y2 - y1) / (img_array.shape[0] * img_array.shape[1])
                severity = self.calculate_severity(confidence, area)
                
                damages.append({
                    'type': self.damage_types[class_id],
                    'confidence': float(confidence),
                    'severity': severity,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
                
                total_severity += severity
                max_confidence = max(max_confidence, confidence)
        
        # Calculate cost estimate
        estimated_cost = self.estimate_repair_cost(damages)
        
        # Create annotated image
        annotated_img = self.annotate_image(img_array, damages)
        
        return {
            'damages_detected': len(damages) > 0,
            'damages': damages,
            'max_confidence': float(max_confidence),
            'total_severity': float(total_severity),
            'estimated_cost': float(estimated_cost),
            'annotated_image': Image.fromarray(annotated_img)
        }
    
    def calculate_severity(self, confidence: float, area: float) -> float:
        """
        Calculate damage severity based on confidence and area
        
        Args:
            confidence: Detection confidence
            area: Relative area of damage
            
        Returns:
            float: Severity score
        """
        # Combine confidence and area with weighted average
        severity = (0.7 * confidence + 0.3 * min(area * 10, 1))
        
        # Normalize to 0-1 range
        return min(max(severity, 0), 1)
    
    def estimate_repair_cost(self, damages: List[Dict]) -> float:
        """
        Estimate repair cost based on detected damages
        
        Args:
            damages: List of detected damages with types and severities
            
        Returns:
            float: Estimated repair cost
        """
        if not damages:
            return 0.0
            
        # Prepare features for cost model
        features = {
            damage_type: 0 for damage_type in self.damage_types.values()
        }
        
        max_severity = {
            damage_type: 0 for damage_type in self.damage_types.values()
        }
        
        # Aggregate damages by type
        for damage in damages:
            damage_type = damage['type']
            features[damage_type] += 1
            max_severity[damage_type] = max(max_severity[damage_type], damage['severity'])
            
        # Combine counts and severities
        feature_vector = []
        for damage_type in self.damage_types.values():
            feature_vector.extend([features[damage_type], max_severity[damage_type]])
            
        # Scale features
        scaled_features = self.feature_scaler.transform([feature_vector])
        
        # Predict cost
        estimated_cost = self.cost_model.predict(scaled_features)[0]
        
        return max(estimated_cost, 100)  # Minimum cost of $100
    
    def annotate_image(self, image: np.ndarray, damages: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image
        
        Args:
            image: Input image
            damages: List of detected damages
            
        Returns:
            np.ndarray: Annotated image
        """
        img_copy = image.copy()
        
        for damage in damages:
            x1, y1, x2, y2 = damage['bbox']
            damage_type = damage['type']
            confidence = damage['confidence']
            severity = damage['severity']
            
            # Determine color based on severity
            if severity < self.severity_thresholds['minor']:
                color = (0, 255, 0)  # Green
            elif severity < self.severity_thresholds['moderate']:
                color = (0, 255, 255)  # Yellow
            elif severity < self.severity_thresholds['severe']:
                color = (0, 165, 255)  # Orange
            else:
                color = (0, 0, 255)  # Red
            
            # Draw bounding box
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
            
            # Add label
            label = f"{damage_type} ({confidence:.2f})"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(img_copy, (x1, y1 - label_size[1] - 10), (x1 + label_size[0], y1), color, -1)
            cv2.putText(img_copy, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return img_copy
