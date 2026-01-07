/**
 * ISQua EEA API functions.
 */
import { apiClient } from './client';
import type {
  ISQuaPrinciple,
  HAMapping,
  ISQuaAssessment,
  PrincipleAssessment,
} from '../types/isqua';

export async function getISQuaPrinciples(): Promise<{ principles: ISQuaPrinciple[] }> {
  const response = await apiClient.get('/api/v1/isqua/principles');
  return response.data;
}

export async function getPrincipleDetails(principleId: string): Promise<ISQuaPrinciple> {
  const response = await apiClient.get(`/api/v1/isqua/principles/${principleId}`);
  return response.data;
}

export async function getHAToISQuaMapping(): Promise<{ mapping: Record<string, HAMapping> }> {
  const response = await apiClient.get('/api/v1/isqua/ha-mapping');
  return response.data;
}

export async function assessISQuaCompliance(
  haChapterScores: Record<string, number>
): Promise<ISQuaAssessment> {
  const response = await apiClient.post('/api/v1/isqua/assess', {
    ha_chapter_scores: haChapterScores,
  });
  return response.data;
}

export async function assessSinglePrinciple(
  principleId: string,
  haChapterScores: Record<string, number>
): Promise<PrincipleAssessment> {
  const response = await apiClient.post(`/api/v1/isqua/assess/${principleId}`, {
    ha_chapter_scores: haChapterScores,
  });
  return response.data;
}

export async function convertHAToISQua(haScore: number): Promise<{
  ha_score: number;
  isqua_rating: number;
  isqua_description: string;
}> {
  const response = await apiClient.get('/api/v1/isqua/convert/ha-to-isqua', {
    params: { ha_score: haScore },
  });
  return response.data;
}

export async function convertISQuaToHA(isquaRating: number): Promise<{
  isqua_rating: number;
  ha_score_approximate: number;
  ha_score_range: string;
}> {
  const response = await apiClient.get('/api/v1/isqua/convert/isqua-to-ha', {
    params: { isqua_rating: isquaRating },
  });
  return response.data;
}


