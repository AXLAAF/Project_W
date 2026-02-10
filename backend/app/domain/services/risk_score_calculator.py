"""
Risk Score Calculator domain service.
Pure domain logic for calculating academic risk scores.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional

from app.domain.entities.risk.risk_assessment import RiskAssessment
from app.domain.entities.risk.attendance import AttendanceStats
from app.domain.entities.risk.assignment import AssignmentStats
from app.domain.value_objects.risk import RiskLevel, RiskScore


@dataclass
class RiskWeights:
    """Configuration for risk factor weights."""
    attendance: float = 0.30
    grades: float = 0.40
    assignments: float = 0.30
    
    def __post_init__(self):
        total = self.attendance + self.grades + self.assignments
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


@dataclass
class RiskThresholds:
    """Configuration for risk calculation thresholds."""
    attendance_critical: float = 70.0  # Below 70% attendance = critical
    grades_failing: float = 6.0        # Below 6 = failing
    assignments_missing: float = 30.0  # More than 30% missing = critical


class RiskScoreCalculator:
    """
    Domain service for calculating academic risk.
    
    Pure domain logic, no infrastructure dependencies.
    """
    
    def __init__(
        self,
        weights: Optional[RiskWeights] = None,
        thresholds: Optional[RiskThresholds] = None,
    ):
        self.weights = weights or RiskWeights()
        self.thresholds = thresholds or RiskThresholds()
    
    def calculate_attendance_risk(self, stats: AttendanceStats) -> int:
        """
        Calculate risk score from attendance.
        Lower attendance = higher risk score (0-100).
        """
        attendance_rate = stats.attendance_rate
        
        if attendance_rate >= 95:
            return 0
        elif attendance_rate >= 90:
            return 10
        elif attendance_rate >= 85:
            return 25
        elif attendance_rate >= 80:
            return 40
        elif attendance_rate >= 75:
            return 60
        elif attendance_rate >= self.thresholds.attendance_critical:
            return 75
        else:
            return 100
    
    def calculate_grades_risk(self, average: float) -> int:
        """
        Calculate risk score from grade average.
        Lower grades = higher risk score (0-100).
        """
        if average == 0:
            return 50  # No grades yet, moderate risk
        
        if average >= 9.0:
            return 0
        elif average >= 8.0:
            return 10
        elif average >= 7.0:
            return 25
        elif average >= 6.5:
            return 40
        elif average >= self.thresholds.grades_failing:
            return 55
        elif average >= 5.0:
            return 75
        else:
            return 100
    
    def calculate_assignments_risk(self, stats: AssignmentStats) -> int:
        """
        Calculate risk score from assignment submissions.
        More missing/late = higher risk score (0-100).
        """
        if stats.total_assignments == 0:
            return 0  # No assignments yet
        
        missing_rate = stats.missing_rate
        on_time_rate = stats.on_time_rate
        
        # Combined score based on missing and late
        if missing_rate > 50:
            return 100
        elif missing_rate > self.thresholds.assignments_missing:
            return 85
        elif on_time_rate >= 95:
            return 0
        elif on_time_rate >= 85:
            return 15
        elif on_time_rate >= 75:
            return 35
        elif on_time_rate >= 65:
            return 55
        elif on_time_rate >= 50:
            return 70
        else:
            return 90
    
    def calculate_total_score(
        self,
        attendance_score: int,
        grades_score: int,
        assignments_score: int,
    ) -> RiskScore:
        """Calculate weighted total risk score."""
        total = int(
            attendance_score * self.weights.attendance +
            grades_score * self.weights.grades +
            assignments_score * self.weights.assignments
        )
        return RiskScore(min(100, max(0, total)))
    
    def assess(
        self,
        student_id: int,
        group_id: int,
        attendance_stats: AttendanceStats,
        grade_average: float,
        assignment_stats: AssignmentStats,
    ) -> RiskAssessment:
        """
        Create a complete risk assessment for a student.
        
        Returns a RiskAssessment with calculated scores and factors.
        """
        # Calculate individual factor scores
        attendance_score = self.calculate_attendance_risk(attendance_stats)
        grades_score = self.calculate_grades_risk(grade_average)
        assignments_score = self.calculate_assignments_risk(assignment_stats)
        
        # Calculate weighted total
        total_score = self.calculate_total_score(
            attendance_score, grades_score, assignments_score
        )
        
        # Build factor details
        factor_details = {
            "attendance": {
                "score": attendance_score,
                "attendance_rate": round(attendance_stats.attendance_rate, 1),
                "absences": attendance_stats.absent,
                "total_classes": attendance_stats.total_classes,
            },
            "grades": {
                "score": grades_score,
                "average": round(grade_average, 2),
            },
            "assignments": {
                "score": assignments_score,
                "on_time_rate": round(assignment_stats.on_time_rate, 1),
                "missing": assignment_stats.missing,
                "late": assignment_stats.late,
            },
        }
        
        # Generate recommendation
        recommendation = self.generate_recommendation(
            total_score.level,
            attendance_score,
            grades_score,
            assignments_score,
            attendance_stats,
            grade_average,
            assignment_stats,
        )
        
        return RiskAssessment.create(
            student_id=student_id,
            group_id=group_id,
            attendance_score=attendance_score,
            grades_score=grades_score,
            assignments_score=assignments_score,
            attendance_weight=self.weights.attendance,
            grades_weight=self.weights.grades,
            assignments_weight=self.weights.assignments,
            factor_details=factor_details,
            recommendation=recommendation,
        )
    
    def generate_recommendation(
        self,
        risk_level: RiskLevel,
        attendance_score: int,
        grades_score: int,
        assignments_score: int,
        attendance_stats: AttendanceStats,
        grade_average: float,
        assignment_stats: AssignmentStats,
    ) -> str:
        """Generate actionable recommendations based on risk factors."""
        recommendations = []
        
        # Attendance recommendations
        if attendance_score >= 60:
            recommendations.append(
                f"⚠️ Asistencia crítica ({attendance_stats.attendance_rate:.0f}%). "
                "Se recomienda hablar con el alumno sobre las ausencias."
            )
        elif attendance_score >= 40:
            recommendations.append(
                f"📊 Asistencia por debajo del objetivo ({attendance_stats.attendance_rate:.0f}%). "
                "Monitorear próximas clases."
            )
        
        # Grades recommendations
        if grades_score >= 75:
            recommendations.append(
                f"📉 Promedio reprobatorio ({grade_average:.1f}). "
                "Considerar tutoría o asesoría adicional."
            )
        elif grades_score >= 50:
            recommendations.append(
                f"📊 Promedio en riesgo ({grade_average:.1f}). "
                "Revisar áreas de oportunidad con el alumno."
            )
        
        # Assignments recommendations
        if assignment_stats.missing > 0:
            recommendations.append(
                f"📝 Hay {assignment_stats.missing} tarea(s) sin entregar. "
                "Dar seguimiento a las entregas pendientes."
            )
        if assignment_stats.late > 2:
            recommendations.append(
                "⏰ Patrón de entregas tardías detectado. "
                "Reforzar importancia de puntualidad."
            )
        
        # General recommendations by risk level
        if risk_level == RiskLevel.CRITICAL:
            recommendations.insert(0,
                "🚨 RIESGO CRÍTICO: Se requiere intervención inmediata. "
                "Agendar reunión con coordinación y/o tutores."
            )
        elif risk_level == RiskLevel.HIGH:
            recommendations.insert(0,
                "⚠️ RIESGO ALTO: Monitoreo cercano requerido. "
                "Considerar programa de apoyo académico."
            )
        
        return "\n".join(recommendations) if recommendations else "✅ Sin riesgos detectados."
