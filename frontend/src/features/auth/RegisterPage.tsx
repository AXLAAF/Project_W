import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff, Loader2 } from 'lucide-react'
import { authApi, RegisterRequest } from '@/api/auth'
import { handleApiError } from '@/api/client'

export default function RegisterPage() {
    const navigate = useNavigate()
    const [showPassword, setShowPassword] = useState(false)
    const [formData, setFormData] = useState<RegisterRequest>({
        email: '',
        password: '',
        profile: {
            first_name: '',
            last_name: '',
            student_id: '',
            program: '',
        },
    })
    const [error, setError] = useState('')

    const registerMutation = useMutation({
        mutationFn: authApi.register,
        onSuccess: () => {
            navigate('/login', { state: { registered: true } })
        },
        onError: (err) => {
            const apiError = handleApiError(err)
            setError(apiError.detail)
        },
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        registerMutation.mutate(formData)
    }

    const updateProfile = (field: string, value: string) => {
        setFormData({
            ...formData,
            profile: { ...formData.profile, [field]: value },
        })
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
                    <p className="text-primary-200 mt-1">Crear cuenta</p>
                </div>

                {/* Register Card */}
                <div className="card p-8">
                    <h2 className="text-xl font-semibold text-center mb-6">Registro</h2>

                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm dark:bg-red-900/30 dark:text-red-400">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="firstName" className="label">
                                    Nombre
                                </label>
                                <input
                                    id="firstName"
                                    type="text"
                                    className="input"
                                    placeholder="Juan"
                                    value={formData.profile.first_name}
                                    onChange={(e) => updateProfile('first_name', e.target.value)}
                                    required
                                />
                            </div>
                            <div>
                                <label htmlFor="lastName" className="label">
                                    Apellido
                                </label>
                                <input
                                    id="lastName"
                                    type="text"
                                    className="input"
                                    placeholder="Pérez"
                                    value={formData.profile.last_name}
                                    onChange={(e) => updateProfile('last_name', e.target.value)}
                                    required
                                />
                            </div>
                        </div>

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
                            <label htmlFor="studentId" className="label">
                                Matrícula
                            </label>
                            <input
                                id="studentId"
                                type="text"
                                className="input"
                                placeholder="A01234567"
                                value={formData.profile.student_id}
                                onChange={(e) => updateProfile('student_id', e.target.value)}
                            />
                        </div>

                        <div>
                            <label htmlFor="program" className="label">
                                Carrera / Programa
                            </label>
                            <input
                                id="program"
                                type="text"
                                className="input"
                                placeholder="Ingeniería en Sistemas"
                                value={formData.profile.program}
                                onChange={(e) => updateProfile('program', e.target.value)}
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
                                    placeholder="Mínimo 8 caracteres"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    minLength={8}
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

                        <button
                            type="submit"
                            disabled={registerMutation.isPending}
                            className="btn-primary w-full"
                        >
                            {registerMutation.isPending ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" />
                                    Registrando...
                                </>
                            ) : (
                                'Crear cuenta'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-surface-600 dark:text-surface-400">
                        ¿Ya tienes cuenta?{' '}
                        <Link to="/login" className="text-primary-600 hover:underline font-medium">
                            Inicia sesión
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    )
}
