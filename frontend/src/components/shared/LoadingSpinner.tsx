import { Loader2 } from 'lucide-react'
import clsx from 'clsx'

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg'
    className?: string
    label?: string
}

export default function LoadingSpinner({
    size = 'md',
    className,
    label,
}: LoadingSpinnerProps) {
    const sizes = {
        sm: 'w-4 h-4',
        md: 'w-6 h-6',
        lg: 'w-8 h-8',
    }

    return (
        <div className={clsx('flex items-center justify-center gap-2', className)}>
            <Loader2 className={clsx('animate-spin text-primary-600', sizes[size])} />
            {label && <span className="text-sm text-surface-600">{label}</span>}
        </div>
    )
}

// Full page loading state
export function PageLoader({ label = 'Cargando...' }: { label?: string }) {
    return (
        <div className="flex items-center justify-center min-h-[400px]">
            <LoadingSpinner size="lg" label={label} />
        </div>
    )
}
