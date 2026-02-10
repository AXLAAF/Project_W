import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import Layout from '@/components/layout/Layout'
import LoginPage from '@/features/auth/LoginPage'
import RegisterPage from '@/features/auth/RegisterPage'
import DashboardPage from '@/features/dashboard/DashboardPage'
import ProfilePage from '@/features/profile/ProfilePage'
import PlanningPage from '@/features/planning/PlanningPage'
import HistoryPage from '@/features/planning/HistoryPage'
import RiskPage from '@/features/risk/RiskPage'
import { InternshipsPage, MyApplicationsPage, ActiveInternshipPage } from '@/features/internships'
import { ResourcesPage, MyReservationsPage } from '@/features/reservations'
import SearchPage from '@/features/search/SearchPage'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />
    }

    return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />
    }

    return <>{children}</>
}

export default function App() {
    return (
        <Routes>
            {/* Public routes */}
            <Route
                path="/login"
                element={
                    <PublicRoute>
                        <LoginPage />
                    </PublicRoute>
                }
            />
            <Route
                path="/register"
                element={
                    <PublicRoute>
                        <RegisterPage />
                    </PublicRoute>
                }
            />

            {/* Protected routes */}
            <Route
                path="/"
                element={
                    <ProtectedRoute>
                        <Layout />
                    </ProtectedRoute>
                }
            >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />
                <Route path="profile" element={<ProfilePage />} />
                <Route path="planning" element={<PlanningPage />} />
                <Route path="history" element={<HistoryPage />} />
                <Route path="risk" element={<RiskPage />} />
                {/* Internships routes */}
                <Route path="internships" element={<InternshipsPage />} />
                <Route path="internships/applications" element={<MyApplicationsPage />} />
                <Route path="internships/active" element={<ActiveInternshipPage />} />
                {/* Search route */}
                <Route path="search" element={<SearchPage />} />

                {/* Reservations routes */}
                <Route path="reservations" element={<ResourcesPage />} />
                <Route path="reservations/my-reservations" element={<MyReservationsPage />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    )
}
