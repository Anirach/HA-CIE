/**
 * Insights API client functions.
 */

import { apiClient } from './client';
import type {
  InsightsResponse,
  InsightCategoriesResponse,
  InsightsSummaryResponse,
  RiskAssessmentResponse,
  RecommendationsResponse,
} from '../types/insights';

/**
 * Get comprehensive AI insights for a hospital.
 */
export async function getInsights(hospitalId: string = 'hosp-001'): Promise<InsightsResponse> {
  const response = await apiClient.get('/api/v1/insights', {
    params: { hospital_id: hospitalId },
  });
  return response.data;
}

/**
 * Get available insight categories.
 */
export async function getInsightCategories(): Promise<InsightCategoriesResponse> {
  const response = await apiClient.get('/api/v1/insights/categories');
  return response.data;
}

/**
 * Get brief insights summary.
 */
export async function getInsightsSummary(hospitalId: string = 'hosp-001'): Promise<InsightsSummaryResponse> {
  const response = await apiClient.get('/api/v1/insights/summary', {
    params: { hospital_id: hospitalId },
  });
  return response.data;
}

/**
 * Get detailed risk assessment.
 */
export async function getRiskAssessment(hospitalId: string = 'hosp-001'): Promise<RiskAssessmentResponse> {
  const response = await apiClient.get('/api/v1/insights/risk-assessment', {
    params: { hospital_id: hospitalId },
  });
  return response.data;
}

/**
 * Get prioritized recommendations.
 */
export async function getRecommendations(
  hospitalId: string = 'hosp-001',
  limit: number = 10
): Promise<RecommendationsResponse> {
  const response = await apiClient.get('/api/v1/insights/recommendations', {
    params: { hospital_id: hospitalId, limit },
  });
  return response.data;
}


