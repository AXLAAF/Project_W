import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { User, Camera, Save, X } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { apiClient, handleApiError } from '@/api/client'
import { Button, Input, Card, CardHeader, CardBody } from '@/components/ui'

interface ProfileUpdateData {
    first_name?: string
    last_name?: string
    department?: string
    program?: string
    phone?: string
}

export default function ProfilePage() {
    const { user, setUser } = useAuthStore()
    const queryClient = useQueryClient()
    const [isEditing, setIsEditing] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')

    const [formData, setFormData] = useState<ProfileUpdateData>({
        first_name: user?.profile?.firstName || '',
        last_name: user?.profile?.lastName || '',
        department: user?.profile?.department || '',
        program: user?.profile?.program || '',
        phone: user?.profile?.phone || '',
    })

    const updateProfileMutation = useMutation({
        mutationFn: async (data: ProfileUpdateData) => {
            const response = await apiClient.put('/users/me', data)
            return response.data
        },
        onSuccess: (data) => {
            setUser({
                ...user!,
                profile: {
                    firstName: data.profile.first_name,
                    lastName: data.profile.last_name,
                    studentId: data.profile.student_id,
                    employeeId: data.profile.employee_id,
                    department: data.profile.department,
                    program: data.profile.program,
                    photoUrl: data.profile.photo_url,
                },
            })
            queryClient.invalidateQueries({ queryKey: ['currentUser'] })
            setIsEditing(false)
            setSuccess('Perfil actualizado correctamente')
            setTimeout(() => setSuccess(''), 3000)
        },
        onError: (err) => {
            setError(handleApiError(err).detail)
        },
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        updateProfileMutation.mutate(formData)
    }

    const handleCancel = () => {
        setIsEditing(false)
        setFormData({
            first_name: user?.profile?.firstName || '',
            last_name: user?.profile?.lastName || '',
            department: user?.profile?.department || '',
            program: user?.profile?.program || '',
            phone: user?.profile?.phone || '',
        })
    }

    return (
        <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
            <h1 className="text-2xl font-bold">Mi Perfil</h1>

            {/* Profile Card */}
            <Card>
                <CardHeader action={
                    !isEditing && (
                        <Button variant="secondary" size="sm" onClick={() => setIsEditing(true)}>
                            Editar
                        </Button>
                    )
                }>
                    Información Personal
                </CardHeader>
                <CardBody>
                    {error && (
                        <div className="mb-4 p-3 rounded-lg bg-red-50 text-red-700 text-sm dark:bg-red-900/30 dark:text-red-400">
                            {error}
                        </div>
                    )}
                    {success && (
                        <div className="mb-4 p-3 rounded-lg bg-green-50 text-green-700 text-sm dark:bg-green-900/30 dark:text-green-400">
                            {success}
                        </div>
                    )}

                    <form onSubmit={handleSubmit}>
                        {/* Avatar */}
                        <div className="flex items-center gap-4 mb-6">
                            <div className="relative">
                                <div className="w-20 h-20 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                                    {user?.profile?.photoUrl ? (
                                        <img
                                            src={user.profile.photoUrl}
                                            alt="Avatar"
                                            className="w-20 h-20 rounded-full object-cover"
                                        />
                                    ) : (
                                        <User className="w-10 h-10 text-primary-600 dark:text-primary-400" />
                                    )}
                                </div>
                                {isEditing && (
                                    <button
                                        type="button"
                                        className="absolute bottom-0 right-0 p-1.5 rounded-full bg-primary-600 text-white hover:bg-primary-700"
                                    >
                                        <Camera className="w-4 h-4" />
                                    </button>
                                )}
                            </div>
                            <div>
                                <h3 className="font-semibold text-lg">
                                    {user?.profile?.firstName} {user?.profile?.lastName}
                                </h3>
                                <p className="text-surface-500">{user?.email}</p>
                                {user?.profile?.studentId && (
                                    <p className="text-sm text-surface-400">Matrícula: {user.profile.studentId}</p>
                                )}
                            </div>
                        </div>

                        {/* Form Fields */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <Input
                                label="Nombre"
                                value={formData.first_name}
                                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                                disabled={!isEditing}
                            />
                            <Input
                                label="Apellido"
                                value={formData.last_name}
                                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                                disabled={!isEditing}
                            />
                            <Input
                                label="Departamento"
                                value={formData.department}
                                onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                                disabled={!isEditing}
                            />
                            <Input
                                label="Programa / Carrera"
                                value={formData.program}
                                onChange={(e) => setFormData({ ...formData, program: e.target.value })}
                                disabled={!isEditing}
                            />
                            <Input
                                label="Teléfono"
                                value={formData.phone}
                                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                                disabled={!isEditing}
                            />
                        </div>

                        {/* Actions */}
                        {isEditing && (
                            <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-surface-200 dark:border-surface-700">
                                <Button type="button" variant="secondary" onClick={handleCancel}>
                                    <X className="w-4 h-4" />
                                    Cancelar
                                </Button>
                                <Button type="submit" isLoading={updateProfileMutation.isPending}>
                                    <Save className="w-4 h-4" />
                                    Guardar cambios
                                </Button>
                            </div>
                        )}
                    </form>
                </CardBody>
            </Card>

            {/* Roles Card */}
            <Card>
                <CardHeader>Roles Asignados</CardHeader>
                <CardBody>
                    <div className="flex flex-wrap gap-2">
                        {user?.roles.map((role) => (
                            <span
                                key={role}
                                className="px-3 py-1 rounded-full bg-primary-100 text-primary-700 text-sm font-medium dark:bg-primary-900/30 dark:text-primary-400"
                            >
                                {role}
                            </span>
                        ))}
                    </div>
                </CardBody>
            </Card>

            {/* Account Info Card */}
            <Card>
                <CardHeader>Información de la Cuenta</CardHeader>
                <CardBody>
                    <dl className="space-y-3">
                        <div className="flex justify-between">
                            <dt className="text-surface-500">Estado</dt>
                            <dd>
                                <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-sm dark:bg-green-900/30 dark:text-green-400">
                                    {user?.isActive ? 'Activo' : 'Inactivo'}
                                </span>
                            </dd>
                        </div>
                        <div className="flex justify-between">
                            <dt className="text-surface-500">Verificado</dt>
                            <dd>
                                <span className={`px-2 py-0.5 rounded-full text-sm ${user?.isVerified
                                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                        : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                                    }`}>
                                    {user?.isVerified ? 'Sí' : 'Pendiente'}
                                </span>
                            </dd>
                        </div>
                    </dl>
                </CardBody>
            </Card>
        </div>
    )
}
