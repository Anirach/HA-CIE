/**
 * Dashboard API functions.
 */
import { apiClient } from './client';
import type { DashboardData, DashboardTrends, HospitalSummary } from '../types/dashboard';

/**
 * Get all hospitals.
 */
export async function getHospitals(): Promise<HospitalSummary[]> {
  const response = await apiClient.get<HospitalSummary[]>('/api/v1/hospitals');
  return response.data;
}

/**
 * Get dashboard data for a hospital.
 */
export async function getDashboard(hospitalId: string): Promise<DashboardData> {
  const response = await apiClient.get<DashboardData>(`/api/v1/dashboard/${hospitalId}`);
  return response.data;
}

/**
 * Get dashboard trends for charts.
 */
export async function getDashboardTrends(hospitalId: string): Promise<DashboardTrends> {
  const response = await apiClient.get<DashboardTrends>(`/api/v1/dashboard/${hospitalId}/trends`);
  return response.data;
}

/**
 * Get detailed domain data.
 */
export async function getDomainDetail(hospitalId: string, partNumber: string) {
  const response = await apiClient.get(`/api/v1/dashboard/${hospitalId}/domain/${partNumber}`);
  return response.data;
}

