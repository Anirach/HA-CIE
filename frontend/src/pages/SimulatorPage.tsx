/**
 * What-If Simulator page component.
 * Supports QI Team (technical) and Executive (simplified) modes.
 */
import { useState, useMemo } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import {
  Play,
  Settings2,
  Briefcase,
  Target,
  TrendingUp,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  ArrowRight,
  Zap,
  Shield,
  RefreshCw,
  Building2,
  Info,
  Sparkles,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { getHospitals } from '../api/dashboard';
import {
  getScenarios,
  runScenario,
  runScenarioSummary,
  getImprovementPriorities,
} from '../api/simulation';
import type { Scenario, SimulationResult, SimulationSummary, ImprovementPriority } from '../types/simulation';

// Part colors
const PART_COLORS: Record<string, string> = {
  I: '#9333ea',
  II: '#dc2626',
  III: '#16a34a',
  IV: '#2563eb',
};

const LEVEL_COLORS: Record<string, string> = {
  Excellent: '#16a34a',
  'Very Good': '#22c55e',
  Good: '#eab308',
  Pass: '#f97316',
  'Not Accredited': '#dc2626',
};

const EFFORT_ICONS: Record<string, React.ReactNode> = {
  low: <Zap className="h-4 w-4 text-green-500" />,
  medium: <Settings2 className="h-4 w-4 text-yellow-500" />,
  high: <Target className="h-4 w-4 text-red-500" />,
};

export function SimulatorPage() {
  const { user } = useAuthStore();
  const isQiTeam = user?.role === 'qi_team';
  
  const [mode, setMode] = useState<'qi_team' | 'executive'>(isQiTeam ? 'qi_team' : 'executive');
  const [selectedHospitalId, setSelectedHospitalId] = useState<string>('hosp-001');
  const [selectedScenarioId, setSelectedScenarioId] = useState<string | null>(null);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [executiveSummary, setExecutiveSummary] = useState<SimulationSummary | null>(null);

  // Fetch hospitals
  const { data: hospitals } = useQuery({
    queryKey: ['hospitals'],
    queryFn: getHospitals,
  });

  // Fetch scenarios
  const { data: scenarios, isLoading: loadingScenarios } = useQuery({
    queryKey: ['scenarios', selectedHospitalId],
    queryFn: () => getScenarios(selectedHospitalId),
    enabled: !!selectedHospitalId,
  });

  // Fetch priorities (QI Team mode)
  const { data: prioritiesData } = useQuery({
    queryKey: ['priorities', selectedHospitalId],
    queryFn: () => getImprovementPriorities(selectedHospitalId),
    enabled: !!selectedHospitalId && mode === 'qi_team',
  });

  // Run scenario mutation
  const runScenarioMutation = useMutation({
    mutationFn: (scenarioId: string) => runScenario(selectedHospitalId, scenarioId),
    onSuccess: (result) => {
      setSimulationResult(result);
      setExecutiveSummary(null);
    },
  });

  // Run executive summary mutation
  const runSummaryMutation = useMutation({
    mutationFn: (scenarioId: string) => runScenarioSummary(selectedHospitalId, scenarioId),
    onSuccess: (summary) => {
      setExecutiveSummary(summary);
      setSimulationResult(null);
    },
  });

  const handleRunScenario = (scenarioId: string) => {
    setSelectedScenarioId(scenarioId);
    if (mode === 'executive') {
      runSummaryMutation.mutate(scenarioId);
    } else {
      runScenarioMutation.mutate(scenarioId);
    }
  };

  const selectedScenario = useMemo(() => {
    return scenarios?.find((s) => s.id === selectedScenarioId);
  }, [scenarios, selectedScenarioId]);

  // Chart data for comparison
  const comparisonData = useMemo(() => {
    if (!simulationResult) return [];
    return [
      { name: 'Part I', current: simulationResult.current_part_scores['I'] || 0, projected: simulationResult.projected_part_scores['I'] || 0, color: PART_COLORS['I'] },
      { name: 'Part II', current: simulationResult.current_part_scores['II'] || 0, projected: simulationResult.projected_part_scores['II'] || 0, color: PART_COLORS['II'] },
      { name: 'Part III', current: simulationResult.current_part_scores['III'] || 0, projected: simulationResult.projected_part_scores['III'] || 0, color: PART_COLORS['III'] },
      { name: 'Part IV', current: simulationResult.current_part_scores['IV'] || 0, projected: simulationResult.projected_part_scores['IV'] || 0, color: PART_COLORS['IV'] },
    ];
  }, [simulationResult]);

  const isLoading = runScenarioMutation.isPending || runSummaryMutation.isPending;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">What-If Simulator</h1>
          <p className="mt-1 text-gray-600">
            Explore improvement scenarios and project future accreditation scores
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Hospital Selector */}
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-gray-400" />
            <select
              value={selectedHospitalId}
              onChange={(e) => {
                setSelectedHospitalId(e.target.value);
                setSimulationResult(null);
                setExecutiveSummary(null);
              }}
              className="px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm"
            >
              {hospitals?.map((h) => (
                <option key={h.id} value={h.id}>{h.name}</option>
              ))}
            </select>
          </div>

          {/* Mode Toggle */}
          {isQiTeam && (
            <div className="flex items-center bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setMode('qi_team')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  mode === 'qi_team'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Settings2 className="h-4 w-4" />
                QI Team
              </button>
              <button
                onClick={() => setMode('executive')}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  mode === 'executive'
                    ? 'bg-white text-indigo-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Briefcase className="h-4 w-4" />
                Executive
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scenarios List */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
            <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-500" />
              Improvement Scenarios
            </h3>

            {loadingScenarios ? (
              <div className="flex items-center justify-center py-8">
                <RefreshCw className="h-6 w-6 text-indigo-600 animate-spin" />
              </div>
            ) : (
              <div className="space-y-3">
                {scenarios?.map((scenario) => (
                  <button
                    key={scenario.id}
                    onClick={() => handleRunScenario(scenario.id)}
                    disabled={isLoading}
                    className={`w-full text-left p-4 rounded-lg border transition-all ${
                      selectedScenarioId === scenario.id
                        ? 'border-indigo-500 bg-indigo-50 ring-2 ring-indigo-200'
                        : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
                    } ${isLoading ? 'opacity-50 cursor-wait' : ''}`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900">{scenario.name}</h4>
                        <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                          {scenario.description}
                        </p>
                      </div>
                      <ChevronRight className="h-5 w-5 text-gray-400 flex-shrink-0 ml-2" />
                    </div>
                    
                    <div className="flex items-center gap-4 mt-3 text-xs">
                      <span className="flex items-center gap-1 text-gray-500">
                        {EFFORT_ICONS[scenario.effort_level]}
                        {scenario.effort_level} effort
                      </span>
                      <span className="flex items-center gap-1 text-gray-500">
                        <Clock className="h-3 w-3" />
                        {scenario.timeline_months} months
                      </span>
                      <span className="flex items-center gap-1 text-green-600">
                        <TrendingUp className="h-3 w-3" />
                        +{(scenario.expected_improvement * 100).toFixed(0)}%
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Priorities (QI Team mode) */}
          {mode === 'qi_team' && prioritiesData?.priorities && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Target className="h-5 w-5 text-orange-500" />
                Top Improvement Priorities
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {prioritiesData.priorities.slice(0, 8).map((priority) => (
                  <div
                    key={priority.criterion_id}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {priority.criterion_id}
                      </p>
                      <p className="text-xs text-gray-500 truncate">{priority.criterion_name}</p>
                    </div>
                    <div className="flex items-center gap-2 ml-2">
                      <span className="text-xs text-orange-600 font-medium">
                        {priority.current_score} → {priority.recommended_target}
                      </span>
                      <span
                        className={`px-1.5 py-0.5 rounded text-xs ${
                          priority.category === 'essential'
                            ? 'bg-red-100 text-red-700'
                            : priority.category === 'core'
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {priority.category}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2">
          {isLoading ? (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 flex items-center justify-center h-96">
              <div className="text-center">
                <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Running simulation...</p>
              </div>
            </div>
          ) : mode === 'executive' && executiveSummary ? (
            /* Executive Mode Results */
            <div className="space-y-4">
              {/* Big Score Card */}
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg p-8 text-white">
                <h3 className="text-lg font-medium opacity-90 mb-6">{executiveSummary.scenario_name}</h3>
                
                <div className="flex items-center justify-center gap-8">
                  <div className="text-center">
                    <p className="text-sm opacity-75 mb-1">Current</p>
                    <p className="text-4xl font-bold">{executiveSummary.current_score.toFixed(1)}</p>
                    <p className="text-sm mt-1">{executiveSummary.current_level}</p>
                  </div>
                  
                  <ArrowRight className="h-8 w-8 opacity-50" />
                  
                  <div className="text-center">
                    <p className="text-sm opacity-75 mb-1">Projected</p>
                    <p className="text-5xl font-bold">{executiveSummary.projected_score.toFixed(1)}</p>
                    <p className="text-sm mt-1">{executiveSummary.projected_level}</p>
                  </div>
                </div>

                <div className="mt-6 pt-6 border-t border-white/20 flex items-center justify-center gap-8">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-300">
                      +{executiveSummary.improvement.toFixed(2)}
                    </p>
                    <p className="text-xs opacity-75">Score Improvement</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold">{executiveSummary.timeline_months}</p>
                    <p className="text-xs opacity-75">Months</p>
                  </div>
                </div>
              </div>

              {/* Key Information Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                    Key Actions
                  </h4>
                  <ul className="space-y-2">
                    {executiveSummary.key_actions.map((action, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                        <ChevronRight className="h-4 w-4 text-indigo-500 flex-shrink-0 mt-0.5" />
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Info className="h-5 w-5 text-blue-500" />
                    Assessment
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Effort Required</p>
                      <p className="text-sm text-gray-900">{executiveSummary.effort_summary}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Risk Level</p>
                      <p className="text-sm text-gray-900">{executiveSummary.risk_level}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Confidence</p>
                      <p className="text-sm text-gray-900">{executiveSummary.confidence}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : simulationResult ? (
            /* QI Team Mode Results */
            <div className="space-y-4">
              {/* Score Summary */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="font-semibold text-gray-900">{simulationResult.scenario_name}</h3>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-600">{simulationResult.estimated_months} months</span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-6 text-center">
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Current Score</p>
                    <p className="text-3xl font-bold text-gray-900">
                      {simulationResult.current_overall_score.toFixed(2)}
                    </p>
                    <p
                      className="text-sm font-medium mt-1"
                      style={{ color: LEVEL_COLORS[simulationResult.current_level] || '#666' }}
                    >
                      {simulationResult.current_level}
                    </p>
                  </div>
                  
                  <div className="flex flex-col items-center justify-center">
                    <ArrowRight className="h-6 w-6 text-gray-300 mb-2" />
                    <span className="text-lg font-bold text-green-600">
                      +{simulationResult.score_improvement.toFixed(2)}
                    </span>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-500 mb-1">Projected Score</p>
                    <p className="text-3xl font-bold text-indigo-600">
                      {simulationResult.projected_overall_score.toFixed(2)}
                    </p>
                    <p
                      className="text-sm font-medium mt-1"
                      style={{ color: LEVEL_COLORS[simulationResult.projected_level] || '#666' }}
                    >
                      {simulationResult.projected_level}
                    </p>
                  </div>
                </div>

                {/* Confidence Interval */}
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-gray-500">Confidence Interval</span>
                    <span className="text-gray-700">
                      {simulationResult.confidence_interval.low.toFixed(2)} -{' '}
                      {simulationResult.confidence_interval.high.toFixed(2)}
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded-full overflow-hidden relative">
                    <div
                      className="absolute h-full bg-indigo-200"
                      style={{
                        left: `${(simulationResult.confidence_interval.low / 5) * 100}%`,
                        width: `${((simulationResult.confidence_interval.high - simulationResult.confidence_interval.low) / 5) * 100}%`,
                      }}
                    />
                    <div
                      className="absolute h-full w-1 bg-indigo-600"
                      style={{
                        left: `${(simulationResult.confidence_interval.mid / 5) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Part Score Comparison Chart */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Domain Score Comparison</h4>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={comparisonData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis type="number" domain={[0, 5]} />
                    <YAxis dataKey="name" type="category" width={60} />
                    <Tooltip />
                    <Bar dataKey="current" name="Current" fill="#e5e7eb" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="projected" name="Projected" radius={[0, 4, 4, 0]}>
                      {comparisonData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Cascade Effects */}
              {simulationResult.cascade_effects.length > 0 && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <Zap className="h-5 w-5 text-amber-500" />
                    Cascade Effects ({simulationResult.cascade_effects.length} criteria affected)
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-64 overflow-y-auto">
                    {simulationResult.cascade_effects.slice(0, 12).map((effect) => (
                      <div
                        key={effect.criterion_id}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {effect.criterion_id}
                          </p>
                          <p className="text-xs text-gray-500">{effect.chapter_name}</p>
                        </div>
                        <div className="flex items-center gap-2 ml-2">
                          <span className="text-xs text-gray-500">
                            {effect.current_score.toFixed(1)}
                          </span>
                          <ArrowRight className="h-3 w-3 text-gray-400" />
                          <span className="text-xs font-medium text-green-600">
                            {effect.projected_score.toFixed(1)}
                          </span>
                          <span className="text-xs text-gray-400">
                            ({(effect.confidence * 100).toFixed(0)}%)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Interventions Detail */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h4 className="font-semibold text-gray-900 mb-4">
                  Interventions ({simulationResult.interventions.length})
                </h4>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                        <th className="pb-2">Criterion</th>
                        <th className="pb-2">Current</th>
                        <th className="pb-2">Target</th>
                        <th className="pb-2">Effort</th>
                        <th className="pb-2">Timeline</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {simulationResult.interventions.map((int) => (
                        <tr key={int.criterion_id} className="text-sm">
                          <td className="py-2 font-medium">{int.criterion_id}</td>
                          <td className="py-2 text-gray-500">
                            {int.current_score?.toFixed(1) || 'N/A'}
                          </td>
                          <td className="py-2 font-medium text-indigo-600">
                            {int.target_score.toFixed(1)}
                          </td>
                          <td className="py-2">
                            <span className="flex items-center gap-1">
                              {EFFORT_ICONS[int.effort_level]}
                              {int.effort_level}
                            </span>
                          </td>
                          <td className="py-2 text-gray-500">{int.timeline_months} mo</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          ) : (
            /* Empty State */
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-8 flex items-center justify-center h-96">
              <div className="text-center">
                <Play className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a Scenario to Begin
                </h3>
                <p className="text-gray-500 max-w-md">
                  Choose an improvement scenario from the list to see projected scores,
                  cascade effects, and implementation timeline.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SimulatorPage;
