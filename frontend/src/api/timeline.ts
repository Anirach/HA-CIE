/**
 * Timeline API client functions.
 */

import { apiClient } from './client';
import type {
  SnapshotSummary,
  SnapshotDetail,
  SnapshotComparison,
  ChapterHistory,
} from '../types/timeline';

/**
 * Get all available timeline snapshots.
 */
export async function getSnapshots(): Promise<{
  snapshots: SnapshotSummary[];
  total: number;
}> {
  const response = await apiClient.get('/api/v1/timeline/snapshots');
  return response.data;
}

/**
 * Get a specific snapshot by index.
 */
export async function getSnapshot(index: number): Promise<SnapshotDetail> {
  const response = await apiClient.get(`/api/v1/timeline/snapshots/${index}`);
  return response.data;
}

/**
 * Compare two snapshots.
 */
export async function compareSnapshots(
  fromIndex: number,
  toIndex: number
): Promise<SnapshotComparison> {
  const response = await apiClient.get('/api/v1/timeline/compare', {
    params: {
      from_index: fromIndex,
      to_index: toIndex,
    },
  });
  return response.data;
}

/**
 * Get chapter history across all snapshots.
 */
export async function getChapterHistory(
  chapterId: string
): Promise<ChapterHistory> {
  const response = await apiClient.get(
    `/api/v1/timeline/chapters/${chapterId}/history`
  );
  return response.data;
}

/**
 * Get the latest snapshot.
 */
export async function getLatestSnapshot(): Promise<SnapshotDetail> {
  const response = await apiClient.get('/api/v1/timeline/latest');
  return response.data;
}


