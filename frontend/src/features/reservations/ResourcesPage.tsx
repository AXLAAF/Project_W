/**
 * Resources catalog page - browse available resources
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MapPin, Users, Search, Building, Filter } from 'lucide-react';

import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    Button,
    Badge,
    Input,
} from '@/components/ui';
import {
    getResources,
    getBuildings,
    ResourceListItem,
    ResourceType,
    ResourceStatus,
    resourceTypeLabels,
    resourceStatusLabels,
} from '@/api/reservations';

const resourceTypeColors: Record<ResourceType, string> = {
    SALA_CONFERENCIAS: 'bg-blue-100 text-blue-800',
    LABORATORIO: 'bg-purple-100 text-purple-800',
    AUDITORIO: 'bg-amber-100 text-amber-800',
    SALA_ESTUDIO: 'bg-green-100 text-green-800',
    EQUIPO: 'bg-red-100 text-red-800',
    VEHICULO: 'bg-gray-100 text-gray-800',
    OTRO: 'bg-slate-100 text-slate-800',
};

const statusColors: Record<ResourceStatus, string> = {
    DISPONIBLE: 'bg-green-100 text-green-800',
    MANTENIMIENTO: 'bg-yellow-100 text-yellow-800',
    FUERA_SERVICIO: 'bg-red-100 text-red-800',
};

export default function ResourcesPage() {
    const [search, setSearch] = useState('');
    const [selectedType, setSelectedType] = useState<ResourceType | ''>('');
    const [selectedBuilding, setSelectedBuilding] = useState('');

    const { data: resources = [], isLoading } = useQuery({
        queryKey: ['resources', search, selectedType, selectedBuilding],
        queryFn: () =>
            getResources({
                search: search || undefined,
                resourceType: selectedType || undefined,
                building: selectedBuilding || undefined,
            }),
    });

    const { data: buildings = [] } = useQuery({
        queryKey: ['buildings'],
        queryFn: getBuildings,
    });

    const ResourceCard = ({ resource }: { resource: ResourceListItem }) => (
        <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{resource.name}</CardTitle>
                    <Badge className={statusColors[resource.status]}>
                        {resourceStatusLabels[resource.status]}
                    </Badge>
                </div>
                <Badge className={resourceTypeColors[resource.resourceType]}>
                    {resourceTypeLabels[resource.resourceType]}
                </Badge>
            </CardHeader>
            <CardContent>
                <div className="space-y-2 text-sm text-gray-600">
                    {resource.location && (
                        <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span>{resource.location}</span>
                        </div>
                    )}
                    {resource.capacity && (
                        <div className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            <span>Capacidad: {resource.capacity} personas</span>
                        </div>
                    )}
                </div>
                <div className="mt-4">
                    <Button
                        size="sm"
                        className="w-full"
                        disabled={resource.status !== 'DISPONIBLE'}
                    >
                        Reservar
                    </Button>
                </div>
            </CardContent>
        </Card>
    );

    return (
        <div className="p-6 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold">Recursos Disponibles</h1>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-4">
                <div className="relative flex-1 min-w-[200px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                        placeholder="Buscar recursos..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="pl-10"
                    />
                </div>

                <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-gray-500" />
                    <select
                        value={selectedType}
                        onChange={(e) => setSelectedType(e.target.value as ResourceType | '')}
                        className="border rounded-md px-3 py-2 text-sm"
                    >
                        <option value="">Todos los tipos</option>
                        {Object.entries(resourceTypeLabels).map(([value, label]) => (
                            <option key={value} value={value}>
                                {label}
                            </option>
                        ))}
                    </select>
                </div>

                {buildings.length > 0 && (
                    <div className="flex items-center gap-2">
                        <Building className="h-4 w-4 text-gray-500" />
                        <select
                            value={selectedBuilding}
                            onChange={(e) => setSelectedBuilding(e.target.value)}
                            className="border rounded-md px-3 py-2 text-sm"
                        >
                            <option value="">Todos los edificios</option>
                            {buildings.map((building) => (
                                <option key={building} value={building}>
                                    {building}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            {/* Resources grid */}
            {isLoading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-gray-600">Cargando recursos...</p>
                </div>
            ) : resources.length === 0 ? (
                <div className="text-center py-12">
                    <p className="text-gray-600">No se encontraron recursos</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {resources.map((resource) => (
                        <ResourceCard key={resource.id} resource={resource} />
                    ))}
                </div>
            )}
        </div>
    );
}
