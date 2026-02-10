import { apiClient } from './client'

export interface Subject {
    id: number
    code: string
    name: string
    credits: number
    hoursTheory: number
    hoursPractice: number
    hoursLab: number
    totalHours: number
    description?: string
    department?: string
    semesterSuggested?: number
    isActive: boolean
}

export interface SubjectWithPrerequisites extends Subject {
    prerequisites: Subject[]
    requiredBy: Subject[]
}

export interface Group {
    id: number
    subjectId: number
    periodId: number
    professorId?: number
    groupNumber: string
    capacity: number
    enrolledCount: number
    availableSpots: number
    isFull: boolean
    classroom?: string
    modality: string
    isActive: boolean
    schedules: Schedule[]
    subject?: {
        id: number
        code: string
        name: string
        credits: number
    }
}

export interface Schedule {
    id: number
    groupId: number
    dayOfWeek: number
    startTime: string
    endTime: string
    classroom?: string
    scheduleType: string
    dayName: string
    timeRange: string
}

export interface AcademicHistoryItem {
    enrollmentId: number
    subject: {
        id: number
        code: string
        name: string
        credits: number
    }
    period: {
        id: number
        code: string
        name: string
    }
    groupNumber: string
    status: string
    grade?: number
    gradeLetter?: string
    attemptNumber: number
    creditsEarned: number
}

export interface AcademicHistory {
    studentId: number
    totalCreditsAttempted: number
    totalCreditsEarned: number
    gpa: number
    subjectsPassed: number
    subjectsFailed: number
    subjectsInProgress: number
    currentEnrollments: AcademicHistoryItem[]
    history: AcademicHistoryItem[]
}

export interface SimulationResult {
    isValid: boolean
    totalCredits: number
    conflicts: {
        group1Id: number
        group2Id: number
        day: string
        timeOverlap: string
        message: string
    }[]
    prerequisiteIssues: string[]
    warnings: string[]
}

// Transform functions for snake_case to camelCase
function transformSubject(data: any): Subject {
    return {
        id: data.id,
        code: data.code,
        name: data.name,
        credits: data.credits,
        hoursTheory: data.hours_theory,
        hoursPractice: data.hours_practice,
        hoursLab: data.hours_lab,
        totalHours: data.total_hours,
        description: data.description,
        department: data.department,
        semesterSuggested: data.semester_suggested,
        isActive: data.is_active,
    }
}

function transformSchedule(data: any): Schedule {
    return {
        id: data.id,
        groupId: data.group_id,
        dayOfWeek: data.day_of_week,
        startTime: data.start_time,
        endTime: data.end_time,
        classroom: data.classroom,
        scheduleType: data.schedule_type,
        dayName: data.day_name,
        timeRange: data.time_range,
    }
}

function transformGroup(data: any): Group {
    return {
        id: data.id,
        subjectId: data.subject_id,
        periodId: data.period_id,
        professorId: data.professor_id,
        groupNumber: data.group_number,
        capacity: data.capacity,
        enrolledCount: data.enrolled_count,
        availableSpots: data.available_spots,
        isFull: data.is_full,
        classroom: data.classroom,
        modality: data.modality,
        isActive: data.is_active,
        schedules: data.schedules?.map(transformSchedule) || [],
        subject: data.subject,
    }
}

export const planningApi = {
    // Subjects
    getSubjects: async (params?: {
        department?: string
        semester?: number
        offset?: number
        limit?: number
    }): Promise<Subject[]> => {
        const response = await apiClient.get('/subjects', { params })
        return response.data.map(transformSubject)
    },

    searchSubjects: async (query: string): Promise<Subject[]> => {
        const response = await apiClient.get('/subjects/search', { params: { q: query } })
        return response.data.map(transformSubject)
    },

    getSubject: async (id: number): Promise<SubjectWithPrerequisites> => {
        const response = await apiClient.get(`/subjects/${id}`)
        const data = response.data
        return {
            ...transformSubject(data),
            prerequisites: data.prerequisites?.map(transformSubject) || [],
            requiredBy: data.required_by?.map(transformSubject) || [],
        }
    },

    getDepartments: async (): Promise<string[]> => {
        const response = await apiClient.get('/subjects/departments')
        return response.data
    },

    // Groups
    getGroups: async (params?: {
        periodId?: number
        subjectId?: number
    }): Promise<Group[]> => {
        const response = await apiClient.get('/groups', {
            params: {
                period_id: params?.periodId,
                subject_id: params?.subjectId,
            },
        })
        return response.data.map(transformGroup)
    },

    getAvailableGroups: async (periodId?: number): Promise<Group[]> => {
        const response = await apiClient.get('/groups/available', {
            params: { period_id: periodId },
        })
        return response.data.map(transformGroup)
    },

    getGroup: async (id: number): Promise<Group> => {
        const response = await apiClient.get(`/groups/${id}`)
        return transformGroup(response.data)
    },

    // Enrollments
    getCurrentEnrollments: async () => {
        const response = await apiClient.get('/enrollments/current')
        return response.data
    },

    getAcademicHistory: async (): Promise<AcademicHistory> => {
        const response = await apiClient.get('/enrollments/history')
        const data = response.data
        return {
            studentId: data.student_id,
            totalCreditsAttempted: data.total_credits_attempted,
            totalCreditsEarned: data.total_credits_earned,
            gpa: data.gpa,
            subjectsPassed: data.subjects_passed,
            subjectsFailed: data.subjects_failed,
            subjectsInProgress: data.subjects_in_progress,
            currentEnrollments: data.current_enrollments,
            history: data.history,
        }
    },

    enroll: async (groupId: number) => {
        const response = await apiClient.post('/enrollments', { group_id: groupId })
        return response.data
    },

    dropEnrollment: async (enrollmentId: number) => {
        await apiClient.delete(`/enrollments/${enrollmentId}`)
    },

    simulate: async (groupIds: number[]): Promise<SimulationResult> => {
        const response = await apiClient.post('/enrollments/simulate', {
            group_ids: groupIds,
        })
        const data = response.data
        return {
            isValid: data.is_valid,
            totalCredits: data.total_credits,
            conflicts: data.conflicts,
            prerequisiteIssues: data.prerequisite_issues,
            warnings: data.warnings,
        }
    },
}
