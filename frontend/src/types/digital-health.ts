/**
 * Types for WHO DISAH Digital Health framework.
 */

export type ReadinessLevel =
  | 'not_started'
  | 'planning'
  | 'pilot'
  | 'partial_implementation'
  | 'full_implementation'
  | 'optimizing';

export interface Intervention {
  id: string;
  name: string;
  description: string;
  critical: boolean;
  weight: number;
}

export interface DISAHCategory {
  id: string;
  name: string;
  description: string;
  ha_mapping: string[];
  intervention_count: number;
  critical_count: number;
}

export interface DISAHFramework {
  categories: DISAHCategory[];
  total_interventions: number;
}

export interface CategoryDetails {
  id: string;
  name: string;
  description: string;
  ha_mapping: string[];
  interventions: Intervention[];
}

export interface InterventionStatus {
  id: string;
  name: string;
  level: ReadinessLevel;
  score: number;
  critical: boolean;
}

export interface CategoryAssessment {
  id: string;
  name: string;
  score: number;
  level: ReadinessLevel;
  interventions: InterventionStatus[];
}

export interface CriticalGap {
  category: string;
  intervention: string;
  current_level: ReadinessLevel;
  gap_severity: 'high' | 'medium';
}

export interface DigitalHealthRecommendation {
  priority: number;
  type: string;
  intervention?: string;
  category?: string;
  recommendation: string;
  expected_impact: string;
}

export interface DigitalHealthAssessment {
  hospital_id: string;
  assessment_date: string;
  categories: CategoryAssessment[];
  overall_score: number;
  overall_level: ReadinessLevel;
  critical_gaps: CriticalGap[];
  recommendations: DigitalHealthRecommendation[];
}

export interface HAAlignment {
  intervention_id: string;
  intervention_name: string;
  category: string;
  ha_chapters: string[];
  critical_for_accreditation: boolean;
  impact_description: string;
}

