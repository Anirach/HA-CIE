/**
 * Hook for checking feature access based on current view mode.
 */
import { useMemo } from 'react';
import { useRoleStore } from '../store/roleStore';
import { Feature } from '../utils/roleAccess';

/**
 * Features available in QI Team mode only
 */
const QI_TEAM_ONLY_FEATURES: Feature[] = [
  Feature.CAUSAL_INFERENCE_CONTROLS,
  Feature.CASCADE_DEPTH_INDICATORS,
  Feature.CUSTOM_INTERVENTION_BUILDER,
  Feature.TECHNICAL_API_ACCESS,
  Feature.CONFIDENCE_INTERVALS,
  Feature.ADVANCED_FILTERING,
  Feature.DATA_IMPORT,
];

/**
 * Features available in both modes
 */
const COMMON_FEATURES: Feature[] = [
  Feature.VIEW_DASHBOARD,
  Feature.VIEW_GRAPH,
  Feature.RUN_SIMULATIONS,
  Feature.VIEW_REPORTS,
  Feature.VIEW_INSIGHTS,
];

export function useFeatureAccess() {
  const { viewMode, isQITeamView, isExecutiveView } = useRoleStore();

  const access = useMemo(() => {
    const isQI = isQITeamView();
    
    // Build feature access map
    const featureAccess: Record<Feature, boolean> = {} as Record<Feature, boolean>;
    
    // Common features are always available
    COMMON_FEATURES.forEach((feature) => {
      featureAccess[feature] = true;
    });
    
    // QI Team only features
    QI_TEAM_ONLY_FEATURES.forEach((feature) => {
      featureAccess[feature] = isQI;
    });

    return {
      viewMode,
      isQITeamMode: isQI,
      isExecutiveMode: isExecutiveView(),
      
      /**
       * Check if a specific feature is accessible
       */
      hasAccess: (feature: Feature): boolean => {
        return featureAccess[feature] ?? false;
      },
      
      /**
       * Check if any of the given features are accessible
       */
      hasAnyAccess: (features: Feature[]): boolean => {
        return features.some((f) => featureAccess[f]);
      },
      
      /**
       * Check if all of the given features are accessible
       */
      hasAllAccess: (features: Feature[]): boolean => {
        return features.every((f) => featureAccess[f]);
      },
      
      /**
       * Get list of accessible features
       */
      accessibleFeatures: Object.entries(featureAccess)
        .filter(([, hasAccess]) => hasAccess)
        .map(([feature]) => feature as Feature),
    };
  }, [viewMode, isQITeamView, isExecutiveView]);

  return access;
}

/**
 * Component wrapper that renders children only if feature is accessible
 */
interface FeatureGateProps {
  feature: Feature;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function FeatureGate({ feature, children, fallback = null }: FeatureGateProps) {
  const { hasAccess } = useFeatureAccess();
  
  if (!hasAccess(feature)) {
    return <>{fallback}</>;
  }
  
  return <>{children}</>;
}

export default useFeatureAccess;

