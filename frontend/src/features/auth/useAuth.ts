import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import { handleApiError } from '@/api/client'

export function useAuth() {
    const {
        user,
        isAuthenticated,
        accessToken,
        setTokens,
        setUser,
        logout: storeLogout,
        hasRole,
        hasAnyRole,
    } = useAuthStore()

    const queryClient = useQueryClient()

    // Fetch current user query
    const userQuery = useQuery({
        queryKey: ['currentUser'],
        queryFn: authApi.getCurrentUser,
        enabled: isAuthenticated && !user,
        staleTime: 5 * 60 * 1000,
        retry: false,
    })

    // Login mutation
    const loginMutation = useMutation({
        mutationFn: authApi.login,
        onSuccess: async (tokens) => {
            setTokens(tokens.access_token, tokens.refresh_token)
            const userData = await authApi.getCurrentUser()
            setUser(userData)
            queryClient.setQueryData(['currentUser'], userData)
        },
    })

    // Logout mutation
    const logoutMutation = useMutation({
        mutationFn: authApi.logout,
        onSettled: () => {
            storeLogout()
            queryClient.clear()
        },
    })

    // Register mutation
    const registerMutation = useMutation({
        mutationFn: authApi.register,
    })

    const login = async (email: string, password: string) => {
        try {
            await loginMutation.mutateAsync({ email, password })
            return { success: true }
        } catch (error) {
            return { success: false, error: handleApiError(error) }
        }
    }

    const logout = () => {
        logoutMutation.mutate()
    }

    const register = async (data: Parameters<typeof authApi.register>[0]) => {
        try {
            await registerMutation.mutateAsync(data)
            return { success: true }
        } catch (error) {
            return { success: false, error: handleApiError(error) }
        }
    }

    return {
        user: user || userQuery.data,
        isAuthenticated,
        isLoading: userQuery.isLoading || loginMutation.isPending,
        accessToken,
        login,
        logout,
        register,
        hasRole,
        hasAnyRole,
        loginError: loginMutation.error,
        registerError: registerMutation.error,
    }
}
