import { Bell, Check, Trash2, X } from 'lucide-react'
import { Notification } from '@/hooks/useNotifications'
import clsx from 'clsx'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'

interface NotificationsPopoverProps {
    notifications: Notification[]
    onMarkAsRead: (id: number) => void
    onMarkAllAsRead: () => void
    onClear: () => void
    onClose: () => void
}

export default function NotificationsPopover({
    notifications,
    onMarkAsRead,
    onMarkAllAsRead,
    onClear,
    onClose,
}: NotificationsPopoverProps) {
    return (
        <div className="absolute right-0 mt-2 w-80 md:w-96 card shadow-xl z-50 animate-fade-in overflow-hidden">
            <div className="p-4 border-b border-surface-200 dark:border-surface-700 flex items-center justify-between bg-surface-50 dark:bg-surface-900/50">
                <h3 className="font-semibold text-sm">Notificaciones</h3>
                <div className="flex items-center gap-1">
                    <button
                        onClick={onMarkAllAsRead}
                        className="p-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded text-surface-500 hover:text-primary-600"
                        title="Marcar todas como leídas"
                    >
                        <Check className="w-4 h-4" />
                    </button>
                    <button
                        onClick={onClear}
                        className="p-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded text-surface-500 hover:text-red-600"
                        title="Borrar todas"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                    <button
                        onClick={onClose}
                        className="p-1 hover:bg-surface-200 dark:hover:bg-surface-700 rounded text-surface-500"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            </div>

            <div className="max-h-96 overflow-y-auto">
                {notifications.length === 0 ? (
                    <div className="p-8 text-center text-surface-500">
                        <Bell className="w-8 h-8 mx-auto mb-2 opacity-20" />
                        <p className="text-sm">No tienes notificaciones</p>
                    </div>
                ) : (
                    <div className="divide-y divide-surface-100 dark:divide-surface-800">
                        {notifications.map((notification) => (
                            <div
                                key={notification.id}
                                onClick={() => !notification.isRead && onMarkAsRead(notification.id)}
                                className={clsx(
                                    'p-4 hover:bg-surface-50 dark:hover:bg-surface-800/50 transition-colors cursor-pointer',
                                    !notification.isRead && 'bg-primary-50/50 dark:bg-primary-900/10'
                                )}
                            >
                                <div className="flex gap-3">
                                    <div className={clsx(
                                        'mt-1 w-2 h-2 rounded-full flex-shrink-0',
                                        !notification.isRead ? 'bg-primary-500' : 'bg-transparent'
                                    )} />
                                    <div className="flex-1 space-y-1">
                                        <p className={clsx(
                                            'text-sm font-medium',
                                            !notification.isRead ? 'text-surface-900 dark:text-surface-100' : 'text-surface-600 dark:text-surface-400'
                                        )}>
                                            {notification.title}
                                        </p>
                                        <p className="text-xs text-surface-500 line-clamp-2">
                                            {notification.message}
                                        </p>
                                        <p className="text-[10px] text-surface-400">
                                            {formatDistanceToNow(notification.createdAt, { addSuffix: true, locale: es })}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
