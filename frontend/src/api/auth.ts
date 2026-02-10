import { apiClient } from './client'
import type { User } from '@/store/authStore'

export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    email: string
    password: string
    profile: {
        first_name: string
        last_name: string
        student_id?: string
        employee_id?: string
        department?: string
        program?: string
    }
}

export interface TokenResponse {
    access_token: string
    refresh_token: string
    token_type: string
    expires_in: number
}

export interface ApiUser {
    id: number
    email: string
    is_active: boolean
    is_verified: boolean
    created_at: string
    updated_at: string
    profile?: {
        id: number
        user_id: number
        first_name: string
        last_name: string
        student_id?: string
        employee_id?: string
        department?: string
        program?: string
        photo_url?: string
    }
    roles: string[]
}

// Transform API user to frontend User type
function transformUser(apiUser: ApiUser): User {
    return {
        id: apiUser.id,
        email: apiUser.email,
        isActive: apiUser.is_active,
        isVerified: apiUser.is_verified,
        profile: apiUser.profile
            ? {
                firstName: apiUser.profile.first_name,
                lastName: apiUser.profile.last_name,
                studentId: apiUser.profile.student_id,
                employeeId: apiUser.profile.employee_id,
                department: apiUser.profile.department,
                program: apiUser.profile.program,
                photoUrl: apiUser.profile.photo_url,
            }
            : undefined,
        roles: apiUser.roles,
    }
}

export const authApi = {
    login: async (data: LoginRequest): Promise<TokenResponse> => {
        const response = await apiClient.post<TokenResponse>('/auth/login', data)
        return response.data
    },

    register: async (data: RegisterRequest): Promise<User> => {
        const response = await apiClient.post<ApiUser>('/auth/register', data)
        return transformUser(response.data)
    },

    logout: async (): Promise<void> => {
        await apiClient.post('/auth/logout')
    },

    refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
        const response = await apiClient.post<TokenResponse>('/auth/refresh', {
            refresh_token: refreshToken,
        })
        return response.data
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await apiClient.get<ApiUser>('/users/me')
        return transformUser(response.data)
    },
}
