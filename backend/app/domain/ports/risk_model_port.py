"""
Risk Model Port.
Adapter interface for the Machine Learning model.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple


class IRiskModelPort(ABC):
    """Interface for the Risk Prediction Model."""
    
    @abstractmethod
    async def predict_risk(self, features: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Predict risk score based on student features.
        
        Args:
            features: Dictionary containing student data (attendance, grades, etc.)
            
        Returns:
            Tuple containing:
            - risk_score: Integer from 0-100
            - factor_details: Dictionary with breakdown of risk factors
        """
        pass
