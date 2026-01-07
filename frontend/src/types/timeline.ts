/**
 * Timeline-related type definitions.
 */

export interface SnapshotSummary {
  id: string;
  index: number;
  date: string;
  label: string;
  overall_score: number;
  accreditation_level: string;
  summary: {
    improved: number;
    declined: number;
    unchanged: number;
  };
}

export interface SnapshotDetail {
  id: string;
  index: number;
  date: string;
  label: string;
  overall_score: number;
  accreditation_level: string;
  scores: Record<string, number>;
  changes: SnapshotChange[];
  summary: {
    improved: number;
    declined: number;
    unchanged: number;
  };
}

export interface SnapshotChange {
  chapter_id: string;
  chapter_name: string;
  previous_score: number;
  new_score: number;
  change: number;
  part: string;
}

export interface SnapshotComparison {
  from_snapshot: {
    id: string;
    date: string;
    label: string;
    overall_score: number;
  };
  to_snapshot: {
    id: string;
    date: string;
    label: string;
    overall_score: number;
  };
  overall_change: number;
  changes: ComparisonChange[];
  summary: {
    improved: number;
    declined: number;
    unchanged: number;
  };
}

export interface ComparisonChange {
  chapter_id: string;
  chapter_name: string;
  part: string;
  from_score: number;
  to_score: number;
  change: number;
  change_percent: number;
}

export interface ChapterHistory {
  chapter_id: string;
  chapter_name: string;
  part: string;
  history: ChapterHistoryPoint[];
  trend: 'improving' | 'declining' | 'stable';
  total_change: number;
}

export interface ChapterHistoryPoint {
  date: string;
  label: string;
  score: number;
  overall: number;
}

