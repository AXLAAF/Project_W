"""
Schedule conflict detector domain service.
Pure domain logic for detecting schedule conflicts.
"""
from typing import List, Tuple

from app.domain.entities.planning.group import Group, Schedule


class ScheduleConflictDetector:
    """
    Domain service for detecting schedule conflicts.
    
    This is pure domain logic - no infrastructure dependencies.
    """
    
    def detect_conflicts(
        self,
        groups: List[Group],
    ) -> List[Tuple[Group, Group, Schedule, Schedule]]:
        """
        Detect all schedule conflicts between groups.
        
        Args:
            groups: List of groups to check for conflicts
        
        Returns:
            List of tuples: (group1, group2, conflicting_schedule1, conflicting_schedule2)
        """
        conflicts = []
        
        for i, group1 in enumerate(groups):
            for group2 in groups[i + 1:]:
                for schedule1 in group1.schedules:
                    for schedule2 in group2.schedules:
                        if schedule1.overlaps_with(schedule2):
                            conflicts.append((group1, group2, schedule1, schedule2))
        
        return conflicts
    
    def has_conflict(
        self,
        new_group: Group,
        existing_groups: List[Group],
    ) -> bool:
        """
        Check if a new group has any conflicts with existing groups.
        
        Args:
            new_group: The group to check
            existing_groups: Currently enrolled groups
        
        Returns:
            True if there's a conflict, False otherwise
        """
        for existing in existing_groups:
            if new_group.has_schedule_conflict(existing.schedules):
                return True
        return False
    
    def get_conflict_details(
        self,
        new_group: Group,
        existing_groups: List[Group],
    ) -> List[dict]:
        """
        Get detailed conflict information.
        
        Returns:
            List of conflict dictionaries with group and schedule details
        """
        conflicts = []
        
        for existing in existing_groups:
            for new_schedule in new_group.schedules:
                for existing_schedule in existing.schedules:
                    if new_schedule.overlaps_with(existing_schedule):
                        conflicts.append({
                            "new_group_id": new_group.id,
                            "new_subject": new_group.subject_code,
                            "new_day": new_schedule.day_of_week.value,
                            "new_time": f"{new_schedule.start_time}-{new_schedule.end_time}",
                            "conflict_group_id": existing.id,
                            "conflict_subject": existing.subject_code,
                            "conflict_day": existing_schedule.day_of_week.value,
                            "conflict_time": f"{existing_schedule.start_time}-{existing_schedule.end_time}",
                        })
        
        return conflicts
    
    def find_compatible_groups(
        self,
        available_groups: List[Group],
        enrolled_groups: List[Group],
    ) -> List[Group]:
        """
        Find groups that don't conflict with already enrolled groups.
        
        Args:
            available_groups: Groups to filter
            enrolled_groups: Currently enrolled groups
        
        Returns:
            List of groups without schedule conflicts
        """
        compatible = []
        
        for group in available_groups:
            if not self.has_conflict(group, enrolled_groups):
                compatible.append(group)
        
        return compatible
