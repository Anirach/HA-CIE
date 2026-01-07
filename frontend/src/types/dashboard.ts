/**
 * Type definitions for Dashboard.
 */

export interface DomainScore {
  part: string;
  name: string;
  score: number;
  weight: number;
  color: string;
  chapter_count: number;
}

export interface CriticalGap {
  criterion_id: string;
  criterion_name: string;
  chapter_id: string;
  chapter_name: string;
  score: number;
  category: 'essential' | 'core' | 'basic';
  priority: 'critical' | 'high' | 'medium';
}

export interface DashboardData {
  hospital_id: string;
  hospital_name: string;
  latest_assessment_id: string | null;
  latest_assessment_date: string | null;
  overall_maturity_score: number | null;
  previous_score: number | null;
  score_change: number | null;
  accreditation_level: string | null;
  target_level: string;
  domain_scores: DomainScore[];
  total_criteria: number;
  criteria_assessed: number;
  compliance_percentage: number;
  essential_met: number;
  essential_total: number;
  core_met: number;
  core_total: number;
  basic_met: number;
  basic_total: number;
  assessment_count: number;
  critical_gaps: CriticalGap[];
}

export interface TrendPoint {
  date: string;
  value: number;
}

export interface ChapterTrend {
  chapter_id: string;
  chapter_name: string;
  scores: Array<{ date: string; score: number }>;
  current_score: number;
  change: number | null;
}

export interface DashboardTrends {
  assessments: Array<{
    id: string;
    date: string;
    cycle: string;
    overall_score: number;
    level: string;
    part_scores: Record<string, number>;
  }>;
  trends: {
    overall: TrendPoint[];
    part_I: TrendPoint[];
    part_II: TrendPoint[];
    part_III: TrendPoint[];
    part_IV: TrendPoint[];
  };
  improvement: number | null;
  assessment_count: number;
  chapter_trends: ChapterTrend[];
}

export interface HospitalSummary {
  id: string;
  name: string;
  name_th: string | null;
  bed_count: number;
  hospital_type: string;
  region: string;
  ownership: string;
  current_accreditation_level: string | null;
  latest_assessment_date: string | null;
  latest_maturity_score: number | null;
  assessment_count: number;
}


