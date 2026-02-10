/**
 * My Reservations page - view and manage user's reservations
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Calendar, Clock, MapPin, X, LogIn, LogOut } from 'lucide-react';

import {
    Card,
    CardHeader,
    CardTitle,
    CardContent,
    Button,
    Badge,
} from '@/components/ui';
import {
    getMyReservations,
    cancelReservation,
    checkIn,
    checkOut,
    Reservation,
    ReservationStatus,
    reservationStatusLabels,
} from '@/api/reservations';

const statusColors: Record<ReservationStatus, string> = {
    PENDING: 'bg-yellow-100 text-yellow-800',
    APPROVED: 'bg-green-100 text-green-800',
    REJECTED: 'bg-red-100 text-red-800',
    CANCELLED: 'bg-gray-100 text-gray-800',
    COMPLETED: 'bg-blue-100 text-blue-800',
    NO_SHOW: 'bg-red-100 text-red-800',
};

export default function MyReservationsPage() {
    const queryClient = useQueryClient();

    const { data: reservations = [], isLoading } = useQuery({
        queryKey: ['my-reservations'],
        queryFn: () => getMyReservations({ upcomingOnly: false }),
    });

    const cancelMutation = useMutation({
        mutationFn: cancelReservation,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['my-reservations'] });
        },
    });

    const checkInMutation = useMutation({
        mutationFn: checkIn,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['my-reservations'] });
        },
    });

    const checkOutMutation = useMutation({
        mutationFn: checkOut,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['my-reservations'] });
        },
    });

    const formatDateTime = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('es-MX', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const canCancel = (reservation: Reservation) =>
        ['PENDING', 'APPROVED'].includes(reservation.status);

    const canCheckIn = (reservation: Reservation) =>
        reservation.status === 'APPROVED' && !reservation.checkedInAt;

    const canCheckOut = (reservation: Reservation) =>
        reservation.status === 'APPROVED' && reservation.checkedInAt && !reservation.checkedOutAt;

    const ReservationCard = ({ reservation }: { reservation: Reservation }) => (
        <Card className="mb-4">
            <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-lg">{reservation.title}</CardTitle>
                        {reservation.resource && (
                            <p className="text-sm text-gray-600">{reservation.resource.name}</p>
                        )}
                    </div>
                    <Badge className={statusColors[reservation.status]}>
                        {reservationStatusLabels[reservation.status]}
                    </Badge>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>{formatDateTime(reservation.startTime)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        <span>Hasta: {formatDateTime(reservation.endTime)}</span>
                    </div>
                    {reservation.resource?.location && (
                        <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4" />
                            <span>{reservation.resource.location}</span>
                        </div>
                    )}
                </div>

                {reservation.rejectionReason && (
                    <div className="bg-red-50 border border-red-200 rounded-md p-2 mb-4 text-sm text-red-700">
                        <strong>Motivo de rechazo:</strong> {reservation.rejectionReason}
                    </div>
                )}

                <div className="flex gap-2 flex-wrap">
                    {canCheckIn(reservation) && (
                        <Button
                            size="sm"
                            onClick={() => checkInMutation.mutate(reservation.id)}
                            disabled={checkInMutation.isPending}
                        >
                            <LogIn className="h-4 w-4 mr-1" />
                            Check-in
                        </Button>
                    )}

                    {canCheckOut(reservation) && (
                        <Button
                            size="sm"
                            onClick={() => checkOutMutation.mutate(reservation.id)}
                            disabled={checkOutMutation.isPending}
                        >
                            <LogOut className="h-4 w-4 mr-1" />
                            Check-out
                        </Button>
                    )}

                    {canCancel(reservation) && (
                        <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => {
                                if (confirm('¿Estás seguro de cancelar esta reservación?')) {
                                    cancelMutation.mutate(reservation.id);
                                }
                            }}
                            disabled={cancelMutation.isPending}
                        >
                            <X className="h-4 w-4 mr-1" />
                            Cancelar
                        </Button>
                    )}
                </div>
            </CardContent>
        </Card>
    );

    return (
        <div className="p-6 space-y-6">
            <h1 className="text-2xl font-bold">Mis Reservaciones</h1>

            {isLoading ? (
                <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-gray-600">Cargando reservaciones...</p>
                </div>
            ) : reservations.length === 0 ? (
                <div className="text-center py-12">
                    <Calendar className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No tienes reservaciones</p>
                    <Button className="mt-4" onClick={() => window.location.href = '/reservations'}>
                        Explorar recursos
                    </Button>
                </div>
            ) : (
                <div className="max-w-2xl">
                    {reservations.map((reservation) => (
                        <ReservationCard key={reservation.id} reservation={reservation} />
                    ))}
                </div>
            )}
        </div>
    );
}
