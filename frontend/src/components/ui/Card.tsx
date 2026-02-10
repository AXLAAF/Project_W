import { ReactNode } from 'react'
import clsx from 'clsx'

interface CardProps {
    children: ReactNode
    className?: string
    padding?: 'none' | 'sm' | 'md' | 'lg'
}

export function Card({ children, className, padding = 'none' }: CardProps) {
    const paddingStyles = {
        none: '',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
    }

    return (
        <div
            className={clsx(
                'bg-white rounded-xl shadow-sm border border-surface-200',
                'dark:bg-surface-900 dark:border-surface-800',
                paddingStyles[padding],
                className
            )}
        >
            {children}
        </div>
    )
}

interface CardHeaderProps {
    children: ReactNode
    className?: string
    action?: ReactNode
}

export function CardHeader({ children, className, action }: CardHeaderProps) {
    return (
        <div
            className={clsx(
                'px-6 py-4 border-b border-surface-200 dark:border-surface-800',
                'flex items-center justify-between',
                className
            )}
        >
            <div className="font-semibold">{children}</div>
            {action && <div>{action}</div>}
        </div>
    )
}

interface CardBodyProps {
    children: ReactNode
    className?: string
}

export function CardBody({ children, className }: CardBodyProps) {
    return <div className={clsx('p-6', className)}>{children}</div>
}

interface CardFooterProps {
    children: ReactNode
    className?: string
}


export function CardFooter({ children, className }: CardFooterProps) {
    return (
        <div
            className={clsx(
                'px-6 py-4 border-t border-surface-200 dark:border-surface-800',
                'flex items-center justify-end gap-3',
                className
            )}
        >
            {children}
        </div>
    )
}

export function CardTitle({ children, className }: { children: ReactNode; className?: string }) {
    return (
        <h3 className={clsx('font-semibold leading-none tracking-tight', className)}>
            {children}
        </h3>
    )
}

export function CardContent({ children, className }: { children: ReactNode; className?: string }) {
    return <div className={clsx('p-6 pt-0', className)}>{children}</div>
}
