/**
 * Simulation API functions.
 */
import { apiClient } from './client';
import type {
  Scenario,
  SimulationResult,
  SimulationSummary,
  ImprovementPriority,
} from '../types/simulation';

/**
 * Get available improvement scenarios.
 */
export async function getScenarios(hospitalId?: string): Promise<Scenario[]> {
  const params = hospitalId ? { hospital_id: hospitalId } : {};
  const response = await apiClient.get<Scenario[]>('/api/v1/simulations/scenarios', { params });
  return response.data;
}

/**
 * Get a specific scenario.
 */
export async function getScenario(scenarioId: string): Promise<Scenario> {
  const response = await apiClient.get<Scenario>(`/api/v1/simulations/scenarios/${scenarioId}`);
  return response.data;
}

/**
 * Run a custom simulation (QI Team only).
 */
export async function runSimulation(
  hospitalId: string,
  interventions: Array<{
    criterion_id: string;
    target_score: number;
    effort_level?: string;
    timeline_months?: number;
  }>,
  scenarioName?: string
): Promise<SimulationResult> {
  const response = await apiClient.post<SimulationResult>('/api/v1/simulations/run', {
    hospital_id: hospitalId,
    scenario_name: scenarioName || 'Custom Simulation',
    interventions,
  });
  return response.data;
}

/**
 * Run a pre-built scenario.
 */
export async function runScenario(
  hospitalId: string,
  scenarioId: string
): Promise<SimulationResult> {
  const response = await apiClient.post<SimulationResult>('/api/v1/simulations/run-scenario', {
    hospital_id: hospitalId,
    scenario_id: scenarioId,
  });
  return response.data;
}

/**
 * Run a scenario and get executive summary.
 */
export async function runScenarioSummary(
  hospitalId: string,
  scenarioId: string
): Promise<SimulationSummary> {
  const response = await apiClient.post<SimulationSummary>('/api/v1/simulations/run-scenario/summary', {
    hospital_id: hospitalId,
    scenario_id: scenarioId,
  });
  return response.data;
}

/**
 * Get improvement priorities.
 */
export async function getImprovementPriorities(
  hospitalId: string,
  targetLevel?: string
): Promise<{ priorities: ImprovementPriority[] }> {
  const params = targetLevel ? { target_level: targetLevel } : {};
  const response = await apiClient.get(`/api/v1/simulations/priorities/${hospitalId}`, { params });
  return response.data;
}

/**
 * Preview cascade effects (QI Team only).
 */
export async function previewCascade(
  hospitalId: string,
  criterionId: string,
  targetScore: number
) {
  const response = await apiClient.get('/api/v1/simulations/cascade-preview', {
    params: {
      hospital_id: hospitalId,
      criterion_id: criterionId,
      target_score: targetScore,
    },
  });
  return response.data;
}

