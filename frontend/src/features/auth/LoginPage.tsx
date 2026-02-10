import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { authApi, LoginRequest } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import { handleApiError } from '@/api/client'

export default function LoginPage() {
    const navigate = useNavigate()
    const { setTokens, setUser } = useAuthStore()
    const [showPassword, setShowPassword] = useState(false)
    const [formData, setFormData] = useState<LoginRequest>({
        email: '',
        password: '',
    })
    const [error, setError] = useState('')

    const loginMutation = useMutation({
        mutationFn: authApi.login,
        onSuccess: async (tokens) => {
            setTokens(tokens.access_token, tokens.refresh_token)
            try {
                const user = await authApi.getCurrentUser()
                setUser(user)
                navigate('/dashboard')
            } catch {
                setError('Error al obtener información del usuario')
            }
        },
        onError: (err) => {
            const apiError = handleApiError(err)
            setError(apiError.detail)
        },
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        loginMutation.mutate(formData)
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 p-4">
            <div className="w-full max-w-md">
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white/10 backdrop-blur mb-4">
                        <span className="text-3xl font-bold text-white">S</span>
                    </div>
                    <h1 className="text-2xl font-bold text-white">SIGAIA</h1>
                    <p className="text-primary-200 mt-1">Sistema de Gestión Académica</p>
                </div>

                {/* Login Card */}
                <div className="card p-8">
                    <h2 className="text-xl font-semibold text-center mb-6">Iniciar Sesión</h2>

                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm dark:bg-red-900/30 dark:text-red-400">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="email" className="label">
                                Correo institucional
                            </label>
                            <input
                                id="email"
                                type="email"
                                className="input"
                                placeholder="usuario@universidad.edu"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                required
                            />
                        </div>

                        <div>
                            <label htmlFor="password" className="label">
                                Contraseña
                            </label>
                            <div className="relative">
                                <input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    className="input pr-10"
                                    placeholder="••••••••"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        <div className="flex items-center justify-between text-sm">
                            <label className="flex items-center gap-2">
                                <input type="checkbox" className="rounded border-surface-300" />
                                <span className="text-surface-600 dark:text-surface-400">Recordarme</span>
                            </label>
                            <a href="#" className="text-primary-600 hover:underline">
                                ¿Olvidaste tu contraseña?
                            </a>
                        </div>

                        <button
                            type="submit"
                            disabled={loginMutation.isPending}
                            className="btn-primary w-full"
                        >
                            {loginMutation.isPending ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Iniciando sesión...
                                </>
                            ) : (
                                'Iniciar Sesión'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-surface-600 dark:text-surface-400">
                        ¿No tienes cuenta?{' '}
                        <Link to="/register" className="text-primary-600 hover:underline font-medium">
                            Regístrate aquí
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
