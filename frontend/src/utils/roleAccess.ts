/**
 * Role-based access control utilities.
 */
import { UserRole } from '../types/auth';

/**
 * Features that are restricted based on user role.
 */
export enum Feature {
  // QI Team only features
  CAUSAL_INFERENCE_CONTROLS = 'causal_inference_controls',
  CASCADE_DEPTH_INDICATORS = 'cascade_depth_indicators',
  CUSTOM_INTERVENTION_BUILDER = 'custom_intervention_builder',
  TECHNICAL_API_ACCESS = 'technical_api_access',
  CONFIDENCE_INTERVALS = 'confidence_intervals',
  ADVANCED_FILTERING = 'advanced_filtering',
  DATA_IMPORT = 'data_import',

  // Available to all authenticated users
  VIEW_DASHBOARD = 'view_dashboard',
  VIEW_GRAPH = 'view_graph',
  RUN_SIMULATIONS = 'run_simulations',
  VIEW_REPORTS = 'view_reports',
  VIEW_INSIGHTS = 'view_insights',
}

/**
 * Define which features are accessible by each role.
 */
const rolePermissions: Record<UserRole, Feature[]> = {
  [UserRole.QI_TEAM]: [
    // QI Team has access to everything
    Feature.CAUSAL_INFERENCE_CONTROLS,
    Feature.CASCADE_DEPTH_INDICATORS,
    Feature.CUSTOM_INTERVENTION_BUILDER,
    Feature.TECHNICAL_API_ACCESS,
    Feature.CONFIDENCE_INTERVALS,
    Feature.ADVANCED_FILTERING,
    Feature.DATA_IMPORT,
    Feature.VIEW_DASHBOARD,
    Feature.VIEW_GRAPH,
    Feature.RUN_SIMULATIONS,
    Feature.VIEW_REPORTS,
    Feature.VIEW_INSIGHTS,
  ],
  [UserRole.EXECUTIVE]: [
    // Executives have simplified access
    Feature.VIEW_DASHBOARD,
    Feature.VIEW_GRAPH,
    Feature.RUN_SIMULATIONS,
    Feature.VIEW_REPORTS,
    Feature.VIEW_INSIGHTS,
  ],
};

/**
 * Check if a user role has access to a specific feature.
 */
export function hasFeatureAccess(role: UserRole | undefined, feature: Feature): boolean {
  if (!role) return false;
  return rolePermissions[role]?.includes(feature) ?? false;
}

/**
 * Check if the user is in QI Team mode (has full access).
 */
export function isQITeamMode(role: UserRole | undefined): boolean {
  return role === UserRole.QI_TEAM;
}

/**
 * Check if the user is in Executive mode (simplified access).
 */
export function isExecutiveMode(role: UserRole | undefined): boolean {
  return role === UserRole.EXECUTIVE;
}

/**
 * Get the display name for a role.
 */
export function getRoleDisplayName(role: UserRole | undefined): string {
  switch (role) {
    case UserRole.QI_TEAM:
      return 'QI Team Member';
    case UserRole.EXECUTIVE:
      return 'Executive';
    default:
      return 'Unknown';
  }
}

export default {
  hasFeatureAccess,
  isQITeamMode,
  isExecutiveMode,
  getRoleDisplayName,
  Feature,
};
