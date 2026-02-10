import { Menu, Bell, User, LogOut } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/api/auth'
import { useUIStore } from '@/store/uiStore'
import { useNotifications } from '@/hooks/useNotifications'
import NotificationsPopover from './NotificationsPopover'

export default function Navbar() {
    const { user, logout } = useAuthStore()
    const { toggleSidebar } = useUIStore()
    const [showUserMenu, setShowUserMenu] = useState(false)

    // Notifications logic
    const { notifications, unreadCount, markAsRead, markAllAsRead, clearNotifications } = useNotifications()
    const [showNotifications, setShowNotifications] = useState(false)
    const notificationRef = useRef<HTMLDivElement>(null)

    // Close notifications when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
                setShowNotifications(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])

    // console.log('Current User in Navbar:', user)


    const handleLogout = async () => {
        try {
            await authApi.logout()
        } catch {
            // Continue with logout even if API fails
        }
        logout()
    }

    return (
        <header className="sticky top-0 z-40 glass border-b border-surface-200 dark:border-surface-800 bg-white/80 backdrop-blur-md">
            <div className="flex items-center justify-between h-16 px-4 lg:px-6">
                {/* Logo & Mobile Menu */}
                <div className="flex items-center gap-4">
                    <button
                        className="lg:hidden btn-ghost p-2 text-surface-600 dark:text-surface-400"
                        onClick={toggleSidebar}
                    >
                        <Menu className="w-6 h-6" />
                    </button>
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
                            <span className="text-white font-bold text-sm">S</span>
                        </div>
                        <span className="font-semibold text-lg hidden sm:block">SIGAIA</span>
                    </div>
                </div>

                {/* Right Section */}
                <div className="flex items-center gap-2">
                    {/* Notifications */}
                    <div className="relative" ref={notificationRef}>
                        <button
                            className="btn-ghost p-2 relative"
                            onClick={() => setShowNotifications(!showNotifications)}
                        >
                            <Bell className="w-5 h-5" />
                            {unreadCount > 0 && (
                                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
                            )}
                        </button>

                        {showNotifications && (
                            <NotificationsPopover
                                notifications={notifications}
                                onMarkAsRead={markAsRead}
                                onMarkAllAsRead={markAllAsRead}
                                onClear={clearNotifications}
                                onClose={() => setShowNotifications(false)}
                            />
                        )}
                    </div>

                    {/* User Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setShowUserMenu(!showUserMenu)}
                            className="flex items-center gap-2 btn-ghost px-2 py-1"
                        >
                            <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                                <User className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                            </div>
                            <span className="hidden sm:block text-sm font-medium">
                                {user?.profile?.firstName || user?.email?.split('@')[0] || 'Usuario'}
                                {/* DEBUG: {JSON.stringify(user)} */}
                            </span>
                        </button>

                        {showUserMenu && (
                            <div className="absolute right-0 mt-2 w-48 card py-1 animate-fade-in">
                                <div className="px-4 py-2 border-b border-surface-200 dark:border-surface-700">
                                    <p className="text-sm font-medium">
                                        {user?.profile?.firstName
                                            ? `${user?.profile?.firstName} ${user?.profile?.lastName}`
                                            : (user?.email?.split('@')[0] || 'Usuario')}
                                    </p>
                                    <p className="text-xs text-surface-500">{user?.email}</p>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-surface-100 dark:hover:bg-surface-800"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Cerrar sesión
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    )
}
