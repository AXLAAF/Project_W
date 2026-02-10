import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { FileText, Clock, CheckCircle, XCircle, AlertCircle, Trash2 } from 'lucide-react'
import { internshipsApi, Application } from '@/api/internships'
import { Card, CardHeader, CardBody, Badge, Button } from '@/components/ui'
import { PageLoader } from '@/components/shared/LoadingSpinner'

export default function MyApplicationsPage() {
    const queryClient = useQueryClient()

    const { data: applications, isLoading } = useQuery({
        queryKey: ['myApplications'],
        queryFn: () => internshipsApi.getMyApplications(),
    })

    const cancelMutation = useMutation({
        mutationFn: internshipsApi.cancelApplication,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['myApplications'] })
        },
    })

    if (isLoading) {
        return <PageLoader label="Cargando tus solicitudes..." />
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div>
                <h1 className="text-2xl font-bold">Mis Solicitudes</h1>
                <p className="text-surface-500 mt-1">Estado de tus solicitudes de prácticas</p>
            </div>

            {applications?.length === 0 ? (
                <div className="text-center py-12">
                    <FileText className="w-12 h-12 mx-auto text-surface-300" />
                    <p className="mt-4 text-surface-500">No tienes solicitudes pendientes</p>
                    <Button variant="primary" className="mt-4">
                        Explorar Plazas
                    </Button>
                </div>
            ) : (
                <div className="space-y-4">
                    {applications?.map((application) => (
                        <ApplicationCard
                            key={application.id}
                            application={application}
                            onCancel={() => cancelMutation.mutate(application.id)}
                            isCancelling={cancelMutation.isPending}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

function ApplicationCard({
    application,
    onCancel,
    isCancelling,
}: {
    application: Application
    onCancel: () => void
    isCancelling: boolean
}) {
    const statusConfig = {
        PENDING: { label: 'Pendiente', variant: 'warning', icon: Clock },
        UNDER_REVIEW: { label: 'En Revisión', variant: 'info', icon: AlertCircle },
        APPROVED: { label: 'Aprobada', variant: 'success', icon: CheckCircle },
        REJECTED: { label: 'Rechazada', variant: 'error', icon: XCircle },
        CANCELLED: { label: 'Cancelada', variant: 'error', icon: XCircle },
    } as const

    const status = statusConfig[application.status]
    const StatusIcon = status.icon
    const canCancel = ['PENDING', 'UNDER_REVIEW'].includes(application.status)

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="font-semibold">{application.position?.title}</h3>
                        <p className="text-sm text-surface-500 mt-1">
                            Enviada el {new Date(application.appliedAt).toLocaleDateString('es-MX')}
                        </p>
                    </div>
                    <Badge variant={status.variant as any}>
                        <StatusIcon className="w-3 h-3 mr-1" />
                        {status.label}
                    </Badge>
                </div>
            </CardHeader>
            <CardBody>
                {application.reviewerNotes && (
                    <div className="mb-4 p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
                        <p className="text-sm font-medium mb-1">Notas del revisor:</p>
                        <p className="text-sm text-surface-600 dark:text-surface-400">
                            {application.reviewerNotes}
                        </p>
                    </div>
                )}
                <div className="flex gap-2">
                    <Button variant="secondary" size="sm">
                        Ver Detalles
                    </Button>
                    {canCancel && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={onCancel}
                            disabled={isCancelling}
                            className="text-error-600"
                        >
                            <Trash2 className="w-4 h-4 mr-1" />
                            Cancelar
                        </Button>
                    )}
                </div>
            </CardBody>
        </Card>
    )
}
