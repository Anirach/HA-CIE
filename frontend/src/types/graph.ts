/**
 * Type definitions for Graph visualization.
 */

export interface GraphNodeData {
  id: string;
  label: string;
  name: string;
  part: string;
  partName: string;
  weight: number;
  focus: string;
  color: string;
  criteriaCount: number;
  essentialCount: number;
  coreCount: number;
}

export interface GraphNode {
  data: GraphNodeData;
}

export interface GraphEdgeData {
  id: string;
  source: string;
  target: string;
  strength: number;
  type: string;
  mechanism: string;
  width: number;
}

export interface GraphEdge {
  data: GraphEdgeData;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface PartSummary {
  number: string;
  name: string;
  weight: number;
  color: string;
  chapter_count: number;
}

export interface Criterion {
  id: string;
  name: string;
  weight: number;
  category: 'essential' | 'core' | 'basic';
  description?: string;
}

export interface CausalRelationship {
  source: string;
  target: string;
  strength: number;
  relationship_type: string;
  mechanism: string;
  direction?: string;
}

export interface ChapterDetail {
  id: string;
  number: string;
  name: string;
  weight: number;
  focus: string;
  part_number: string;
  part_name: string;
  color: string;
  criteria: Criterion[];
  incoming_relationships: CausalRelationship[];
  outgoing_relationships: CausalRelationship[];
}

export interface RelationshipDetail {
  source: string;
  source_name: string;
  target: string;
  target_name: string;
  strength: number;
  relationship_type: string;
  mechanism: string;
}

export interface GraphStatistics {
  parts: number;
  chapters: number;
  criteria: {
    total: number;
    essential: number;
    core: number;
    basic: number;
  };
  relationships: {
    total: number;
    average_strength: number;
    by_type: Record<string, number>;
  };
  parts_detail: Array<{
    number: string;
    name: string;
    chapters: number;
    criteria: number;
  }>;
}

