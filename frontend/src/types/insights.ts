/**
 * Insights-related type definitions.
 */

export type InsightCategory =
  | 'gap_analysis'
  | 'trend_analysis'
  | 'risk_assessment'
  | 'recommendation'
  | 'root_cause'
  | 'benchmark';

export type InsightPriority = 'critical' | 'high' | 'medium' | 'low';

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low';

export interface InsightMetric {
  name: string;
  value: number | string;
  trend: string;
}

export interface Insight {
  id: string;
  category: InsightCategory;
  priority: InsightPriority;
  title: string;
  description: string;
  affected_criteria?: string[];
  affected_areas?: string[];
  metric?: InsightMetric;
  action_items?: string[];
}

export interface Recommendation {
  rank: number;
  title: string;
  description: string;
  priority: InsightPriority;
  category: InsightCategory;
  estimated_impact: string;
  estimated_effort: string;
  related_insight_id?: string;
}

export interface InsightsSummary {
  total: number;
  by_category: Record<InsightCategory, number>;
  by_priority: Record<InsightPriority, number>;
}

export interface InsightsResponse {
  hospital_id: string;
  generated_at: string;
  assessment_date: string | null;
  overall_score: number;
  insights: Insight[];
  summary: InsightsSummary;
  recommendations: Recommendation[];
  risk_score: number;
  risk_level: RiskLevel;
}

export interface InsightCategoryInfo {
  id: string;
  name: string;
  icon: string;
}

export interface InsightCategoriesResponse {
  categories: InsightCategoryInfo[];
}

export interface InsightsSummaryResponse {
  hospital_id: string;
  generated_at: string;
  risk_score: number;
  risk_level: RiskLevel;
  summary: InsightsSummary;
  top_recommendations: Recommendation[];
}

export interface RiskAssessmentResponse {
  hospital_id: string;
  risk_score: number;
  risk_level: RiskLevel;
  risk_insights: Insight[];
  critical_count: number;
  high_count: number;
}

export interface RecommendationsResponse {
  hospital_id: string;
  recommendations: Recommendation[];
  total_available: number;
}


