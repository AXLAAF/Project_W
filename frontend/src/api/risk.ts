import { apiClient } from './client'

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface RiskFactors {
    attendance?: {
        score: number
        attendance_rate: number
        absences: number
        total_classes: number
    }
    grades?: {
        score: number
        average: number
    }
    assignments?: {
        score: number
        on_time_rate: number
        missing: number
        late: number
    }
}

export interface StudentRiskSummary {
    currentScore: number
    riskLevel: RiskLevel
    isAtRisk: boolean
    trend: 'stable' | 'increasing' | 'decreasing'
    factors: RiskFactors | null
    recommendation: string | null
    lastAssessed: string
}

export interface AtRiskStudent {
    studentId: number
    studentName: string
    riskScore: number
    mainFactor?: string
}

export interface GroupRiskDashboard {
    totalAtRisk: number
    criticalCount: number
    highCount: number
    mediumCount: number
    criticalStudents: AtRiskStudent[]
    highStudents: AtRiskStudent[]
}

export interface AttendanceStats {
    totalClasses: number
    present: number
    absent: number
    late: number
    excused: number
    attendanceRate: number
}

// Transform functions
function transformRiskSummary(data: any): StudentRiskSummary {
    return {
        currentScore: data.current_score,
        riskLevel: data.risk_level,
        isAtRisk: data.is_at_risk,
        trend: data.trend,
        factors: data.factors,
        recommendation: data.recommendation,
        lastAssessed: data.last_assessed,
    }
}

function transformDashboard(data: any): GroupRiskDashboard {
    return {
        totalAtRisk: data.total_at_risk,
        criticalCount: data.critical_count,
        highCount: data.high_count,
        mediumCount: data.medium_count,
        criticalStudents: data.critical_students?.map((s: any) => ({
            studentId: s.student_id,
            studentName: s.student_name,
            riskScore: s.risk_score,
            mainFactor: s.main_factor,
        })) || [],
        highStudents: data.high_students?.map((s: any) => ({
            studentId: s.student_id,
            studentName: s.student_name,
            riskScore: s.risk_score,
        })) || [],
    }
}

export const riskApi = {
    getMyRisk: async (groupId: number): Promise<StudentRiskSummary> => {
        const response = await apiClient.get(`/risk/my-risk/${groupId}`)
        return transformRiskSummary(response.data)
    },

    getStudentRisk: async (studentId: number, groupId: number): Promise<StudentRiskSummary> => {
        const response = await apiClient.get(`/risk/student/${studentId}/group/${groupId}`)
        return transformRiskSummary(response.data)
    },

    calculateRisk: async (studentId: number, groupId: number) => {
        const response = await apiClient.post(`/risk/calculate/${studentId}/group/${groupId}`)
        return response.data
    },

    getGroupDashboard: async (groupId: number): Promise<GroupRiskDashboard> => {
        const response = await apiClient.get(`/risk/dashboard/${groupId}`)
        return transformDashboard(response.data)
    },

    getAttendanceStats: async (studentId: number, groupId: number): Promise<AttendanceStats> => {
        const response = await apiClient.get(`/risk/attendance/${studentId}/group/${groupId}`)
        const data = response.data
        return {
            totalClasses: data.total_classes,
            present: data.present,
            absent: data.absent,
            late: data.late,
            excused: data.excused,
            attendanceRate: data.attendance_rate,
        }
    },

    recordAttendance: async (data: {
        studentId: number
        groupId: number
        classDate: string
        status: string
        notes?: string
    }) => {
        await apiClient.post('/risk/attendance', {
            student_id: data.studentId,
            group_id: data.groupId,
            class_date: data.classDate,
            status: data.status,
            notes: data.notes,
        })
    },

    recordGrade: async (data: {
        studentId: number
        groupId: number
        gradeType: string
        name: string
        grade: number
        maxGrade?: number
        weight?: number
        feedback?: string
    }) => {
        await apiClient.post('/risk/grade', {
            student_id: data.studentId,
            group_id: data.groupId,
            grade_type: data.gradeType,
            name: data.name,
            grade: data.grade,
            max_grade: data.maxGrade,
            weight: data.weight,
            feedback: data.feedback,
        })
    },

    getAtRiskStudents: async (groupId: number) => {
        const response = await apiClient.get(`/risk/at-risk-students/${groupId}`)
        return response.data
    },
}
