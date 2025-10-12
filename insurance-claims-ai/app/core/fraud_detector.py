import cv2
import numpy as np
from PIL import Image
import imagehash
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

class FraudDetector:
    def __init__(self, db_path: str = "claims.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database for tracking claims"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create claims table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_hash TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                damage_type TEXT NOT NULL,
                severity FLOAT NOT NULL,
                location TEXT,
                device_id TEXT,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def check_fraud(self, image: Image.Image, metadata: Dict) -> Dict:
        """
        Check for potential fraud in the claim
        """
        # Generate image hash
        img_hash = str(imagehash.average_hash(image))
        
        # Check for duplicate claims
        duplicates = self._check_duplicates(img_hash)
        
        # Check for suspicious patterns
        suspicious = self._check_suspicious_patterns(metadata)
        
        # Calculate fraud probability
        fraud_probability = self._calculate_fraud_probability(duplicates, suspicious)
        
        # Log the claim
        self._log_claim(img_hash, metadata)
        
        return {
            "fraud_probability": fraud_probability,
            "duplicate_claims": len(duplicates),
            "suspicious_patterns": suspicious,
            "recommendations": self._generate_recommendations(fraud_probability)
        }
    
    def _check_duplicates(self, image_hash: str) -> List[Dict]:
        """
        Check for duplicate claims using image hash
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, damage_type, severity, location
            FROM claims
            WHERE image_hash = ?
            ORDER BY timestamp DESC
        ''', (image_hash,))
        
        duplicates = []
        for row in cursor.fetchall():
            duplicates.append({
                "timestamp": row[0],
                "damage_type": row[1],
                "severity": row[2],
                "location": row[3]
            })
        
        conn.close()
        return duplicates
    
    def _check_suspicious_patterns(self, metadata: Dict) -> List[str]:
        """
        Check for suspicious patterns in claims
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        suspicious_patterns = []
        device_id = metadata.get("device_id", "unknown")
        location = metadata.get("location", "unknown")
        
        # Check for multiple claims from same device
        cursor.execute('''
            SELECT COUNT(*)
            FROM claims
            WHERE device_id = ? AND timestamp > datetime('now', '-24 hours')
        ''', (device_id,))
        
        if cursor.fetchone()[0] >= 3:
            suspicious_patterns.append("Multiple claims from same device in 24 hours")
        
        # Check for multiple claims from same location
        cursor.execute('''
            SELECT COUNT(*)
            FROM claims
            WHERE location = ? AND timestamp > datetime('now', '-24 hours')
        ''', (location,))
        
        if cursor.fetchone()[0] >= 5:
            suspicious_patterns.append("Multiple claims from same location in 24 hours")
        
        conn.close()
        return suspicious_patterns
    
    def _calculate_fraud_probability(self, duplicates: List[Dict], suspicious_patterns: List[str]) -> float:
        """
        Calculate probability of fraudulent claim
        """
        fraud_score = 0.0
        
        # Add score for duplicates
        if duplicates:
            fraud_score += 0.4
        
        # Add score for suspicious patterns
        fraud_score += len(suspicious_patterns) * 0.2
        
        return min(fraud_score, 1.0)
    
    def _log_claim(self, image_hash: str, metadata: Dict):
        """
        Log claim details to database
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO claims (
                image_hash, timestamp, damage_type, severity,
                location, device_id, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            image_hash,
            datetime.now().isoformat(),
            metadata.get("damage_type", "unknown"),
            metadata.get("severity", 0.0),
            metadata.get("location", "unknown"),
            metadata.get("device_id", "unknown"),
            str(metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def _generate_recommendations(self, fraud_probability: float) -> str:
        """
        Generate recommendations based on fraud probability
        """
        if fraud_probability > 0.7:
            return "High risk of fraud. Manual review required."
        elif fraud_probability > 0.4:
            return "Medium risk. Additional verification recommended."
        return "Low risk. Standard processing recommended."