"""
Risk Calculator Service.
Calculates academic risk scores based on multiple factors.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.risk.models.risk_assessment import RiskAssessment, RiskLevel, RiskFactor
from app.risk.repositories.risk_repository import RiskRepository


class RiskCalculatorService:
    """
    Service for calculating and assessing academic risk.
    
    Risk Score Formula:
    - Attendance factor (30% weight): Based on absence rate
    - Grades factor (40% weight): Based on grade average
    - Assignments factor (30% weight): Based on missing/late submissions
    
    Score ranges:
    - 0-30: LOW risk (green)
    - 31-60: MEDIUM risk (yellow)
    - 61-80: HIGH risk (orange)
    - 81-100: CRITICAL risk (red)
    """

    # Weights for each factor
    ATTENDANCE_WEIGHT = 0.30
    GRADES_WEIGHT = 0.40
    ASSIGNMENTS_WEIGHT = 0.30

    # Thresholds for risk calculation
    ATTENDANCE_CRITICAL_THRESHOLD = 70  # Below 70% attendance = critical
    GRADES_FAILING_THRESHOLD = 6.0      # Below 6 = failing
    ASSIGNMENTS_MISSING_THRESHOLD = 30  # More than 30% missing = critical

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = RiskRepository(session)

    async def calculate_risk(
        self, student_id: int, group_id: int
    ) -> RiskAssessment:
        """
        Calculate comprehensive risk score for a student in a course.
        
        Returns a RiskAssessment with detailed factor breakdown.
        """
        # Get statistics from each factor
        attendance_stats = await self.repo.get_attendance_stats(student_id, group_id)
        grade_average = await self.repo.get_grade_average(student_id, group_id)
        assignment_stats = await self.repo.get_assignment_stats(student_id, group_id)

        # Calculate individual factor scores (0-100, higher = more risk)
        attendance_score = self._calculate_attendance_risk(attendance_stats)
        grades_score = self._calculate_grades_risk(grade_average)
        assignments_score = self._calculate_assignments_risk(assignment_stats)

        # Calculate weighted total
        total_score = int(
            attendance_score * self.ATTENDANCE_WEIGHT +
            grades_score * self.GRADES_WEIGHT +
            assignments_score * self.ASSIGNMENTS_WEIGHT
        )

        # Determine risk level
        risk_level = RiskAssessment.calculate_risk_level(total_score)

        # Generate recommendation
        recommendation = self._generate_recommendation(
            risk_level,
            attendance_score,
            grades_score,
            assignments_score,
            attendance_stats,
            grade_average,
            assignment_stats,
        )

        # Create assessment
        assessment = RiskAssessment(
            student_id=student_id,
            group_id=group_id,
            risk_score=total_score,
            risk_level=risk_level.value,
            attendance_score=attendance_score,
            grades_score=grades_score,
            assignments_score=assignments_score,
            factor_details={
                "attendance": {
                    "score": attendance_score,
                    "attendance_rate": attendance_stats["attendance_rate"],
                    "absences": attendance_stats["absent"],
                    "total_classes": attendance_stats["total_classes"],
                },
                "grades": {
                    "score": grades_score,
                    "average": round(grade_average, 2),
                },
                "assignments": {
                    "score": assignments_score,
                    "on_time_rate": assignment_stats["on_time_rate"],
                    "missing": assignment_stats["missing"],
                    "late": assignment_stats["late"],
                },
            },
            recommendation=recommendation,
            assessed_at=datetime.now(datetime.now().astimezone().tzinfo),
        )

        # Save assessment
        await self.repo.save_assessment(assessment)
        
        return assessment

    def _calculate_attendance_risk(self, stats: dict) -> int:
        """
        Calculate risk score from attendance.
        Lower attendance = higher risk score.
        """
        attendance_rate = stats["attendance_rate"]
        
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
        elif attendance_rate >= 70:
            return 75
        else:
            return 100

    def _calculate_grades_risk(self, average: float) -> int:
        """
        Calculate risk score from grade average.
        Lower grades = higher risk score.
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
        elif average >= 6.0:
            return 55
        elif average >= 5.0:
            return 75
        else:
            return 100

    def _calculate_assignments_risk(self, stats: dict) -> int:
        """
        Calculate risk score from assignment submissions.
        More missing/late = higher risk score.
        """
        total = stats["total_assignments"]
        if total == 0:
            return 0  # No assignments yet
        
        on_time_rate = stats["on_time_rate"]
        missing_rate = (stats["missing"] / total) * 100
        
        # Combined score based on missing and late
        if missing_rate > 50:
            return 100
        elif missing_rate > 30:
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

    def _generate_recommendation(
        self,
        risk_level: RiskLevel,
        attendance_score: int,
        grades_score: int,
        assignments_score: int,
        attendance_stats: dict,
        grade_average: float,
        assignment_stats: dict,
    ) -> str:
        """Generate actionable recommendations based on risk factors."""
        recommendations = []

        # Attendance recommendations
        if attendance_score >= 60:
            recommendations.append(
                f"⚠️ Asistencia crítica ({attendance_stats['attendance_rate']:.0f}%). "
                "Se recomienda hablar con el alumno sobre las ausencias."
            )
        elif attendance_score >= 40:
            recommendations.append(
                f"📊 Asistencia por debajo del objetivo ({attendance_stats['attendance_rate']:.0f}%). "
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
        if assignment_stats["missing"] > 0:
            recommendations.append(
                f"📝 Hay {assignment_stats['missing']} tarea(s) sin entregar. "
                "Dar seguimiento a las entregas pendientes."
            )
        if assignment_stats["late"] > 2:
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

    async def get_student_risk_summary(
        self, student_id: int, group_id: int
    ) -> dict:
        """Get a summary of the student's current risk status."""
        assessment = await self.repo.get_latest_assessment(student_id, group_id)
        
        if not assessment:
            # Calculate new assessment if none exists
            assessment = await self.calculate_risk(student_id, group_id)

        history = await self.repo.get_risk_history(student_id, group_id)
        
        # Calculate trend
        trend = "stable"
        if len(history) >= 2:
            recent_scores = [a.risk_score for a in history[-3:]]
            if all(s > recent_scores[0] for s in recent_scores[1:]):
                trend = "increasing"
            elif all(s < recent_scores[0] for s in recent_scores[1:]):
                trend = "decreasing"

        return {
            "current_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "is_at_risk": assessment.is_at_risk,
            "trend": trend,
            "factors": assessment.factor_details,
            "recommendation": assessment.recommendation,
            "last_assessed": assessment.assessed_at.isoformat(),
        }

    async def get_group_risk_dashboard(self, group_id: int) -> dict:
        """Get risk dashboard for a group (for professors/coordinators)."""
        at_risk = await self.repo.get_at_risk_students(group_id, RiskLevel.MEDIUM)
        
        # Categorize by risk level
        critical = [a for a in at_risk if a.risk_level == RiskLevel.CRITICAL.value]
        high = [a for a in at_risk if a.risk_level == RiskLevel.HIGH.value]
        medium = [a for a in at_risk if a.risk_level == RiskLevel.MEDIUM.value]

        return {
            "total_at_risk": len(at_risk),
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
            "critical_students": [
                {
                    "student_id": a.student_id,
                    "student_name": f"{a.student.profile.first_name} {a.student.profile.last_name}" if a.student.profile else a.student.email,
                    "risk_score": a.risk_score,
                    "main_factor": self._get_main_risk_factor(a),
                }
                for a in critical[:10]
            ],
            "high_students": [
                {
                    "student_id": a.student_id,
                    "student_name": f"{a.student.profile.first_name} {a.student.profile.last_name}" if a.student.profile else a.student.email,
                    "risk_score": a.risk_score,
                }
                for a in high[:10]
            ],
        }

    def _get_main_risk_factor(self, assessment: RiskAssessment) -> str:
        """Determine the main contributing factor to risk."""
        factors = [
            (RiskFactor.ATTENDANCE.value, assessment.attendance_score),
            (RiskFactor.GRADES.value, assessment.grades_score),
            (RiskFactor.ASSIGNMENTS.value, assessment.assignments_score),
        ]
        return max(factors, key=lambda x: x[1])[0]
