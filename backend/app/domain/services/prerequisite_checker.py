"""
Prerequisite checker domain service.
Pure domain logic for validating subject prerequisites.
"""
from typing import List, Set

from app.domain.entities.planning.subject import Subject
from app.domain.entities.planning.enrollment import Enrollment, EnrollmentStatus


class PrerequisiteChecker:
    """
    Domain service for checking prerequisite requirements.
    
    This is pure domain logic - no infrastructure dependencies.
    """
    
    def check_prerequisites(
        self,
        target_subject: Subject,
        completed_subjects: List[Enrollment],
    ) -> tuple[bool, List[str]]:
        """
        Check if a student has completed all prerequisites for a subject.
        
        Args:
            target_subject: The subject the student wants to enroll in
            completed_subjects: List of enrollments the student has completed
        
        Returns:
            Tuple of (can_enroll: bool, missing_prerequisites: list of codes)
        """
        # Get codes of passed subjects
        passed_codes: Set[str] = set()
        for enrollment in completed_subjects:
            if enrollment.status == EnrollmentStatus.PASSED and enrollment.subject_code:
                passed_codes.add(enrollment.subject_code)
        
        # Check mandatory prerequisites
        missing = []
        for prereq in target_subject.prerequisites:
            if prereq.is_mandatory and prereq.prerequisite_code not in passed_codes:
                missing.append(prereq.prerequisite_code)
        
        return len(missing) == 0, missing
    
    def get_available_subjects(
        self,
        all_subjects: List[Subject],
        completed_enrollments: List[Enrollment],
        in_progress_subject_ids: Set[int],
    ) -> List[Subject]:
        """
        Get list of subjects available for enrollment.
        
        Filters out:
        - Already passed subjects
        - Currently enrolled subjects
        - Subjects with unmet prerequisites
        
        Args:
            all_subjects: All subjects in the curriculum
            completed_enrollments: Student's enrollment history
            in_progress_subject_ids: IDs of subjects currently being taken
        
        Returns:
            List of subjects available for enrollment
        """
        # Get passed subjects
        passed_subject_codes = {
            e.subject_code
            for e in completed_enrollments
            if e.status == EnrollmentStatus.PASSED and e.subject_code
        }
        
        available = []
        for subject in all_subjects:
            # Skip if already passed
            if subject.code_str in passed_subject_codes:
                continue
            
            # Skip if currently enrolled
            if subject.id in in_progress_subject_ids:
                continue
            
            # Skip if inactive
            if not subject.is_active:
                continue
            
            # Check prerequisites
            can_enroll, _ = self.check_prerequisites(subject, completed_enrollments)
            if can_enroll:
                available.append(subject)
        
        return available
    
    def validate_enrollment(
        self,
        subject: Subject,
        student_enrollments: List[Enrollment],
        max_attempts: int = 3,
    ) -> tuple[bool, str]:
        """
        Validate if a student can enroll in a subject.
        
        Checks:
        - Prerequisites met
        - Not already enrolled
        - Not exceeded max attempts
        
        Returns:
            Tuple of (can_enroll: bool, reason: str if denied)
        """
        # Check if already passed
        passed = [
            e for e in student_enrollments
            if e.subject_code == subject.code_str and e.status == EnrollmentStatus.PASSED
        ]
        if passed:
            return False, "Subject already passed"
        
        # Check if currently enrolled
        current = [
            e for e in student_enrollments
            if e.subject_code == subject.code_str and e.status == EnrollmentStatus.ENROLLED
        ]
        if current:
            return False, "Already enrolled in this subject"
        
        # Check attempt count
        attempts = len([
            e for e in student_enrollments
            if e.subject_code == subject.code_str
        ])
        if attempts >= max_attempts:
            return False, f"Maximum attempts ({max_attempts}) exceeded"
        
        # Check prerequisites
        can_enroll, missing = self.check_prerequisites(subject, student_enrollments)
        if not can_enroll:
            return False, f"Missing prerequisites: {', '.join(missing)}"
        
        return True, ""
