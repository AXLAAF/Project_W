"""
Risk Model interface (port).
Contract for ML risk prediction models.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any

from app.domain.entities.risk.risk_assessment import RiskAssessment
from app.domain.value_objects.risk import RiskScore, RiskFactor


class IRiskModel(ABC):
    """
    Interface for Risk Prediction Model.
    
    Acts as a port for the Machine Learning adapter.
    """
    
    @abstractmethod
    async def predict_risk(
        self,
        student_data: Dict[str, Any],
        attendance_stats: Dict[str, float],
        grade_stats: Dict[str, float],
        assignment_stats: Dict[str, float],
    ) -> RiskScore:
        """
        Predict risk score based on student data and stats.
        
        Args:
            student_data: Basic student info
            attendance_stats: Aggregate attendance metrics
            grade_stats: Aggregate grade metrics
            assignment_stats: Aggregate assignment metrics
            
        Returns:
            RiskScore object (0-100)
        """
        pass
    
    @abstractmethod
    async def analyze_factors(
        self,
        student_data: Dict[str, Any],
        history: List[RiskAssessment],
    ) -> List[Dict[str, Any]]:
        """
        Analyze contributing factors to the risk.
        
        Returns:
            List of factors with weights and descriptions.
        """
        pass
    
    @abstractmethod
    async def train(self, training_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Train the model with new data.
        
        Returns:
            Training metrics (accuracy, precision, etc.)
        """
        pass
    
    @abstractmethod
    async def get_version(self) -> str:
        """Get model version."""
        pass
