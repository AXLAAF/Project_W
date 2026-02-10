import { useQuery } from '@tanstack/react-query'
import { BookOpen, TrendingUp, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { planningApi } from '@/api/planning'
import { Card, CardHeader, CardBody, Badge } from '@/components/ui'
import { PageLoader } from '@/components/shared/LoadingSpinner'

export default function HistoryPage() {
    const { data: history, isLoading } = useQuery({
        queryKey: ['academicHistory'],
        queryFn: planningApi.getAcademicHistory,
    })

    if (isLoading) {
        return <PageLoader label="Cargando historial académico..." />
    }

    if (!history) {
        return <div>Error al cargar historial</div>
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">Historial Académico</h1>
                <p className="text-surface-500 mt-1">Tu progreso académico y calificaciones</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <SummaryCard
                    title="Promedio (GPA)"
                    value={history.gpa.toFixed(2)}
                    icon={<TrendingUp className="w-6 h-6" />}
                    color="blue"
                />
                <SummaryCard
                    title="Créditos Aprobados"
                    value={`${history.totalCreditsEarned}`}
                    subtitle={`de ${history.totalCreditsAttempted} cursados`}
                    icon={<CheckCircle className="w-6 h-6" />}
                    color="green"
                />
                <SummaryCard
                    title="Materias Aprobadas"
                    value={history.subjectsPassed.toString()}
                    icon={<BookOpen className="w-6 h-6" />}
                    color="teal"
                />
                <SummaryCard
                    title="En Curso"
                    value={history.subjectsInProgress.toString()}
                    icon={<AlertTriangle className="w-6 h-6" />}
                    color="amber"
                />
            </div>

            {/* Current Enrollments */}
            {history.currentEnrollments.length > 0 && (
                <Card>
                    <CardHeader>Inscripciones Actuales</CardHeader>
                    <CardBody className="p-0">
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-surface-50 dark:bg-surface-800">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                            Materia
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                            Grupo
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                            Créditos
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                            Estado
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
                                    {history.currentEnrollments.map((item) => (
                                        <tr key={item.enrollmentId}>
                                            <td className="px-4 py-3">
                                                <div>
                                                    <span className="text-xs text-primary-600">{item.subject.code}</span>
                                                    <p className="font-medium">{item.subject.name}</p>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3 text-sm">{item.groupNumber}</td>
                                            <td className="px-4 py-3 text-sm">{item.subject.credits}</td>
                                            <td className="px-4 py-3">
                                                <Badge variant="info">En curso</Badge>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardBody>
                </Card>
            )}

            {/* History */}
            <Card>
                <CardHeader>Historial de Materias</CardHeader>
                <CardBody className="p-0">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-surface-50 dark:bg-surface-800">
                                <tr>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                        Materia
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                        Periodo
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                        Calificación
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                        Estado
                                    </th>
                                    <th className="px-4 py-3 text-left text-xs font-medium text-surface-500 uppercase">
                                        Intento
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-surface-200 dark:divide-surface-700">
                                {history.history.map((item) => (
                                    <tr key={item.enrollmentId}>
                                        <td className="px-4 py-3">
                                            <div>
                                                <span className="text-xs text-primary-600">{item.subject.code}</span>
                                                <p className="font-medium">{item.subject.name}</p>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-sm">{item.period.name}</td>
                                        <td className="px-4 py-3">
                                            {item.grade ? (
                                                <div className="flex items-center gap-2">
                                                    <span className="font-semibold">{Number(item.grade).toFixed(1)}</span>
                                                    <span className="text-xs text-surface-500">({item.gradeLetter})</span>
                                                </div>
                                            ) : (
                                                <span className="text-surface-400">-</span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3">
                                            <StatusBadge status={item.status} />
                                        </td>
                                        <td className="px-4 py-3 text-sm">
                                            {item.attemptNumber > 1 && (
                                                <span className="text-amber-600">#{item.attemptNumber}</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardBody>
            </Card>
        </div>
    )
}

function SummaryCard({
    title,
    value,
    subtitle,
    icon,
    color,
}: {
    title: string
    value: string
    subtitle?: string
    icon: React.ReactNode
    color: string
}) {
    const colors: Record<string, string> = {
        blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
        green: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
        teal: 'bg-teal-100 text-teal-600 dark:bg-teal-900/30 dark:text-teal-400',
        amber: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
    }

    return (
        <Card padding="md">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm text-surface-500">{title}</p>
                    <p className="text-2xl font-bold mt-1">{value}</p>
                    {subtitle && <p className="text-xs text-surface-400 mt-1">{subtitle}</p>}
                </div>
                <div className={`p-3 rounded-full ${colors[color]}`}>{icon}</div>
            </div>
        </Card>
    )
}

function StatusBadge({ status }: { status: string }) {
    const config: Record<string, { variant: 'success' | 'danger' | 'warning' | 'default'; label: string }> = {
        PASSED: { variant: 'success', label: 'Aprobada' },
        FAILED: { variant: 'danger', label: 'Reprobada' },
        DROPPED: { variant: 'warning', label: 'Baja' },
        WITHDRAWN: { variant: 'default', label: 'NP' },
    }

    const { variant, label } = config[status] || { variant: 'default', label: status }
    return <Badge variant={variant}>{label}</Badge>
}
