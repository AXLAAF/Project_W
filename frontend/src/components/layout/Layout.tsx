import { useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/api/auth'

export default function Layout() {
    const { setUser } = useAuthStore()

    useEffect(() => {
        // Refresh user data on mount to ensure profile is up to date
        const fetchUser = async () => {
            try {
                const user = await authApi.getCurrentUser()
                setUser(user)
            } catch (error) {
                console.error('Failed to refresh user data', error)
            }
        }
        fetchUser()
    }, [setUser])

    return (
        <div className="min-h-screen bg-surface-50 dark:bg-surface-950">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6">
                    <div className="max-w-7xl mx-auto">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    )
}
