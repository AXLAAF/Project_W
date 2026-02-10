import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Briefcase, Calendar, User, Mail, Phone, FileText, Plus, Send, Check } from 'lucide-react'
import { useState } from 'react'
import { internshipsApi, Internship } from '@/api/internships'
import { Card, CardHeader, CardBody, Badge, Button } from '@/components/ui'
import { PageLoader } from '@/components/shared/LoadingSpinner'

export default function ActiveInternshipPage() {
    const { data: internship, isLoading } = useQuery({
        queryKey: ['activeInternship'],
        queryFn: internshipsApi.getActiveInternship,
    })

    if (isLoading) {
        return <PageLoader label="Cargando información de tu práctica..." />
    }

    if (!internship) {
        return (
            <div className="space-y-6 animate-fade-in">
                <div>
                    <h1 className="text-2xl font-bold">Mi Práctica Profesional</h1>
                </div>
                <div className="text-center py-12">
                    <Briefcase className="w-12 h-12 mx-auto text-surface-300" />
                    <p className="mt-4 text-surface-500">No tienes una práctica activa actualmente</p>
                    <Button variant="primary" className="mt-4">
                        Explorar Oportunidades
                    </Button>
                </div>
            </div>
        )
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Mi Práctica Profesional</h1>
                    <p className="text-surface-500 mt-1">Gestiona tu práctica y reportes mensuales</p>
                </div>
                <Badge variant="success" className="text-sm">
                    <Check className="w-4 h-4 mr-1" />
                    Activa
                </Badge>
            </div>

            {/* Internship Details */}
            <Card>
                <CardHeader>
                    <h2 className="text-lg font-semibold">Información General</h2>
                </CardHeader>
                <CardBody>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <Calendar className="w-5 h-5 text-surface-400" />
                                <div>
                                    <p className="text-sm text-surface-500">Periodo</p>
                                    <p className="font-medium">
                                        {new Date(internship.startDate).toLocaleDateString('es-MX')} -{' '}
                                        {new Date(internship.expectedEndDate).toLocaleDateString('es-MX')}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <FileText className="w-5 h-5 text-surface-400" />
                                <div>
                                    <p className="text-sm text-surface-500">Horas Totales</p>
                                    <p className="font-medium">{internship.totalHours} horas</p>
                                </div>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="flex items-center gap-3">
                                <User className="w-5 h-5 text-surface-400" />
                                <div>
                                    <p className="text-sm text-surface-500">Supervisor</p>
                                    <p className="font-medium">{internship.supervisorName}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <Mail className="w-5 h-5 text-surface-400" />
                                <div>
                                    <p className="text-sm text-surface-500">Correo</p>
                                    <p className="font-medium">{internship.supervisorEmail}</p>
                                </div>
                            </div>
                            {internship.supervisorPhone && (
                                <div className="flex items-center gap-3">
                                    <Phone className="w-5 h-5 text-surface-400" />
                                    <div>
                                        <p className="text-sm text-surface-500">Teléfono</p>
                                        <p className="font-medium">{internship.supervisorPhone}</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </CardBody>
            </Card>

            {/* Monthly Reports */}
            <ReportsSection internship={internship} />
        </div>
    )
}

function ReportsSection({ internship }: { internship: Internship }) {
    const queryClient = useQueryClient()
    const [showNewReport, setShowNewReport] = useState(false)

    const { data: reports, isLoading } = useQuery({
        queryKey: ['internshipReports', internship.id],
        queryFn: () => internshipsApi.getReports(internship.id),
    })

    const submitMutation = useMutation({
        mutationFn: ({ reportId }: { reportId: number }) =>
            internshipsApi.submitReport(internship.id, reportId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['internshipReports', internship.id] })
        },
    })

    if (isLoading) {
        return <div>Cargando reportes...</div>
    }

    const statusConfig = {
        DRAFT: { label: 'Borrador', variant: 'warning' },
        SUBMITTED: { label: 'Enviado', variant: 'info' },
        APPROVED: { label: 'Aprobado', variant: 'success' },
        REVISION_NEEDED: { label: 'Requiere Revisión', variant: 'error' },
    } as const

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Reportes Mensuales</h2>
                    <Button variant="secondary" size="sm" onClick={() => setShowNewReport(!showNewReport)}>
                        <Plus className="w-4 h-4 mr-1" />
                        Nuevo Reporte
                    </Button>
                </div>
            </CardHeader>
            <CardBody>
                {reports?.length === 0 ? (
                    <p className="text-center text-surface-500 py-6">
                        No hay reportes aún. Crea tu primer reporte mensual.
                    </p>
                ) : (
                    <div className="space-y-3">
                        {reports?.map((report) => {
                            const status = statusConfig[report.status]
                            return (
                                <div
                                    key={report.id}
                                    className="flex items-center justify-between p-4 bg-surface-50 dark:bg-surface-800 rounded-lg"
                                >
                                    <div>
                                        <p className="font-medium">Mes {report.monthNumber}</p>
                                        <p className="text-sm text-surface-500">
                                            {report.hoursWorked} horas trabajadas
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Badge variant={status.variant as any}>{status.label}</Badge>
                                        {report.status === 'DRAFT' && (
                                            <Button
                                                variant="primary"
                                                size="sm"
                                                onClick={() => submitMutation.mutate({ reportId: report.id })}
                                                disabled={submitMutation.isPending}
                                            >
                                                <Send className="w-4 h-4 mr-1" />
                                                Enviar
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}
            </CardBody>
        </Card>
    )
}
