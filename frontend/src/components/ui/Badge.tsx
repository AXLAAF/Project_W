import clsx from 'clsx'

interface BadgeProps {
    variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
    size?: 'sm' | 'md'
    children: React.ReactNode
    className?: string
}

export default function Badge({
    variant = 'default',
    size = 'md',
    children,
    className,
}: BadgeProps) {
    const variants = {
        default: 'bg-surface-100 text-surface-700 dark:bg-surface-800 dark:text-surface-300',
        success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
        danger: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
        info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    }

    const sizes = {
        sm: 'px-2 py-0.5 text-xs',
        md: 'px-2.5 py-0.5 text-sm',
    }

    return (
        <span
            className={clsx(
                'inline-flex items-center font-medium rounded-full',
                variants[variant],
                sizes[size],
                className
            )}
        >
            {children}
        </span>
    )
}

// Convenience components for risk levels
export function RiskBadge({ level }: { level: 'low' | 'medium' | 'high' }) {
    const config = {
        low: { variant: 'success' as const, label: 'Bajo' },
        medium: { variant: 'warning' as const, label: 'Medio' },
        high: { variant: 'danger' as const, label: 'Alto' },
    }

    const { variant, label } = config[level]

    return <Badge variant={variant}>{label}</Badge>
}
