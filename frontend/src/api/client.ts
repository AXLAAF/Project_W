import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = useAuthStore.getState().accessToken
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

        // If 401 and not already retrying, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = useAuthStore.getState().refreshToken
                if (!refreshToken) {
                    throw new Error('No refresh token')
                }

                const response = await axios.post(`${API_URL}/auth/refresh`, {
                    refresh_token: refreshToken,
                })

                const { access_token, refresh_token } = response.data
                useAuthStore.getState().setTokens(access_token, refresh_token)

                // Retry original request
                originalRequest.headers.Authorization = `Bearer ${access_token}`
                return apiClient(originalRequest)
            } catch (refreshError) {
                // Refresh failed, logout user
                useAuthStore.getState().logout()
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

// API Error type
export interface ApiError {
    detail: string
    status: number
}

export function handleApiError(error: unknown): ApiError {
    if (axios.isAxiosError(error)) {
        return {
            detail: error.response?.data?.detail || error.message,
            status: error.response?.status || 500,
        }
    }
    return {
        detail: 'An unexpected error occurred',
        status: 500,
    }
}
