import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
    id: number
    email: string
    isActive: boolean
    isVerified: boolean
    profile?: {
        firstName: string
        lastName: string
        studentId?: string
        employeeId?: string
        department?: string
        program?: string
        photoUrl?: string
    }
    roles: string[]
}

interface AuthState {
    user: User | null
    accessToken: string | null
    refreshToken: string | null
    isAuthenticated: boolean

    // Actions
    setTokens: (accessToken: string, refreshToken: string) => void
    setUser: (user: User) => void
    logout: () => void
    hasRole: (role: string) => boolean
    hasAnyRole: (roles: string[]) => boolean
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,

            setTokens: (accessToken, refreshToken) => {
                set({
                    accessToken,
                    refreshToken,
                    isAuthenticated: true,
                })
            },

            setUser: (user) => {
                set({ user })
            },

            logout: () => {
                set({
                    user: null,
                    accessToken: null,
                    refreshToken: null,
                    isAuthenticated: false,
                })
            },

            hasRole: (role) => {
                const { user } = get()
                return user?.roles.includes(role) ?? false
            },

            hasAnyRole: (roles) => {
                const { user } = get()
                return roles.some((role) => user?.roles.includes(role)) ?? false
            },
        }),
        {
            name: 'sigaia-auth',
            partialize: (state) => ({
                accessToken: state.accessToken,
                refreshToken: state.refreshToken,
                user: state.user,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
)
