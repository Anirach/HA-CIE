/**
 * Types for ISQua EEA framework integration.
 */

export type ISQuaRating = 1 | 2 | 3;

export interface ISQuaPrinciple {
  id: string;
  number: number;
  name: string;
  description: string;
  focus_areas: string[];
  ha_chapters: string[];
  weight: number;
}

export interface HAMapping {
  chapter_name: string;
  isqua_principles: string[];
  alignment_strength: number;
  alignment_notes: string;
}

export interface ChapterScore {
  chapter_id: string;
  chapter_name: string;
  ha_score: number;
  isqua_rating: ISQuaRating;
  alignment_strength: number;
}

export interface PrincipleAssessment {
  principle_id: string;
  principle_name: string;
  principle_number: number;
  ha_score: number;
  isqua_rating: ISQuaRating;
  isqua_rating_text: string;
  chapter_details: ChapterScore[];
  focus_areas: string[];
  weight?: number;
}

export interface RatingSummary {
  not_met: number;
  partially_met: number;
  fully_met: number;
}

export interface ISQuaAssessment {
  overall_ha_score: number;
  overall_isqua_rating: ISQuaRating;
  overall_isqua_text: string;
  principle_results: PrincipleAssessment[];
  rating_summary: RatingSummary;
  strengths: PrincipleAssessment[];
  improvements_needed: PrincipleAssessment[];
}

