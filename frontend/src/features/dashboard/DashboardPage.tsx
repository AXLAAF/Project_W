import {
    GraduationCap,
    AlertTriangle,
    Search,
    Briefcase,
    CalendarDays,
    TrendingUp,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'

export default function DashboardPage() {
    const { user } = useAuthStore()

    const quickActions = [
        {
            title: 'Planeación de Materias',
            description: 'Planea tu próximo semestre',
            icon: <GraduationCap className="w-6 h-6" />,
            color: 'bg-blue-500',
            href: '/planning',
        },
        {
            title: 'Riesgo Académico',
            description: 'Consulta tu índice de riesgo',
            icon: <AlertTriangle className="w-6 h-6" />,
            color: 'bg-amber-500',
            href: '/risk',
        },
        {
            title: 'Buscar Material',
            description: 'Encuentra documentos académicos',
            icon: <Search className="w-6 h-6" />,
            color: 'bg-purple-500',
            href: '/search',
        },
        {
            title: 'Prácticas Profesionales',
            description: 'Explora oportunidades',
            icon: <Briefcase className="w-6 h-6" />,
            color: 'bg-green-500',
            href: '/internships',
        },
        {
            title: 'Reservar Recursos',
            description: 'Salas, laboratorios y equipos',
            icon: <CalendarDays className="w-6 h-6" />,
            color: 'bg-rose-500',
            href: '/reservations',
        },
    ]

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Welcome Header */}
            <div className="card p-6 bg-gradient-to-r from-primary-600 to-secondary-600 text-white">
                <h1 className="text-2xl font-bold">
                    ¡Bienvenido, {user?.profile?.firstName || user?.email?.split('@')[0] || 'Estudiante'}!
                </h1>
                <p className="text-primary-100 mt-1">
                    Sistema de Gestión Académica Integral con IA
                </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card p-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-surface-500">Promedio General</p>
                            <p className="text-2xl font-bold text-surface-900 dark:text-white">8.7</p>
                        </div>
                        <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/30">
                            <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
                        </div>
                    </div>
                    <p className="text-xs text-green-600 mt-2">+0.3 vs semestre anterior</p>
                </div>

                <div className="card p-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-surface-500">Créditos Cursados</p>
                            <p className="text-2xl font-bold text-surface-900 dark:text-white">156</p>
                        </div>
                        <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900/30">
                            <GraduationCap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                        </div>
                    </div>
                    <p className="text-xs text-surface-500 mt-2">de 240 requeridos</p>
                </div>

                <div className="card p-5">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-surface-500">Índice de Riesgo</p>
                            <p className="text-2xl font-bold text-green-600">Bajo</p>
                        </div>
                        <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/30">
                            <AlertTriangle className="w-6 h-6 text-green-600 dark:text-green-400" />
                        </div>
                    </div>
                    <p className="text-xs text-surface-500 mt-2">Puntuación: 18/100</p>
                </div>
            </div>

            {/* Quick Actions */}
            <div>
                <h2 className="text-lg font-semibold mb-4">Acciones Rápidas</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {quickActions.map((action) => (
                        <a
                            key={action.href}
                            href={action.href}
                            className="card p-5 hover:shadow-md transition-shadow group"
                        >
                            <div className="flex items-start gap-4">
                                <div className={`p-3 rounded-xl ${action.color} text-white`}>
                                    {action.icon}
                                </div>
                                <div>
                                    <h3 className="font-medium group-hover:text-primary-600 transition-colors">
                                        {action.title}
                                    </h3>
                                    <p className="text-sm text-surface-500 mt-1">{action.description}</p>
                                </div>
                            </div>
                        </a>
                    ))}
                </div>
            </div>

            {/* Recent Activity Placeholder */}
            <div className="card">
                <div className="card-header">
                    <h2 className="font-semibold">Actividad Reciente</h2>
                </div>
                <div className="card-body">
                    <div className="text-center py-8 text-surface-500">
                        <p>No hay actividad reciente para mostrar.</p>
                        <p className="text-sm mt-1">Comienza explorando los módulos disponibles.</p>
                    </div>
                </div>
            </div>
        </div>
    )
}
