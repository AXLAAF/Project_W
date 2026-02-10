import { useQuery } from '@tanstack/react-query'
import {
    AlertTriangle,
    TrendingUp,
    TrendingDown,
    Minus,
    BookOpen,
    Calendar,
    FileText,
    Users,
} from 'lucide-react'
import { riskApi, RiskLevel, StudentRiskSummary } from '@/api/risk'
import { Card, CardHeader, CardBody, Badge } from '@/components/ui'
import { PageLoader } from '@/components/shared/LoadingSpinner'

// Mock group ID for demo - in production this would come from route/context
const DEMO_GROUP_ID = 1

export default function RiskPage() {
    const { data: riskSummary, isLoading } = useQuery({
        queryKey: ['myRisk', DEMO_GROUP_ID],
        queryFn: () => riskApi.getMyRisk(DEMO_GROUP_ID),
    })

    if (isLoading) {
        return <PageLoader label="Analizando indicadores de riesgo..." />
    }

    if (!riskSummary) {
        return (
            <div className="text-center py-12">
                <AlertTriangle className="w-12 h-12 mx-auto text-surface-300" />
                <p className="mt-4 text-surface-500">No hay datos de riesgo disponibles</p>
                <p className="text-sm text-surface-400 mt-2">
                    Inscríbete en un grupo para ver tu evaluación de riesgo académico
                </p>
            </div>
        )
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">Riesgo Académico</h1>
                <p className="text-surface-500 mt-1">
                    Monitorea tu progreso y recibe recomendaciones personalizadas
                </p>
            </div>

            {/* Main Risk Score */}
            <RiskScoreCard summary={riskSummary} />

            {/* Factor Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <FactorCard
                    title="Asistencia"
                    icon={<Calendar className="w-5 h-5" />}
                    score={riskSummary.factors?.attendance?.score || 0}
                    detail={`${riskSummary.factors?.attendance?.attendance_rate?.toFixed(0) || 100}% de asistencia`}
                    subdetail={`${riskSummary.factors?.attendance?.absences || 0} faltas de ${riskSummary.factors?.attendance?.total_classes || 0} clases`}
                />
                <FactorCard
                    title="Calificaciones"
                    icon={<BookOpen className="w-5 h-5" />}
                    score={riskSummary.factors?.grades?.score || 0}
                    detail={`Promedio: ${riskSummary.factors?.grades?.average?.toFixed(1) || 'N/A'}`}
                    subdetail="Basado en evaluaciones parciales"
                />
                <FactorCard
                    title="Entregas"
                    icon={<FileText className="w-5 h-5" />}
                    score={riskSummary.factors?.assignments?.score || 0}
                    detail={`${riskSummary.factors?.assignments?.on_time_rate?.toFixed(0) || 100}% a tiempo`}
                    subdetail={`${riskSummary.factors?.assignments?.missing || 0} tareas pendientes`}
                />
            </div>

            {/* Recommendations */}
            {riskSummary.recommendation && (
                <Card>
                    <CardHeader>
                        <div className="flex items-center gap-2">
                            <Users className="w-5 h-5 text-primary-600" />
                            Recomendaciones
                        </div>
                    </CardHeader>
                    <CardBody>
                        <div className="prose dark:prose-invert max-w-none">
                            {riskSummary.recommendation.split('\n').map((line, i) => (
                                <p key={i} className="mb-2 last:mb-0">
                                    {line}
                                </p>
                            ))}
                        </div>
                    </CardBody>
                </Card>
            )}
        </div>
    )
}

function RiskScoreCard({ summary }: { summary: StudentRiskSummary }) {
    const levelConfig: Record<RiskLevel, { color: string; bg: string; label: string }> = {
        LOW: { color: 'text-green-600', bg: 'bg-green-100 dark:bg-green-900/30', label: 'Bajo' },
        MEDIUM: { color: 'text-amber-600', bg: 'bg-amber-100 dark:bg-amber-900/30', label: 'Medio' },
        HIGH: { color: 'text-orange-600', bg: 'bg-orange-100 dark:bg-orange-900/30', label: 'Alto' },
        CRITICAL: { color: 'text-red-600', bg: 'bg-red-100 dark:bg-red-900/30', label: 'Crítico' },
    }

    const config = levelConfig[summary.riskLevel]

    const TrendIcon = summary.trend === 'increasing'
        ? TrendingUp
        : summary.trend === 'decreasing'
            ? TrendingDown
            : Minus

    const trendColor = summary.trend === 'increasing'
        ? 'text-red-500'
        : summary.trend === 'decreasing'
            ? 'text-green-500'
            : 'text-surface-400'

    return (
        <Card padding="lg">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                <div className="flex items-center gap-6">
                    {/* Score Circle */}
                    <div className={`relative w-28 h-28 rounded-full ${config.bg} flex items-center justify-center`}>
                        <div className="text-center">
                            <span className={`text-3xl font-bold ${config.color}`}>
                                {summary.currentScore}
                            </span>
                            <p className="text-xs text-surface-500">de 100</p>
                        </div>
                        {/* Risk indicator ring */}
                        <svg className="absolute inset-0 w-full h-full -rotate-90">
                            <circle
                                cx="50%"
                                cy="50%"
                                r="45%"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="4"
                                strokeDasharray={`${summary.currentScore * 2.83} 283`}
                                className={config.color}
                                strokeLinecap="round"
                            />
                        </svg>
                    </div>

                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg font-semibold">Nivel de Riesgo:</span>
                            <Badge variant={
                                summary.riskLevel === 'LOW' ? 'success' :
                                    summary.riskLevel === 'MEDIUM' ? 'warning' :
                                        summary.riskLevel === 'HIGH' ? 'warning' : 'danger'
                            }>
                                {config.label}
                            </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-surface-500">
                            <TrendIcon className={`w-4 h-4 ${trendColor}`} />
                            <span>
                                {summary.trend === 'increasing' && 'Tendencia al alza'}
                                {summary.trend === 'decreasing' && 'Mejorando'}
                                {summary.trend === 'stable' && 'Estable'}
                            </span>
                        </div>
                        <p className="text-xs text-surface-400 mt-1">
                            Última evaluación: {new Date(summary.lastAssessed).toLocaleDateString('es-MX')}
                        </p>
                    </div>
                </div>

                {summary.isAtRisk && (
                    <div className="flex items-center gap-3 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                        <AlertTriangle className="w-8 h-8 text-red-600" />
                        <div>
                            <p className="font-semibold text-red-700 dark:text-red-400">Atención requerida</p>
                            <p className="text-sm text-red-600 dark:text-red-300">
                                Tu nivel de riesgo requiere atención inmediata
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </Card>
    )
}

function FactorCard({
    title,
    icon,
    score,
    detail,
    subdetail,
}: {
    title: string
    icon: React.ReactNode
    score: number
    detail: string
    subdetail: string
}) {
    // Lower score = better for the student (less risk)
    const getScoreColor = (score: number) => {
        if (score <= 25) return 'text-green-600 bg-green-100 dark:bg-green-900/30'
        if (score <= 50) return 'text-amber-600 bg-amber-100 dark:bg-amber-900/30'
        if (score <= 75) return 'text-orange-600 bg-orange-100 dark:bg-orange-900/30'
        return 'text-red-600 bg-red-100 dark:bg-red-900/30'
    }

    const scoreColor = getScoreColor(score)

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-surface-600 dark:text-surface-400">
                        {icon}
                        <span>{title}</span>
                    </div>
                    <span className={`text-sm font-semibold px-2 py-0.5 rounded ${scoreColor}`}>
                        {score}/100
                    </span>
                </div>
            </CardHeader>
            <CardBody>
                <p className="font-medium">{detail}</p>
                <p className="text-sm text-surface-500 mt-1">{subdetail}</p>
            </CardBody>
        </Card>
    )
}
