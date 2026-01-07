/**
 * Digital Health API functions.
 */
import { apiClient } from './client';
import type {
  DISAHFramework,
  CategoryDetails,
  DigitalHealthAssessment,
  HAAlignment,
} from '../types/digital-health';

export async function getDISAHFramework(): Promise<DISAHFramework> {
  const response = await apiClient.get('/api/v1/digital-health/framework');
  return response.data;
}

export async function getCategoryDetails(categoryId: string): Promise<CategoryDetails> {
  const response = await apiClient.get(`/api/v1/digital-health/categories/${categoryId}`);
  return response.data;
}

export async function assessReadiness(
  hospitalId: string,
  assessments: Record<string, string>
): Promise<DigitalHealthAssessment> {
  const response = await apiClient.post('/api/v1/digital-health/assess', {
    hospital_id: hospitalId,
    assessments,
  });
  return response.data;
}

export async function getHospitalAssessment(
  hospitalId: string
): Promise<DigitalHealthAssessment> {
  const response = await apiClient.get(`/api/v1/digital-health/assessment/${hospitalId}`);
  return response.data;
}

export async function getHAAlignment(): Promise<{ alignments: HAAlignment[] }> {
  const response = await apiClient.get('/api/v1/digital-health/ha-alignment');
  return response.data;
}

export async function getReadinessLevels(): Promise<{
  levels: Array<{
    id: string;
    name: string;
    score: number;
    description: string;
  }>;
}> {
  const response = await apiClient.get('/api/v1/digital-health/readiness-levels');
  return response.data;
}


