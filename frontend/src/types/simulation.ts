/**
 * Type definitions for Simulations.
 */

export interface Intervention {
  criterion_id: string;
  target_score: number;
  current_score?: number;
  effort_level: 'low' | 'medium' | 'high';
  timeline_months: number;
}

export interface CascadeEffect {
  criterion_id: string;
  chapter_id: string;
  chapter_name: string;
  current_score: number;
  projected_score: number;
  change: number;
  path_length: number;
  confidence: number;
}

export interface SimulationResult {
  id: string;
  hospital_id: string;
  scenario_name: string;
  created_at: string;
  interventions: Intervention[];
  current_overall_score: number;
  projected_overall_score: number;
  score_improvement: number;
  current_part_scores: Record<string, number>;
  projected_part_scores: Record<string, number>;
  current_level: string;
  projected_level: string;
  cascade_effects: CascadeEffect[];
  confidence_interval: {
    low: number;
    mid: number;
    high: number;
  };
  estimated_months: number;
  effort_summary: string;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  target_areas: string[];
  interventions: Intervention[];
  expected_improvement: number;
  effort_level: string;
  timeline_months: number;
  suitable_for: string[];
}

export interface SimulationSummary {
  hospital_id: string;
  scenario_name: string;
  current_score: number;
  projected_score: number;
  improvement: number;
  current_level: string;
  projected_level: string;
  timeline_months: number;
  effort_summary: string;
  key_actions: string[];
  risk_level: string;
  confidence: string;
}

export interface ImprovementPriority {
  criterion_id: string;
  criterion_name: string;
  category: string;
  current_score: number;
  recommended_target: number;
  impact_score: number;
  downstream_effects: number;
  effort_estimate: string;
}


