import torch
import numpy as np
from PIL import Image
import cv2
from transformers import pipeline
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
import tensorflow.keras.backend as K

class AdvancedDamageDetector:
    def __init__(self):
        # Load text-image model
        self.text_classifier = pipeline("zero-shot-classification")
        
        # Load ResNet model
        self.resnet_model = ResNet50(weights='imagenet', include_top=True)
        
        self.damage_types = {
            "scratch": {"base_cost": 500, "severity_multiplier": 1.5},
            "dent": {"base_cost": 800, "severity_multiplier": 2.0},
            "crack": {"base_cost": 1200, "severity_multiplier": 2.5},
            "broken": {"base_cost": 2000, "severity_multiplier": 3.0}
        }
    
    def grad_cam(self, img_array, pred_index=None):
        """Generate Grad-CAM visualization"""
        # Get the last conv layer
        last_conv_layer = self.resnet_model.get_layer('conv5_block3_out')
        
        # Gradient model
        grad_model = tf.keras.Model(
            [self.resnet_model.inputs],
            [last_conv_layer.output, self.resnet_model.output]
        )
        
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            if pred_index is None:
                pred_index = tf.argmax(predictions[0])
            class_channel = predictions[:, pred_index]
        
        # Gradient of the predicted class with regard to the output feature map
        grads = tape.gradient(class_channel, conv_outputs)
        
        # Vector of mean intensity of the gradient over a specific feature map channel
        pooled_grads = K.mean(grads, axis=(0, 1, 2))
        
        # Weight the channels by corresponding gradients
        conv_outputs = conv_outputs[0]
        heatmap = tf.reduce_mean(tf.multiply(pooled_grads, conv_outputs), axis=-1)
        
        # Normalize the heatmap
        heatmap = np.maximum(heatmap, 0) / np.max(heatmap)
        
        return heatmap
    
    def analyze_image_text(self, image: Image.Image, description: str) -> dict:
        """Analyze both image and text description"""
        # Convert image for ResNet
        img_array = preprocess_input(np.expand_dims(
            cv2.resize(np.array(image), (224, 224)), axis=0
        ))
        
        # Get visual features
        visual_features = self.resnet_model.predict(img_array)
        
        # Get text analysis
        text_analysis = self.text_classifier(
            description,
            candidate_labels=["scratch", "dent", "crack", "broken"]
        )
        
        # Generate explanation heatmap
        heatmap = self.grad_cam(img_array)
        
        # Combine visual and textual analysis
        damage_type = text_analysis['labels'][0]
        confidence = text_analysis['scores'][0]
        
        # Calculate severity based on visual features
        severity = np.mean(visual_features) * confidence
        
        return {
            "damage_type": damage_type,
            "severity": float(severity),
            "confidence": float(confidence),
            "visual_explanation": heatmap,
            "text_analysis": text_analysis,
            "recommendations": self._generate_recommendations(damage_type, severity)
        }
    
    def _generate_recommendations(self, damage_type: str, severity: float) -> str:
        if severity > 0.7:
            return "Immediate repair recommended. High risk of further damage."
        elif severity > 0.4:
            return "Repair recommended within 2 weeks. Monitor for deterioration."
        return "Minor damage. Cosmetic repair suggested."