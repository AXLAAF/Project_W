/**
 * API client for Reservations module
 */
import { apiClient } from './client';

// ========== Types ==========

export type ResourceType =
    | 'SALA_CONFERENCIAS'
    | 'LABORATORIO'
    | 'AUDITORIO'
    | 'SALA_ESTUDIO'
    | 'EQUIPO'
    | 'VEHICULO'
    | 'OTRO';

export type ResourceStatus = 'DISPONIBLE' | 'MANTENIMIENTO' | 'FUERA_SERVICIO';

export type ReservationStatus =
    | 'PENDING'
    | 'APPROVED'
    | 'REJECTED'
    | 'CANCELLED'
    | 'COMPLETED'
    | 'NO_SHOW';

export interface Resource {
    id: number;
    name: string;
    code: string;
    description?: string;
    resourceType: ResourceType;
    location?: string;
    building?: string;
    floor?: string;
    capacity?: number;
    features?: string;
    status: ResourceStatus;
    isActive: boolean;
    imageUrl?: string;
    minReservationMinutes: number;
    maxReservationMinutes: number;
    advanceBookingDays: number;
    requiresApproval: boolean;
    responsibleUserId?: number;
    createdAt: string;
    updatedAt: string;
}

export interface ResourceListItem {
    id: number;
    name: string;
    code: string;
    resourceType: ResourceType;
    location?: string;
    capacity?: number;
    status: ResourceStatus;
    isActive: boolean;
    imageUrl?: string;
}

export interface Reservation {
    id: number;
    resourceId: number;
    userId: number;
    startTime: string;
    endTime: string;
    title: string;
    description?: string;
    attendeesCount?: number;
    status: ReservationStatus;
    approvedById?: number;
    approvedAt?: string;
    rejectionReason?: string;
    checkedInAt?: string;
    checkedOutAt?: string;
    isRecurring: boolean;
    createdAt: string;
    updatedAt: string;
    resource?: ResourceListItem;
}

export interface ReservationCalendarItem {
    id: number;
    resourceId: number;
    startTime: string;
    endTime: string;
    title: string;
    status: ReservationStatus;
}

// ========== Transform functions ==========

const transformResource = (data: Record<string, unknown>): Resource => ({
    id: data.id as number,
    name: data.name as string,
    code: data.code as string,
    description: data.description as string | undefined,
    resourceType: data.resource_type as ResourceType,
    location: data.location as string | undefined,
    building: data.building as string | undefined,
    floor: data.floor as string | undefined,
    capacity: data.capacity as number | undefined,
    features: data.features as string | undefined,
    status: data.status as ResourceStatus,
    isActive: data.is_active as boolean,
    imageUrl: data.image_url as string | undefined,
    minReservationMinutes: data.min_reservation_minutes as number,
    maxReservationMinutes: data.max_reservation_minutes as number,
    advanceBookingDays: data.advance_booking_days as number,
    requiresApproval: data.requires_approval as boolean,
    responsibleUserId: data.responsible_user_id as number | undefined,
    createdAt: data.created_at as string,
    updatedAt: data.updated_at as string,
});

const transformResourceListItem = (data: Record<string, unknown>): ResourceListItem => ({
    id: data.id as number,
    name: data.name as string,
    code: data.code as string,
    resourceType: data.resource_type as ResourceType,
    location: data.location as string | undefined,
    capacity: data.capacity as number | undefined,
    status: data.status as ResourceStatus,
    isActive: data.is_active as boolean,
    imageUrl: data.image_url as string | undefined,
});

const transformReservation = (data: Record<string, unknown>): Reservation => ({
    id: data.id as number,
    resourceId: data.resource_id as number,
    userId: data.user_id as number,
    startTime: data.start_time as string,
    endTime: data.end_time as string,
    title: data.title as string,
    description: data.description as string | undefined,
    attendeesCount: data.attendees_count as number | undefined,
    status: data.status as ReservationStatus,
    approvedById: data.approved_by_id as number | undefined,
    approvedAt: data.approved_at as string | undefined,
    rejectionReason: data.rejection_reason as string | undefined,
    checkedInAt: data.checked_in_at as string | undefined,
    checkedOutAt: data.checked_out_at as string | undefined,
    isRecurring: data.is_recurring as boolean,
    createdAt: data.created_at as string,
    updatedAt: data.updated_at as string,
    resource: data.resource ? transformResourceListItem(data.resource as Record<string, unknown>) : undefined,
});

const transformCalendarItem = (data: Record<string, unknown>): ReservationCalendarItem => ({
    id: data.id as number,
    resourceId: data.resource_id as number,
    startTime: data.start_time as string,
    endTime: data.end_time as string,
    title: data.title as string,
    status: data.status as ReservationStatus,
});

// ========== API Functions ==========

// Resources
export const getResources = async (params?: {
    resourceType?: ResourceType;
    status?: ResourceStatus;
    building?: string;
    search?: string;
}): Promise<ResourceListItem[]> => {
    const response = await apiClient.get('/resources', { params });
    return (response.data as Record<string, unknown>[]).map(transformResourceListItem);
};

export const getResource = async (id: number): Promise<Resource> => {
    const response = await apiClient.get(`/resources/${id}`);
    return transformResource(response.data as Record<string, unknown>);
};

export const getBuildings = async (): Promise<string[]> => {
    const response = await apiClient.get('/resources/buildings');
    return response.data as string[];
};

// Reservations
export const createReservation = async (data: {
    resourceId: number;
    startTime: string;
    endTime: string;
    title: string;
    description?: string;
    attendeesCount?: number;
}): Promise<Reservation> => {
    const response = await apiClient.post('/reservations', {
        resource_id: data.resourceId,
        start_time: data.startTime,
        end_time: data.endTime,
        title: data.title,
        description: data.description,
        attendees_count: data.attendeesCount,
    });
    return transformReservation(response.data as Record<string, unknown>);
};

export const getMyReservations = async (params?: {
    status?: ReservationStatus;
    upcomingOnly?: boolean;
}): Promise<Reservation[]> => {
    const response = await apiClient.get('/reservations/my-reservations', {
        params: {
            status: params?.status,
            upcoming_only: params?.upcomingOnly,
        },
    });
    return (response.data as Record<string, unknown>[]).map(transformReservation);
};

export const getResourceCalendar = async (
    resourceId: number,
    startDate: string,
    endDate: string
): Promise<ReservationCalendarItem[]> => {
    const response = await apiClient.get(`/reservations/calendar/${resourceId}`, {
        params: { start_date: startDate, end_date: endDate },
    });
    return (response.data as Record<string, unknown>[]).map(transformCalendarItem);
};

export const cancelReservation = async (id: number): Promise<void> => {
    await apiClient.delete(`/reservations/${id}`);
};

export const checkIn = async (id: number): Promise<Reservation> => {
    const response = await apiClient.post(`/reservations/${id}/check-in`);
    return transformReservation(response.data as Record<string, unknown>);
};

export const checkOut = async (id: number): Promise<Reservation> => {
    const response = await apiClient.post(`/reservations/${id}/check-out`);
    return transformReservation(response.data as Record<string, unknown>);
};

// Resource type labels for display
export const resourceTypeLabels: Record<ResourceType, string> = {
    SALA_CONFERENCIAS: 'Sala de Conferencias',
    LABORATORIO: 'Laboratorio',
    AUDITORIO: 'Auditorio',
    SALA_ESTUDIO: 'Sala de Estudio',
    EQUIPO: 'Equipo',
    VEHICULO: 'Vehículo',
    OTRO: 'Otro',
};

export const resourceStatusLabels: Record<ResourceStatus, string> = {
    DISPONIBLE: 'Disponible',
    MANTENIMIENTO: 'En Mantenimiento',
    FUERA_SERVICIO: 'Fuera de Servicio',
};

export const reservationStatusLabels: Record<ReservationStatus, string> = {
    PENDING: 'Pendiente',
    APPROVED: 'Aprobada',
    REJECTED: 'Rechazada',
    CANCELLED: 'Cancelada',
    COMPLETED: 'Completada',
    NO_SHOW: 'No asistió',
};
