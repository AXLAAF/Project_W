import { apiClient } from './client'

// Types
export interface Company {
    id: number
    name: string
    rfc: string
    contactEmail: string
    contactPhone?: string
    address?: string
    description?: string
    website?: string
    logoUrl?: string
    isVerified: boolean
    isActive: boolean
    createdAt: string
    updatedAt: string
}

export interface Position {
    id: number
    companyId: number
    title: string
    description: string
    requirements?: string
    benefits?: string
    durationMonths: number
    modality: 'PRESENCIAL' | 'REMOTO' | 'HIBRIDO'
    location?: string
    minGpa?: number
    minCredits?: number
    capacity: number
    filledCount: number
    isActive: boolean
    createdAt: string
    updatedAt: string
    company?: CompanySummary
}

export interface CompanySummary {
    id: number
    name: string
    logoUrl?: string
    isVerified: boolean
}

export interface Application {
    id: number
    userId: number
    positionId: number
    status: 'PENDING' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED' | 'CANCELLED'
    cvPath?: string
    coverLetter?: string
    additionalDocuments?: Record<string, any>
    appliedAt: string
    reviewedAt?: string
    reviewerId?: number
    reviewerNotes?: string
    position?: PositionSummary
    user?: UserSummary
}

export interface PositionSummary {
    id: number
    title: string
    companyId: number
}

export interface UserSummary {
    id: number
    email: string
}

export interface Internship {
    id: number
    applicationId: number
    startDate: string
    expectedEndDate: string
    actualEndDate?: string
    status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED' | 'ON_HOLD'
    supervisorName: string
    supervisorEmail: string
    supervisorPhone?: string
    totalHours: number
    finalGrade?: number
    completionCertificatePath?: string
    createdAt: string
    updatedAt: string
    reports?: ReportSummary[]
}

export interface ReportSummary {
    id: number
    monthNumber: number
    status: string
    hoursWorked: number
}

export interface Report {
    id: number
    internshipId: number
    monthNumber: number
    reportDate: string
    filePath?: string
    hoursWorked: number
    activitiesSummary?: string
    achievements?: string
    challenges?: string
    supervisorComments?: string
    supervisorGrade?: number
    status: 'DRAFT' | 'SUBMITTED' | 'APPROVED' | 'REVISION_NEEDED'
    submittedAt?: string
    reviewedAt?: string
    createdAt: string
    updatedAt: string
}

// Transform functions
function transformCompany(data: any): Company {
    return {
        id: data.id,
        name: data.name,
        rfc: data.rfc,
        contactEmail: data.contact_email,
        contactPhone: data.contact_phone,
        address: data.address,
        description: data.description,
        website: data.website,
        logoUrl: data.logo_url,
        isVerified: data.is_verified,
        isActive: data.is_active,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
    }
}

function transformPosition(data: any): Position {
    return {
        id: data.id,
        companyId: data.company_id,
        title: data.title,
        description: data.description,
        requirements: data.requirements,
        benefits: data.benefits,
        durationMonths: data.duration_months,
        modality: data.modality,
        location: data.location,
        minGpa: data.min_gpa,
        minCredits: data.min_credits,
        capacity: data.capacity,
        filledCount: data.filled_count,
        isActive: data.is_active,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
        company: data.company ? {
            id: data.company.id,
            name: data.company.name,
            logoUrl: data.company.logo_url,
            isVerified: data.company.is_verified,
        } : undefined,
    }
}

function transformApplication(data: any): Application {
    return {
        id: data.id,
        userId: data.user_id,
        positionId: data.position_id,
        status: data.status,
        cvPath: data.cv_path,
        coverLetter: data.cover_letter,
        additionalDocuments: data.additional_documents,
        appliedAt: data.applied_at,
        reviewedAt: data.reviewed_at,
        reviewerId: data.reviewer_id,
        reviewerNotes: data.reviewer_notes,
        position: data.position,
        user: data.user,
    }
}

function transformInternship(data: any): Internship {
    return {
        id: data.id,
        applicationId: data.application_id,
        startDate: data.start_date,
        expectedEndDate: data.expected_end_date,
        actualEndDate: data.actual_end_date,
        status: data.status,
        supervisorName: data.supervisor_name,
        supervisorEmail: data.supervisor_email,
        supervisorPhone: data.supervisor_phone,
        totalHours: data.total_hours,
        finalGrade: data.final_grade,
        completionCertificatePath: data.completion_certificate_path,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
        reports: data.reports?.map((r: any) => ({
            id: r.id,
            monthNumber: r.month_number,
            status: r.status,
            hoursWorked: r.hours_worked,
        })),
    }
}

function transformReport(data: any): Report {
    return {
        id: data.id,
        internshipId: data.internship_id,
        monthNumber: data.month_number,
        reportDate: data.report_date,
        filePath: data.file_path,
        hoursWorked: data.hours_worked,
        activitiesSummary: data.activities_summary,
        achievements: data.achievements,
        challenges: data.challenges,
        supervisorComments: data.supervisor_comments,
        supervisorGrade: data.supervisor_grade,
        status: data.status,
        submittedAt: data.submitted_at,
        reviewedAt: data.reviewed_at,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
    }
}

export const internshipsApi = {
    // Companies
    getCompanies: async (params?: {
        isVerified?: boolean
        search?: string
        offset?: number
        limit?: number
    }): Promise<Company[]> => {
        const response = await apiClient.get('/companies', {
            params: {
                is_verified: params?.isVerified,
                search: params?.search,
                offset: params?.offset,
                limit: params?.limit,
            },
        })
        return response.data.map(transformCompany)
    },

    getCompany: async (id: number): Promise<Company> => {
        const response = await apiClient.get(`/companies/${id}`)
        return transformCompany(response.data)
    },

    createCompany: async (data: {
        name: string
        rfc: string
        contactEmail: string
        contactPhone?: string
        address?: string
        description?: string
        website?: string
    }): Promise<Company> => {
        const response = await apiClient.post('/companies', {
            name: data.name,
            rfc: data.rfc,
            contact_email: data.contactEmail,
            contact_phone: data.contactPhone,
            address: data.address,
            description: data.description,
            website: data.website,
        })
        return transformCompany(response.data)
    },

    // Positions
    getPositions: async (params?: {
        companyId?: number
        modality?: string
        search?: string
        onlyAvailable?: boolean
        offset?: number
        limit?: number
    }): Promise<Position[]> => {
        const response = await apiClient.get('/internships/positions', {
            params: {
                company_id: params?.companyId,
                modality: params?.modality,
                search: params?.search,
                only_available: params?.onlyAvailable,
                offset: params?.offset,
                limit: params?.limit,
            },
        })
        return response.data.map(transformPosition)
    },

    getPosition: async (id: number): Promise<Position> => {
        const response = await apiClient.get(`/internships/positions/${id}`)
        return transformPosition(response.data)
    },

    // Applications
    applyToPosition: async (data: {
        positionId: number
        cvPath?: string
        coverLetter?: string
    }): Promise<Application> => {
        const response = await apiClient.post('/internships/apply', {
            position_id: data.positionId,
            cv_path: data.cvPath,
            cover_letter: data.coverLetter,
        })
        return transformApplication(response.data)
    },

    getMyApplications: async (status?: string): Promise<Application[]> => {
        const response = await apiClient.get('/internships/my-applications', {
            params: { status },
        })
        return response.data.map(transformApplication)
    },

    cancelApplication: async (id: number): Promise<void> => {
        await apiClient.delete(`/internships/applications/${id}`)
    },

    // Internships
    getActiveInternship: async (): Promise<Internship | null> => {
        const response = await apiClient.get('/internships/active')
        return response.data ? transformInternship(response.data) : null
    },

    getMyInternships: async (status?: string): Promise<Internship[]> => {
        const response = await apiClient.get('/internships/my-internships', {
            params: { status },
        })
        return response.data.map(transformInternship)
    },

    getInternship: async (id: number): Promise<Internship> => {
        const response = await apiClient.get(`/internships/${id}`)
        return transformInternship(response.data)
    },

    // Reports
    getReports: async (internshipId: number): Promise<Report[]> => {
        const response = await apiClient.get(`/internships/${internshipId}/reports`)
        return response.data.map(transformReport)
    },

    createReport: async (internshipId: number, data: {
        monthNumber: number
        reportDate: string
        hoursWorked: number
        activitiesSummary?: string
        achievements?: string
        challenges?: string
    }): Promise<Report> => {
        const response = await apiClient.post(`/internships/${internshipId}/reports`, {
            internship_id: internshipId,
            month_number: data.monthNumber,
            report_date: data.reportDate,
            hours_worked: data.hoursWorked,
            activities_summary: data.activitiesSummary,
            achievements: data.achievements,
            challenges: data.challenges,
        })
        return transformReport(response.data)
    },

    submitReport: async (internshipId: number, reportId: number): Promise<Report> => {
        const response = await apiClient.put(
            `/internships/${internshipId}/reports/${reportId}/submit`
        )
        return transformReport(response.data)
    },
}
