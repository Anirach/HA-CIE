/**
 * Digital Health Readiness page component.
 * WHO DISAH framework assessment and tracking.
 */
import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Laptop,
  Shield,
  Database,
  Activity,
  Bell,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Info,
  Zap,
} from 'lucide-react';
import { getDISAHFramework, getCategoryDetails, assessReadiness, getReadinessLevels } from '../api/digital-health';
import type { ReadinessLevel } from '../types/digital-health';
import clsx from 'clsx';

const CATEGORY_ICONS: Record<string, typeof Laptop> = {
  point_of_service: Laptop,
  provider_administration: Shield,
  registries_directories: Database,
  data_management: Activity,
  surveillance_response: Bell,
};

const LEVEL_COLORS: Record<ReadinessLevel, string> = {
  not_started: 'bg-gray-100 text-gray-600',
  planning: 'bg-blue-100 text-blue-700',
  pilot: 'bg-yellow-100 text-yellow-700',
  partial_implementation: 'bg-orange-100 text-orange-700',
  full_implementation: 'bg-green-100 text-green-700',
  optimizing: 'bg-purple-100 text-purple-700',
};

export function DigitalHealthPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [assessmentValues, setAssessmentValues] = useState<Record<string, string>>({});
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

  // Fetch framework
  const { data: framework, isLoading } = useQuery({
    queryKey: ['disah-framework'],
    queryFn: getDISAHFramework,
  });

  // Fetch readiness levels
  const { data: levelsData } = useQuery({
    queryKey: ['readiness-levels'],
    queryFn: getReadinessLevels,
  });

  // Fetch category details
  const { data: categoryDetails } = useQuery({
    queryKey: ['disah-category', selectedCategory],
    queryFn: () => selectedCategory ? getCategoryDetails(selectedCategory) : null,
    enabled: !!selectedCategory,
  });

  // Assessment mutation
  const assessMutation = useMutation({
    mutationFn: () => assessReadiness('hosp-001', assessmentValues),
  });

  const handleAssessmentChange = (interventionId: string, level: string) => {
    setAssessmentValues((prev) => ({
      ...prev,
      [interventionId]: level,
    }));
  };

  const toggleCategory = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setExpandedCategory(expandedCategory === categoryId ? null : categoryId);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Digital Health Readiness</h1>
        <p className="mt-1 text-gray-600">
          WHO DISAH Framework - Track digital health intervention implementation
        </p>
      </div>

      {/* Framework Overview */}
      <div className="bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl border border-cyan-200 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-cyan-100 rounded-lg">
            <Laptop className="h-6 w-6 text-cyan-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              WHO DISAH Framework
            </h2>
            <p className="text-gray-600 mt-1">
              Digital Health Interventions, Services and Applications in Health (DISAH) 
              provides a standardized classification for digital health systems.
            </p>
            <div className="flex gap-4 mt-3">
              <div className="text-center">
                <p className="text-2xl font-bold text-cyan-600">
                  {framework?.categories.length || 0}
                </p>
                <p className="text-xs text-gray-500">Categories</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-cyan-600">
                  {framework?.total_interventions || 0}
                </p>
                <p className="text-xs text-gray-500">Interventions</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-cyan-600">
                  {framework?.categories.reduce((acc, c) => acc + c.critical_count, 0) || 0}
                </p>
                <p className="text-xs text-gray-500">Critical Items</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Assessment Results (if available) */}
      {assessMutation.data && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Assessment Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-indigo-600">
                {assessMutation.data.overall_score.toFixed(1)}
              </p>
              <p className="text-sm text-gray-500">Overall Score</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <span className={clsx(
                'px-3 py-1 rounded-full text-sm font-medium',
                LEVEL_COLORS[assessMutation.data.overall_level as ReadinessLevel]
              )}>
                {assessMutation.data.overall_level.replace('_', ' ')}
              </span>
              <p className="text-sm text-gray-500 mt-2">Readiness Level</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-3xl font-bold text-red-600">
                {assessMutation.data.critical_gaps.length}
              </p>
              <p className="text-sm text-gray-500">Critical Gaps</p>
            </div>
          </div>

          {/* Critical Gaps */}
          {assessMutation.data.critical_gaps.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Critical Gaps</h4>
              <div className="space-y-2">
                {assessMutation.data.critical_gaps.map((gap, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-red-500" />
                    <div>
                      <p className="font-medium text-gray-900">{gap.intervention}</p>
                      <p className="text-sm text-gray-600">
                        Current: {gap.current_level.replace('_', ' ')} | Severity: {gap.gap_severity}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {assessMutation.data.recommendations.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Recommendations</h4>
              <div className="space-y-2">
                {assessMutation.data.recommendations.map((rec, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                    <Zap className="h-5 w-5 text-blue-500 mt-0.5" />
                    <div>
                      <p className="font-medium text-gray-900">{rec.recommendation}</p>
                      <p className="text-sm text-gray-600">{rec.expected_impact}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Categories */}
      <div className="space-y-4">
        {framework?.categories.map((category) => {
          const Icon = CATEGORY_ICONS[category.id] || Laptop;
          const isExpanded = expandedCategory === category.id;
          
          return (
            <div
              key={category.id}
              className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden"
            >
              <button
                onClick={() => toggleCategory(category.id)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-indigo-100 rounded-lg">
                    <Icon className="h-6 w-6 text-indigo-600" />
                  </div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-900">{category.name}</h3>
                    <p className="text-sm text-gray-500">{category.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {category.intervention_count} interventions
                    </p>
                    <p className="text-xs text-red-600">
                      {category.critical_count} critical
                    </p>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </button>
              
              {isExpanded && categoryDetails && (
                <div className="border-t border-gray-100 p-4">
                  <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
                    <Info className="h-4 w-4" />
                    <span>Mapped to HA chapters: {categoryDetails.ha_mapping.join(', ')}</span>
                  </div>
                  
                  <div className="space-y-3">
                    {categoryDetails.interventions.map((intervention) => (
                      <div
                        key={intervention.id}
                        className={clsx(
                          'p-4 rounded-lg border',
                          intervention.critical ? 'border-red-200 bg-red-50' : 'border-gray-200 bg-gray-50'
                        )}
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium text-gray-900">{intervention.name}</h4>
                              {intervention.critical && (
                                <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full">
                                  Critical
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 mt-1">{intervention.description}</p>
                          </div>
                          
                          <select
                            value={assessmentValues[intervention.id] || 'not_started'}
                            onChange={(e) => handleAssessmentChange(intervention.id, e.target.value)}
                            className={clsx(
                              'px-3 py-2 rounded-lg text-sm font-medium border',
                              LEVEL_COLORS[assessmentValues[intervention.id] as ReadinessLevel || 'not_started']
                            )}
                          >
                            {levelsData?.levels.map((level) => (
                              <option key={level.id} value={level.id}>
                                {level.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Submit Assessment */}
      <div className="flex justify-end">
        <button
          onClick={() => assessMutation.mutate()}
          disabled={assessMutation.isPending || Object.keys(assessmentValues).length === 0}
          className={clsx(
            'flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors',
            Object.keys(assessmentValues).length === 0
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          )}
        >
          {assessMutation.isPending ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <CheckCircle2 className="h-4 w-4" />
          )}
          Run Assessment
        </button>
      </div>
    </div>
  );
}

export default DigitalHealthPage;

