"""
Mappers for converting between Planning domain entities and SQLAlchemy models.
"""
from datetime import time
from typing import List

from app.domain.entities.planning.subject import Subject as SubjectEntity, Prerequisite as SubjectPrerequisiteEntity
from app.domain.entities.planning.group import Group as GroupEntity, Schedule as ScheduleEntity, DayOfWeek
from app.domain.entities.planning.enrollment import Enrollment as EnrollmentEntity, EnrollmentStatus as DomainEnrollmentStatus
from app.domain.value_objects.planning import SubjectCode, Credits, Grade

# Import ORM models
from app.planning.models.subject import Subject as SubjectModel, SubjectPrerequisite as SubjectPrerequisiteModel
from app.planning.models.group import Group as GroupModel, Schedule as ScheduleModel, DayOfWeek as ORMDayOfWeek
from app.planning.models.enrollment import Enrollment as EnrollmentModel, EnrollmentStatus as ORMEnrollmentStatus

from decimal import Decimal


class SubjectPrerequisiteMapper:
    """Mapper for SubjectPrerequisite entity <-> SubjectPrerequisiteModel."""
    
    @staticmethod
    def to_entity(model: SubjectPrerequisiteModel) -> SubjectPrerequisiteEntity:
        """Convert ORM model to domain entity."""
        return SubjectPrerequisiteEntity(
            prerequisite_subject_id=model.prerequisite_id,
            prerequisite_code=model.prerequisite.code if model.prerequisite else "",
            prerequisite_name=model.prerequisite.name if model.prerequisite else "",
            is_mandatory=model.is_mandatory,
        )


class SubjectMapper:
    """Mapper for Subject entity <-> SubjectModel."""
    
    @staticmethod
    def to_entity(model: SubjectModel) -> SubjectEntity:
        """Convert ORM model to domain entity."""
        prerequisites: List[SubjectPrerequisiteEntity] = []
        if model.prerequisites:
            prerequisites = [
                SubjectPrerequisiteMapper.to_entity(p)
                for p in model.prerequisites
            ]
        
        return SubjectEntity(
            id=model.id,
            code=SubjectCode(model.code),
            name=model.name,
            credits=Credits(model.credits),
            hours_theory=model.hours_theory,
            hours_practice=model.hours_practice,
            hours_lab=model.hours_lab,
            description=model.description,
            department=model.department,
            semester_suggested=model.semester_suggested,
            is_active=model.is_active,
            prerequisites=prerequisites,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: SubjectEntity) -> SubjectModel:
        """Convert domain entity to ORM model."""
        model = SubjectModel(
            code=entity.code_str,
            name=entity.name,
            credits=entity.credits_value,
            hours_theory=entity.hours_theory,
            hours_practice=entity.hours_practice,
            hours_lab=entity.hours_lab,
            description=entity.description,
            department=entity.department,
            semester_suggested=entity.semester_suggested,
            is_active=entity.is_active,
        )
        if entity.id:
            model.id = entity.id
        return model
    
    @staticmethod
    def update_model(model: SubjectModel, entity: SubjectEntity) -> None:
        """Update ORM model from domain entity."""
        model.code = entity.code_str
        model.name = entity.name
        model.credits = entity.credits_value
        model.hours_theory = entity.hours_theory
        model.hours_practice = entity.hours_practice
        model.hours_lab = entity.hours_lab
        model.description = entity.description
        model.department = entity.department
        model.semester_suggested = entity.semester_suggested
        model.is_active = entity.is_active


class ScheduleMapper:
    """Mapper for Schedule entity <-> ScheduleModel."""
    
    @staticmethod
    def _orm_day_to_domain(orm_day: int) -> DayOfWeek:
        """Convert ORM day of week (1-7) to domain DayOfWeek enum."""
        mapping = {
            1: DayOfWeek.MONDAY,
            2: DayOfWeek.TUESDAY,
            3: DayOfWeek.WEDNESDAY,
            4: DayOfWeek.THURSDAY,
            5: DayOfWeek.FRIDAY,
            6: DayOfWeek.SATURDAY,
            7: DayOfWeek.SUNDAY,
        }
        return mapping.get(orm_day, DayOfWeek.MONDAY)
    
    @staticmethod
    def _domain_day_to_orm(day: DayOfWeek) -> int:
        """Convert domain DayOfWeek to ORM day of week (1-7)."""
        mapping = {
            DayOfWeek.MONDAY: 1,
            DayOfWeek.TUESDAY: 2,
            DayOfWeek.WEDNESDAY: 3,
            DayOfWeek.THURSDAY: 4,
            DayOfWeek.FRIDAY: 5,
            DayOfWeek.SATURDAY: 6,
            DayOfWeek.SUNDAY: 7,
        }
        return mapping.get(day, 1)
    
    @staticmethod
    def to_entity(model: ScheduleModel) -> ScheduleEntity:
        """Convert ORM model to domain entity."""
        return ScheduleEntity(
            day_of_week=ScheduleMapper._orm_day_to_domain(model.day_of_week),
            start_time=model.start_time,
            end_time=model.end_time,
            classroom=model.classroom,
            schedule_type=getattr(model, 'schedule_type', 'class'),
            id=model.id,
            group_id=model.group_id,
        )
    
    @staticmethod
    def to_model(entity: ScheduleEntity, group_id: int) -> ScheduleModel:
        """Convert domain entity to ORM model."""
        return ScheduleModel(
            group_id=group_id,
            day_of_week=ScheduleMapper._domain_day_to_orm(entity.day_of_week),
            start_time=entity.start_time,
            end_time=entity.end_time,
            classroom=entity.classroom,
            schedule_type=entity.schedule_type,
        )


class GroupMapper:
    """Mapper for Group entity <-> GroupModel."""
    
    @staticmethod
    def to_entity(model: GroupModel) -> GroupEntity:
        """Convert ORM model to domain entity."""
        schedules: List[ScheduleEntity] = []
        if model.schedules:
            schedules = [ScheduleMapper.to_entity(s) for s in model.schedules]
        
        professor_name = None
        if model.professor and model.professor.profile:
            professor_name = f"{model.professor.profile.first_name} {model.professor.profile.last_name}"
        
        return GroupEntity(
            id=model.id,
            subject_id=model.subject_id,
            period_id=model.period_id,
            group_number=model.group_number,
            professor_id=model.professor_id,
            professor_name=professor_name,
            capacity=model.capacity,
            enrolled_count=model.enrolled_count,
            subject_code=model.subject.code if model.subject else None,
            subject_name=model.subject.name if model.subject else None,
            classroom=model.classroom,
            modality=getattr(model, 'modality', 'presencial'),
            is_active=model.is_active,
            schedules=schedules,
            created_at=model.created_at,
        )
    
    @staticmethod
    def to_model(entity: GroupEntity) -> GroupModel:
        """Convert domain entity to ORM model."""
        model = GroupModel(
            subject_id=entity.subject_id,
            period_id=entity.period_id,
            group_number=entity.group_number,
            professor_id=entity.professor_id,
            capacity=entity.capacity,
            enrolled_count=entity.enrolled_count,
            classroom=entity.classroom,
            modality=entity.modality,
            is_active=entity.is_active,
        )
        if entity.id:
            model.id = entity.id
        return model
    
    @staticmethod
    def update_model(model: GroupModel, entity: GroupEntity) -> None:
        """Update ORM model from domain entity."""
        model.subject_id = entity.subject_id
        model.period_id = entity.period_id
        model.group_number = entity.group_number
        model.professor_id = entity.professor_id
        model.capacity = entity.capacity
        model.enrolled_count = entity.enrolled_count
        model.classroom = entity.classroom
        model.modality = entity.modality
        model.is_active = entity.is_active


class EnrollmentMapper:
    """Mapper for Enrollment entity <-> EnrollmentModel."""
    
    @staticmethod
    def _orm_status_to_domain(status: str) -> DomainEnrollmentStatus:
        """Convert ORM status string to domain enum."""
        mapping = {
            ORMEnrollmentStatus.ENROLLED.value: DomainEnrollmentStatus.ENROLLED,
            ORMEnrollmentStatus.PASSED.value: DomainEnrollmentStatus.PASSED,
            ORMEnrollmentStatus.FAILED.value: DomainEnrollmentStatus.FAILED,
            ORMEnrollmentStatus.DROPPED.value: DomainEnrollmentStatus.DROPPED,
            ORMEnrollmentStatus.WITHDRAWN.value: DomainEnrollmentStatus.WITHDRAWN,
            ORMEnrollmentStatus.PENDING.value: DomainEnrollmentStatus.PENDING,
        }
        return mapping.get(status, DomainEnrollmentStatus.ENROLLED)
    
    @staticmethod
    def _domain_status_to_orm(status: DomainEnrollmentStatus) -> str:
        """Convert domain status to ORM status string."""
        return status.value
    
    @staticmethod
    def to_entity(model: EnrollmentModel) -> EnrollmentEntity:
        """Convert ORM model to domain entity."""
        grade = None
        if model.grade is not None:
            grade = Grade(model.grade)
        
        subject_code = None
        subject_name = None
        if model.group and model.group.subject:
            subject_code = model.group.subject.code
            subject_name = model.group.subject.name
        
        return EnrollmentEntity(
            id=model.id,
            student_id=model.student_id,
            group_id=model.group_id,
            subject_code=subject_code,
            subject_name=subject_name,
            status=EnrollmentMapper._orm_status_to_domain(model.status),
            grade=grade,
            attempt_number=model.attempt_number,
            enrolled_at=model.enrolled_at,
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
    
    @staticmethod
    def to_model(entity: EnrollmentEntity) -> EnrollmentModel:
        """Convert domain entity to ORM model."""
        grade_value = None
        grade_letter = None
        if entity.grade:
            grade_value = entity.grade.value
            grade_letter = entity.grade.letter
        
        model = EnrollmentModel(
            student_id=entity.student_id,
            group_id=entity.group_id,
            status=EnrollmentMapper._domain_status_to_orm(entity.status),
            grade=grade_value,
            grade_letter=grade_letter,
            attempt_number=entity.attempt_number,
            enrolled_at=entity.enrolled_at,
            completed_at=entity.completed_at,
        )
        if entity.id:
            model.id = entity.id
        return model
    
    @staticmethod
    def update_model(model: EnrollmentModel, entity: EnrollmentEntity) -> None:
        """Update ORM model from domain entity."""
        model.status = EnrollmentMapper._domain_status_to_orm(entity.status)
        if entity.grade:
            model.grade = entity.grade.value
            model.grade_letter = entity.grade.letter
        model.attempt_number = entity.attempt_number
        model.completed_at = entity.completed_at
