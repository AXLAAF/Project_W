import { useState, useEffect } from 'react'

export interface Notification {
    id: number
    title: string
    message: string
    type: 'info' | 'success' | 'warning' | 'error'
    isRead: boolean
    createdAt: Date
}

const MOCK_NOTIFICATIONS: Notification[] = [
    {
        id: 1,
        title: 'Bienvenido a SIGAIA',
        message: 'Explora los nuevos módulos de planeación y riesgo académico.',
        type: 'info',
        isRead: false,
        createdAt: new Date(),
    },
    {
        id: 2,
        title: 'Recordatorio de Inscripción',
        message: 'Tu turno de inscripción comienza mañana a las 10:00 AM.',
        type: 'warning',
        isRead: false,
        createdAt: new Date(Date.now() - 86400000), // Yesterday
    },
    {
        id: 3,
        title: 'Calificación Publicada',
        message: 'Se ha publicado la calificación final de Matemáticas Avanzadas.',
        type: 'success',
        isRead: true,
        createdAt: new Date(Date.now() - 172800000), // 2 days ago
    },
]

export function useNotifications() {
    const [notifications, setNotifications] = useState<Notification[]>([])
    const [unreadCount, setUnreadCount] = useState(0)

    useEffect(() => {
        // Simulate fetching notifications
        setNotifications(MOCK_NOTIFICATIONS)
    }, [])

    useEffect(() => {
        setUnreadCount(notifications.filter((n) => !n.isRead).length)
    }, [notifications])

    const markAsRead = (id: number) => {
        setNotifications((prev) =>
            prev.map((n) => (n.id === id ? { ...n, isRead: true } : n))
        )
    }

    const markAllAsRead = () => {
        setNotifications((prev) => prev.map((n) => ({ ...n, isRead: true })))
    }

    const clearNotifications = () => {
        setNotifications([])
    }

    return {
        notifications,
        unreadCount,
        markAsRead,
        markAllAsRead,
        clearNotifications,
    }
}
