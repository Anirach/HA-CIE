/**
 * Graph API functions.
 */
import { apiClient } from './client';
import type {
  GraphData,
  PartSummary,
  ChapterDetail,
  CausalRelationship,
  Criterion,
  GraphStatistics,
  RelationshipDetail,
} from '../types/graph';

/**
 * Get the standards graph data for Cytoscape.js visualization.
 */
export async function getStandardsGraph(): Promise<GraphData> {
  const response = await apiClient.get<GraphData>('/api/v1/graph/standards');
  return response.data;
}

/**
 * Get all standard parts.
 */
export async function getParts(): Promise<PartSummary[]> {
  const response = await apiClient.get<PartSummary[]>('/api/v1/graph/parts');
  return response.data;
}

/**
 * Get detailed chapter information.
 */
export async function getChapterDetail(chapterId: string): Promise<ChapterDetail> {
  const response = await apiClient.get<ChapterDetail>(`/api/v1/graph/chapters/${chapterId}`);
  return response.data;
}

/**
 * Get all causal relationships with optional filtering.
 */
export async function getRelationships(params?: {
  source?: string;
  target?: string;
  relationship_type?: string;
  min_strength?: number;
}): Promise<CausalRelationship[]> {
  const response = await apiClient.get<CausalRelationship[]>('/api/v1/graph/relationships', {
    params,
  });
  return response.data;
}

/**
 * Get relationship detail between two chapters.
 */
export async function getRelationshipDetail(
  source: string,
  target: string
): Promise<RelationshipDetail> {
  const response = await apiClient.get<RelationshipDetail>(
    `/api/v1/graph/relationships/${source}/${target}`
  );
  return response.data;
}

/**
 * Get criteria with optional filtering.
 */
export async function getCriteria(params?: {
  chapter?: string;
  category?: 'essential' | 'core' | 'basic';
}): Promise<Criterion[]> {
  const response = await apiClient.get<Criterion[]>('/api/v1/graph/criteria', { params });
  return response.data;
}

/**
 * Get graph statistics.
 */
export async function getGraphStatistics(): Promise<GraphStatistics> {
  const response = await apiClient.get<GraphStatistics>('/api/v1/graph/statistics');
  return response.data;
}

