import { NavLink } from 'react-router-dom'
import {
    LayoutDashboard,
    GraduationCap,
    AlertTriangle,
    Search,
    Briefcase,
    CalendarDays,
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useUIStore } from '@/store/uiStore'
import clsx from 'clsx'

interface NavItem {
    label: string
    path: string
    icon: React.ReactNode
    roles?: string[]
}

const navItems: NavItem[] = [
    {
        label: 'Dashboard',
        path: '/dashboard',
        icon: <LayoutDashboard className="w-5 h-5" />,
    },
    {
        label: 'Planeación',
        path: '/planning',
        icon: <GraduationCap className="w-5 h-5" />,
        roles: ['ALUMNO', 'COORDINADOR', 'ADMIN_SISTEMA'],
    },
    {
        label: 'Riesgo Académico',
        path: '/risk',
        icon: <AlertTriangle className="w-5 h-5" />,
        roles: ['ALUMNO', 'PROFESOR', 'COORDINADOR', 'ADMIN_SISTEMA'],
    },
    {
        label: 'Búsqueda',
        path: '/search',
        icon: <Search className="w-5 h-5" />,
    },
    {
        label: 'Prácticas',
        path: '/internships',
        icon: <Briefcase className="w-5 h-5" />,
        roles: ['ALUMNO', 'GESTOR_PRACTICAS', 'ADMIN_SISTEMA'],
    },
    {
        label: 'Reservas',
        path: '/reservations',
        icon: <CalendarDays className="w-5 h-5" />,
    },
]

export default function Sidebar() {
    const { hasAnyRole } = useAuthStore()
    const { isSidebarOpen, closeSidebar } = useUIStore()

    const visibleItems = navItems.filter((item) => {
        if (!item.roles) return true
        return hasAnyRole(item.roles)
    })

    return (
        <>
            {/* Mobile Overlay */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/50 lg:hidden backdrop-blur-sm transition-opacity"
                    onClick={closeSidebar}
                />
            )}

            {/* Sidebar */}
            <aside
                className={clsx(
                    'fixed inset-y-0 left-0 z-50 w-64 flex-col border-r border-surface-200 dark:border-surface-800 bg-white dark:bg-surface-900 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-auto lg:flex',
                    isSidebarOpen ? 'translate-x-0 shadow-xl' : '-translate-x-full'
                )}
            >
                <div className="flex h-16 items-center justify-center border-b border-surface-200 dark:border-surface-800 lg:hidden">
                    <span className="font-semibold text-lg">SIGAIA</span>
                </div>

                <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                    {visibleItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            onClick={() => window.innerWidth < 1024 && closeSidebar()}
                            className={({ isActive }) =>
                                clsx(
                                    'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                                        : 'text-surface-600 hover:bg-surface-100 dark:text-surface-400 dark:hover:bg-surface-800'
                                )
                            }
                        >
                            {item.icon}
                            {item.label}
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-surface-200 dark:border-surface-800">
                    <div className="text-xs text-surface-400 text-center">
                        SIGAIA v0.1.0
                    </div>
                </div>
            </aside>
        </>
    )
}
