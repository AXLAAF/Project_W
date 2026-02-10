import { useQuery } from '@tanstack/react-query'
import { Search, Filter, BookOpen, Clock, Users } from 'lucide-react'
import { useState } from 'react'
import { planningApi, Subject } from '@/api/planning'
import { Card, CardHeader, CardBody, Input, Badge } from '@/components/ui'
import { PageLoader } from '@/components/shared/LoadingSpinner'

export default function PlanningPage() {
    const [searchQuery, setSearchQuery] = useState('')
    const [selectedDepartment, setSelectedDepartment] = useState<string | null>(null)

    const { data: subjects, isLoading: subjectsLoading } = useQuery({
        queryKey: ['subjects', selectedDepartment],
        queryFn: () => planningApi.getSubjects({ department: selectedDepartment || undefined }),
    })

    const { data: departments } = useQuery({
        queryKey: ['departments'],
        queryFn: planningApi.getDepartments,
    })

    const { data: searchResults, isLoading: searchLoading } = useQuery({
        queryKey: ['subjectSearch', searchQuery],
        queryFn: () => planningApi.searchSubjects(searchQuery),
        enabled: searchQuery.length >= 2,
    })

    const displaySubjects = searchQuery.length >= 2 ? searchResults : subjects

    if (subjectsLoading) {
        return <PageLoader label="Cargando catálogo de materias..." />
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold">Planeación de Materias</h1>
                    <p className="text-surface-500 mt-1">Explora el catálogo y planifica tu próximo semestre</p>
                </div>
            </div>

            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                    <Input
                        placeholder="Buscar materias por nombre o código..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        leftIcon={<Search className="w-5 h-5" />}
                    />
                </div>
                <div className="sm:w-64">
                    <select
                        value={selectedDepartment || ''}
                        onChange={(e) => setSelectedDepartment(e.target.value || null)}
                        className="input"
                    >
                        <option value="">Todos los departamentos</option>
                        {departments?.map((dept) => (
                            <option key={dept} value={dept}>
                                {dept}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Subject Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {displaySubjects?.map((subject) => (
                    <SubjectCard key={subject.id} subject={subject} />
                ))}
            </div>

            {displaySubjects?.length === 0 && (
                <div className="text-center py-12">
                    <BookOpen className="w-12 h-12 mx-auto text-surface-300" />
                    <p className="mt-4 text-surface-500">No se encontraron materias</p>
                </div>
            )}
        </div>
    )
}

function SubjectCard({ subject }: { subject: Subject }) {
    return (
        <Card className="hover:shadow-md transition-shadow">
            <CardHeader>
                <div className="flex items-start justify-between">
                    <div>
                        <span className="text-xs font-medium text-primary-600 dark:text-primary-400">
                            {subject.code}
                        </span>
                        <h3 className="font-semibold mt-1 line-clamp-2">{subject.name}</h3>
                    </div>
                    <Badge variant="info">{subject.credits} créditos</Badge>
                </div>
            </CardHeader>
            <CardBody>
                <div className="space-y-2 text-sm text-surface-600 dark:text-surface-400">
                    <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        <span>{subject.totalHours} horas totales</span>
                    </div>
                    {subject.department && (
                        <div className="flex items-center gap-2">
                            <Filter className="w-4 h-4" />
                            <span>{subject.department}</span>
                        </div>
                    )}
                    {subject.semesterSuggested && (
                        <div className="flex items-center gap-2">
                            <Users className="w-4 h-4" />
                            <span>Semestre {subject.semesterSuggested}</span>
                        </div>
                    )}
                </div>
                <div className="mt-4 flex gap-2">
                    <span className="text-xs px-2 py-1 rounded bg-surface-100 dark:bg-surface-800">
                        Teoría: {subject.hoursTheory}h
                    </span>
                    <span className="text-xs px-2 py-1 rounded bg-surface-100 dark:bg-surface-800">
                        Práctica: {subject.hoursPractice}h
                    </span>
                    {subject.hoursLab > 0 && (
                        <span className="text-xs px-2 py-1 rounded bg-surface-100 dark:bg-surface-800">
                            Lab: {subject.hoursLab}h
                        </span>
                    )}
                </div>
            </CardBody>
        </Card>
    )
}
