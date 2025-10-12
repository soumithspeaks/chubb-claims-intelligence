import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import json
from typing import Dict, Tuple, List

class DamageDetector:
    def __init__(self):
        self.damage_types = {
            "scratch": {"base_cost": 500, "severity_multiplier": 1.5},
            "dent": {"base_cost": 800, "severity_multiplier": 2.0},
            "crack": {"base_cost": 1200, "severity_multiplier": 2.5},
            "broken": {"base_cost": 2000, "severity_multiplier": 3.0}
        }
        
    def process_image(self, image: Image.Image) -> Dict:
        """
        Process image and detect damage
        """
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Image preprocessing
        processed = self._preprocess_image(cv_image)
        
        # Detect edges and contours
        edges, contours = self._detect_edges_contours(processed)
        
        # Analyze damage
        damage_type, severity = self._analyze_damage(edges, contours)
        
        # Calculate costs
        cost_estimate = self._estimate_cost(damage_type, severity)
        
        return {
            "damage_type": damage_type,
            "severity": severity,
            "confidence": self._calculate_confidence(edges, contours),
            "estimated_cost": cost_estimate,
            "repair_time": self._estimate_repair_time(damage_type, severity),
            "recommendations": self._generate_recommendations(damage_type, severity)
        }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better damage detection
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        return thresh
    
    def _detect_edges_contours(self, image: np.ndarray) -> Tuple[np.ndarray, List]:
        """
        Detect edges and contours in the image
        """
        # Edge detection
        edges = cv2.Canny(image, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        return edges, contours
    
    def _analyze_damage(self, edges: np.ndarray, contours: List) -> Tuple[str, float]:
        """
        Analyze the type and severity of damage
        """
        # Calculate edge density
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Calculate contour characteristics
        total_area = sum(cv2.contourArea(cnt) for cnt in contours)
        max_area = max((cv2.contourArea(cnt) for cnt in contours), default=0)
        
        # Determine damage type
        if edge_density > 0.15 and max_area > 1000:
            damage_type = "broken"
            severity = min(edge_density * 3, 1.0)
        elif edge_density > 0.1:
            damage_type = "crack"
            severity = min(edge_density * 2.5, 1.0)
        elif edge_density > 0.05:
            damage_type = "dent"
            severity = min(edge_density * 2, 1.0)
        else:
            damage_type = "scratch"
            severity = min(edge_density * 1.5, 1.0)
        
        return damage_type, severity
    
    def _calculate_confidence(self, edges: np.ndarray, contours: List) -> float:
        """
        Calculate confidence score for the damage detection
        """
        if not contours:
            return 0.5
            
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        contour_area = sum(cv2.contourArea(cnt) for cnt in contours)
        
        confidence = min(0.5 + edge_density + (contour_area / 10000), 1.0)
        return round(confidence, 2)
    
    def _estimate_cost(self, damage_type: str, severity: float) -> float:
        """
        Estimate repair cost based on damage type and severity
        """
        damage_info = self.damage_types.get(damage_type, self.damage_types["scratch"])
        base_cost = damage_info["base_cost"]
        multiplier = damage_info["severity_multiplier"]
        
        return round(base_cost * (1 + severity * multiplier))
    
    def _estimate_repair_time(self, damage_type: str, severity: float) -> str:
        """
        Estimate repair time based on damage type and severity
        """
        if severity > 0.8:
            return "3-5 days"
        elif severity > 0.5:
            return "2-3 days"
        elif severity > 0.3:
            return "1-2 days"
        return "Same day repair possible"
    
    def _generate_recommendations(self, damage_type: str, severity: float) -> str:
        """
        Generate repair recommendations
        """
        if severity > 0.7:
            return "Immediate repair recommended. High risk of further damage."
        elif severity > 0.4:
            return "Repair recommended within 2 weeks. Monitor for deterioration."
        return "Minor damage. Cosmetic repair suggested."