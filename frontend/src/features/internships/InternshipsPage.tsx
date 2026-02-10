import { useQuery } from '@tanstack/react-query'
import { Search, Building2, MapPin, Clock, Users, Briefcase, CheckCircle } from 'lucide-react'
import { useState } from 'react'
import { internshipsApi, Position } from '@/api/internships'
import { Card, CardHeader, CardBody, Input, Badge, Button } from '@/components/ui'
import { PageLoader } from '@/components/shared/LoadingSpinner'

export default function InternshipsPage() {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedModality, setSelectedModality] = useState<string | null>(null)
    const [onlyAvailable, setOnlyAvailable] = useState(true)

    const { data: positions, isLoading } = useQuery({
        queryKey: ['positions', selectedModality, searchQuery, onlyAvailable],
        queryFn: () => internshipsApi.getPositions({
            modality: selectedModality || undefined,
            search: searchQuery || undefined,
            onlyAvailable,
        }),
    })

    if (isLoading) {
        return <PageLoader label="Cargando plazas de prácticas..." />
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold">Prácticas Profesionales</h1>
                    <p className="text-surface-500 mt-1">Explora las oportunidades de prácticas disponibles</p>
                </div>
            </div>

            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                    <Input
                        placeholder="Buscar plazas por título..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        leftIcon={<Search className="w-5 h-5" />}
                    />
                </div>
                <div className="sm:w-48">
                    <select
                        value={selectedModality || ''}
                        onChange={(e) => setSelectedModality(e.target.value || null)}
                        className="input"
                    >
                        <option value="">Todas las modalidades</option>
                        <option value="PRESENCIAL">Presencial</option>
                        <option value="REMOTO">Remoto</option>
                        <option value="HIBRIDO">Híbrido</option>
                    </select>
                </div>
                <label className="flex items-center gap-2 text-sm">
                    <input
                        type="checkbox"
                        checked={onlyAvailable}
                        onChange={(e) => setOnlyAvailable(e.target.checked)}
                        className="rounded border-surface-300"
                    />
                    Solo disponibles
                </label>
            </div>

            {/* Position Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {positions?.map((position) => (
                    <PositionCard key={position.id} position={position} />
                ))}
            </div>

            {positions?.length === 0 && (
                <div className="text-center py-12">
                    <Briefcase className="w-12 h-12 mx-auto text-surface-300" />
                    <p className="mt-4 text-surface-500">No se encontraron plazas disponibles</p>
                </div>
            )}
        </div>
    )
}

function PositionCard({ position }: { position: Position }) {
    const availableSpots = position.capacity - position.filledCount

    const modalityColors = {
        PRESENCIAL: 'info',
        REMOTO: 'success',
        HIBRIDO: 'warning',
    } as const

    const modalityLabels = {
        PRESENCIAL: 'Presencial',
        REMOTO: 'Remoto',
        HIBRIDO: 'Híbrido',
    }

    return (
        <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        {position.company && (
                            <div className="flex items-center gap-2 mb-2">
                                <Building2 className="w-4 h-4 text-surface-400" />
                                <span className="text-xs font-medium text-primary-600 dark:text-primary-400">
                                    {position.company.name}
                                </span>
                                {position.company.isVerified && (
                                    <CheckCircle className="w-3 h-3 text-success-500" />
                                )}
                            </div>
                        )}
                        <h3 className="font-semibold line-clamp-2">{position.title}</h3>
                    </div>
                    <Badge variant={modalityColors[position.modality]}>
                        {modalityLabels[position.modality]}
                    </Badge>
                </div>
            </CardHeader>
            <CardBody>
                <p className="text-sm text-surface-600 dark:text-surface-400 line-clamp-3 mb-4">
                    {position.description}
                </p>
                <div className="space-y-2 text-sm text-surface-600 dark:text-surface-400">
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>{position.durationMonths} meses</span>
                    </div>
                    {position.location && (
                        <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            <span>{position.location}</span>
                        </div>
                    )}
                    <div className="flex items-center gap-2">
                        <Users className="w-4 h-4" />
                        <span>{availableSpots} lugares disponibles</span>
                    </div>
                </div>
                {(position.minGpa || position.minCredits) && (
                    <div className="mt-3 flex gap-2 flex-wrap">
                        {position.minGpa && (
                            <span className="text-xs px-2 py-1 rounded bg-surface-100 dark:bg-surface-800">
                                Promedio mín: {position.minGpa}
                            </span>
                        )}
                        {position.minCredits && (
                            <span className="text-xs px-2 py-1 rounded bg-surface-100 dark:bg-surface-800">
                                Créditos mín: {position.minCredits}
                            </span>
                        )}
                    </div>
                )}
                <div className="mt-4">
                    <Button variant="primary" size="sm" className="w-full">
                        Ver Detalles
                    </Button>
                </div>
            </CardBody>
        </Card>
    )
}
