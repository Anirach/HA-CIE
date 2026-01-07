/**
 * Dashboard page component.
 * Shows compliance overview, trends, and key metrics.
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
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
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Shield,
  Target,
  Activity,
  ChevronRight,
  Building2,
  Calendar,
  Award,
  RefreshCw,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useRoleStore } from '../store/roleStore';
import { useFeatureAccess } from '../hooks/useFeatureAccess';
import { Feature } from '../utils/roleAccess';
import { getHospitals, getDashboard, getDashboardTrends } from '../api/dashboard';
import type { DashboardData, DashboardTrends, HospitalSummary } from '../types/dashboard';

// Part colors
const PART_COLORS: Record<string, string> = {
  I: '#9333ea',
  II: '#dc2626',
  III: '#16a34a',
  IV: '#2563eb',
};

const LEVEL_COLORS: Record<string, string> = {
  excellent: '#16a34a',
  very_good: '#22c55e',
  good: '#eab308',
  pass: '#f97316',
  not_accredited: '#dc2626',
};

const LEVEL_LABELS: Record<string, string> = {
  excellent: 'Excellent',
  very_good: 'Very Good',
  good: 'Good',
  pass: 'Pass',
  not_accredited: 'Not Accredited',
};

// Mini sparkline component
function Sparkline({ data, color = '#6366f1' }: { data: number[]; color?: string }) {
  const chartData = data.map((value, index) => ({ value, index }));
  
  return (
    <ResponsiveContainer width="100%" height={40}>
      <AreaChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
        <defs>
          <linearGradient id={`gradient-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.3} />
            <stop offset="95%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          fill={`url(#gradient-${color.replace('#', '')})`}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// Score badge component
function ScoreBadge({ score, size = 'md' }: { score: number | null; size?: 'sm' | 'md' | 'lg' }) {
  const getColor = (s: number) => {
    if (s >= 4.0) return 'bg-green-100 text-green-800 border-green-200';
    if (s >= 3.0) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (s >= 2.0) return 'bg-orange-100 text-orange-800 border-orange-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const sizes = {
    sm: 'text-sm px-2 py-0.5',
    md: 'text-base px-3 py-1',
    lg: 'text-2xl px-4 py-2 font-bold',
  };

  if (score === null) {
    return (
      <span className={`${sizes[size]} rounded-full bg-gray-100 text-gray-500 border border-gray-200`}>
        N/A
      </span>
    );
  }

  return (
    <span className={`${sizes[size]} rounded-full border ${getColor(score)}`}>
      {score.toFixed(1)}
    </span>
  );
}

export function DashboardPage() {
  const { user } = useAuthStore();
  const { isQITeamView, isExecutiveView } = useRoleStore();
  const { hasAccess } = useFeatureAccess();
  const [selectedHospitalId, setSelectedHospitalId] = useState<string>('hosp-001');

  // Fetch hospitals list
  const { data: hospitals, isLoading: loadingHospitals } = useQuery({
    queryKey: ['hospitals'],
    queryFn: getHospitals,
  });

  // Fetch dashboard data
  const {
    data: dashboard,
    isLoading: loadingDashboard,
    error: dashboardError,
    refetch: refetchDashboard,
  } = useQuery({
    queryKey: ['dashboard', selectedHospitalId],
    queryFn: () => getDashboard(selectedHospitalId),
    enabled: !!selectedHospitalId,
  });

  // Fetch trends data
  const { data: trends, isLoading: loadingTrends } = useQuery({
    queryKey: ['dashboard-trends', selectedHospitalId],
    queryFn: () => getDashboardTrends(selectedHospitalId),
    enabled: !!selectedHospitalId,
  });

  const isLoading = loadingHospitals || loadingDashboard || loadingTrends;

  if (isLoading && !dashboard) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (dashboardError) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load dashboard</h3>
          <button
            onClick={() => refetchDashboard()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {isExecutiveView() ? 'Executive Dashboard' : 'Dashboard'}
          </h1>
          <p className="mt-1 text-gray-600">
            {isExecutiveView() 
              ? `Welcome, ${user?.name || 'Executive'}. Here's your strategic overview.`
              : `Welcome back, ${user?.name || 'User'}. Here's your accreditation overview.`
            }
          </p>
        </div>
        
        {/* Hospital Selector */}
        <div className="flex items-center gap-3">
          <Building2 className="h-5 w-5 text-gray-400" />
          <select
            value={selectedHospitalId}
            onChange={(e) => setSelectedHospitalId(e.target.value)}
            className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {hospitals?.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {dashboard && (
        <>
          {/* Score Change Banner */}
          {dashboard.score_change !== null && (
            <div
              className={`rounded-xl p-4 flex items-center justify-between ${
                dashboard.score_change >= 0
                  ? 'bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200'
                  : 'bg-gradient-to-r from-red-50 to-orange-50 border border-red-200'
              }`}
            >
              <div className="flex items-center gap-3">
                {dashboard.score_change >= 0 ? (
                  <TrendingUp className="h-6 w-6 text-green-600" />
                ) : (
                  <TrendingDown className="h-6 w-6 text-red-600" />
                )}
                <div>
                  <p className="font-medium text-gray-900">
                    {dashboard.score_change >= 0 ? 'Improvement' : 'Regression'} since last assessment
                  </p>
                  <p className="text-sm text-gray-600">
                    Score changed from {dashboard.previous_score?.toFixed(1)} to{' '}
                    {dashboard.overall_maturity_score?.toFixed(1)}
                  </p>
                </div>
              </div>
              <span
                className={`text-2xl font-bold ${
                  dashboard.score_change >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {dashboard.score_change >= 0 ? '+' : ''}
                {dashboard.score_change.toFixed(2)}
              </span>
            </div>
          )}

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Maturity Score Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Maturity Score</p>
                  <div className="mt-2">
                    <ScoreBadge score={dashboard.overall_maturity_score} size="lg" />
                  </div>
                </div>
                <div className="p-3 bg-indigo-100 rounded-lg">
                  <LayoutDashboard className="h-6 w-6 text-indigo-600" />
                </div>
              </div>
              {trends?.trends.overall && trends.trends.overall.length > 1 && (
                <div className="mt-3">
                  <Sparkline
                    data={trends.trends.overall.map((t) => t.value)}
                    color="#6366f1"
                  />
                </div>
              )}
            </div>

            {/* Accreditation Level Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Accreditation Level</p>
                  <p
                    className="text-2xl font-bold mt-1"
                    style={{
                      color: LEVEL_COLORS[dashboard.accreditation_level || 'not_accredited'],
                    }}
                  >
                    {LEVEL_LABELS[dashboard.accreditation_level || 'not_accredited']}
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <Award className="h-6 w-6 text-green-600" />
                </div>
              </div>
              <div className="mt-3 flex items-center gap-2 text-sm text-gray-500">
                <Target className="h-4 w-4" />
                <span>Target: {LEVEL_LABELS[dashboard.target_level]}</span>
              </div>
            </div>

            {/* Compliance Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Criteria Assessed</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {dashboard.criteria_assessed}/{dashboard.total_criteria}
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <CheckCircle2 className="h-6 w-6 text-blue-600" />
                </div>
              </div>
              <div className="mt-3">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-500">Completion</span>
                  <span className="font-medium">{dashboard.compliance_percentage}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all duration-500"
                    style={{ width: `${dashboard.compliance_percentage}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Critical Gaps Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Critical Gaps</p>
                  <p className="text-2xl font-bold text-orange-600 mt-1">
                    {dashboard.critical_gaps.filter((g) => g.priority === 'critical').length}
                  </p>
                </div>
                <div className="p-3 bg-orange-100 rounded-lg">
                  <AlertTriangle className="h-6 w-6 text-orange-600" />
                </div>
              </div>
              <p className="mt-3 text-sm text-gray-500">
                {dashboard.critical_gaps.length} total gaps requiring attention
              </p>
            </div>
          </div>

          {/* Domain Scores & Trends */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Domain Scores */}
            <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Domain Scores</h3>
              <div className="space-y-4">
                {dashboard.domain_scores.map((domain) => (
                  <div key={domain.part} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: domain.color }}
                        />
                        <span className="font-medium text-gray-900">
                          Part {domain.part} - {domain.name}
                        </span>
                        <span className="text-xs text-gray-500">
                          ({(domain.weight * 100).toFixed(0)}%)
                        </span>
                      </div>
                      <ScoreBadge score={domain.score} size="sm" />
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full transition-all duration-500"
                        style={{
                          width: `${(domain.score / 5) * 100}%`,
                          backgroundColor: domain.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Trend Chart */}
              {trends?.trends.overall && trends.trends.overall.length > 1 && (
                <div className="mt-6 pt-6 border-t border-gray-100">
                  <h4 className="text-sm font-medium text-gray-700 mb-4">Score Trend</h4>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart
                      data={trends.trends.overall.map((t) => ({
                        date: new Date(t.date).toLocaleDateString('en-US', {
                          month: 'short',
                          year: '2-digit',
                        }),
                        score: t.value,
                      }))}
                      margin={{ top: 5, right: 20, bottom: 5, left: 0 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#9ca3af" />
                      <YAxis domain={[0, 5]} tick={{ fontSize: 12 }} stroke="#9ca3af" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e5e7eb',
                          borderRadius: '8px',
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke="#6366f1"
                        strokeWidth={2}
                        dot={{ fill: '#6366f1', strokeWidth: 2 }}
                        activeDot={{ r: 6, fill: '#6366f1' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Category Breakdown */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Criteria Status</h3>
              
              {/* Essential */}
              <div className="mb-4 p-4 bg-red-50 rounded-lg border border-red-100">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-red-600" />
                    <span className="font-medium text-red-900">Essential for Safety</span>
                  </div>
                  <span className="text-sm font-medium text-red-700">
                    {dashboard.essential_met}/{dashboard.essential_total}
                  </span>
                </div>
                <div className="h-2 bg-red-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-600"
                    style={{
                      width: `${
                        dashboard.essential_total > 0
                          ? (dashboard.essential_met / dashboard.essential_total) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>

              {/* Core */}
              <div className="mb-4 p-4 bg-amber-50 rounded-lg border border-amber-100">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-amber-600" />
                    <span className="font-medium text-amber-900">Core for Sustainability</span>
                  </div>
                  <span className="text-sm font-medium text-amber-700">
                    {dashboard.core_met}/{dashboard.core_total}
                  </span>
                </div>
                <div className="h-2 bg-amber-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-amber-600"
                    style={{
                      width: `${
                        dashboard.core_total > 0
                          ? (dashboard.core_met / dashboard.core_total) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>

              {/* Basic */}
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-gray-600" />
                    <span className="font-medium text-gray-900">Basic Requirements</span>
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {dashboard.basic_met}/{dashboard.basic_total}
                  </span>
                </div>
                <div className="h-2 bg-gray-300 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gray-600"
                    style={{
                      width: `${
                        dashboard.basic_total > 0
                          ? (dashboard.basic_met / dashboard.basic_total) * 100
                          : 0
                      }%`,
                    }}
                  />
                </div>
              </div>

              {/* Assessment History */}
              <div className="mt-6 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Calendar className="h-4 w-4" />
                  <span>
                    {dashboard.assessment_count} assessment
                    {dashboard.assessment_count !== 1 ? 's' : ''} recorded
                  </span>
                </div>
                {dashboard.latest_assessment_date && (
                  <p className="text-xs text-gray-400 mt-1">
                    Latest: {new Date(dashboard.latest_assessment_date).toLocaleDateString()}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Critical Gaps Table */}
          {dashboard.critical_gaps.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Priority Gaps</h3>
                <span className="text-sm text-gray-500">
                  {dashboard.critical_gaps.length} items need attention
                </span>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      <th className="pb-3">Priority</th>
                      <th className="pb-3">Criterion</th>
                      <th className="pb-3">Chapter</th>
                      <th className="pb-3">Category</th>
                      <th className="pb-3 text-right">Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {dashboard.critical_gaps.slice(0, 10).map((gap) => (
                      <tr key={gap.criterion_id} className="hover:bg-gray-50">
                        <td className="py-3">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                              gap.priority === 'critical'
                                ? 'bg-red-100 text-red-800'
                                : gap.priority === 'high'
                                ? 'bg-orange-100 text-orange-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {gap.priority}
                          </span>
                        </td>
                        <td className="py-3">
                          <div>
                            <p className="font-medium text-gray-900">{gap.criterion_id}</p>
                            <p className="text-sm text-gray-500">{gap.criterion_name}</p>
                          </div>
                        </td>
                        <td className="py-3 text-sm text-gray-600">
                          {gap.chapter_id} - {gap.chapter_name}
                        </td>
                        <td className="py-3">
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              gap.category === 'essential'
                                ? 'bg-red-50 text-red-700'
                                : gap.category === 'core'
                                ? 'bg-amber-50 text-amber-700'
                                : 'bg-gray-50 text-gray-700'
                            }`}
                          >
                            {gap.category}
                          </span>
                        </td>
                        <td className="py-3 text-right">
                          <ScoreBadge score={gap.score} size="sm" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Executive Summary - Only in Executive Mode */}
          {isExecutiveView() && (
            <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl shadow-lg p-6 text-white">
              <h3 className="text-lg font-semibold mb-4">Executive Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <p className="text-indigo-200 text-sm">Current Status</p>
                  <p className="text-3xl font-bold">
                    {LEVEL_LABELS[dashboard.accreditation_level || 'not_accredited']}
                  </p>
                  <p className="text-indigo-200 text-sm">
                    Score: {dashboard.overall_maturity_score?.toFixed(1)}/5.0
                  </p>
                </div>
                <div className="space-y-2">
                  <p className="text-indigo-200 text-sm">Key Metric</p>
                  <p className="text-3xl font-bold">{dashboard.compliance_percentage}%</p>
                  <p className="text-indigo-200 text-sm">Criteria Compliance</p>
                </div>
                <div className="space-y-2">
                  <p className="text-indigo-200 text-sm">Action Items</p>
                  <p className="text-3xl font-bold">
                    {dashboard.critical_gaps.filter((g) => g.priority === 'critical').length}
                  </p>
                  <p className="text-indigo-200 text-sm">Critical gaps to address</p>
                </div>
              </div>
              
              {/* Progress to Target */}
              <div className="mt-6 pt-4 border-t border-indigo-500">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-indigo-200">Progress to {LEVEL_LABELS[dashboard.target_level]}</span>
                  <span className="font-medium">{Math.min(100, Math.round((dashboard.overall_maturity_score || 0) / 4 * 100))}%</span>
                </div>
                <div className="h-3 bg-indigo-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.round((dashboard.overall_maturity_score || 0) / 4 * 100))}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Chapter Trends Sparklines - Only in QI Team Mode */}
          {isQITeamView() && trends?.chapter_trends && trends.chapter_trends.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Chapter Trends</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {trends.chapter_trends
                  .filter((ct) => ct.scores.length > 0)
                  .slice(0, 12)
                  .map((chapter) => (
                    <div
                      key={chapter.chapter_id}
                      className="p-3 bg-gray-50 rounded-lg border border-gray-100"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          {chapter.chapter_id}
                        </span>
                        <div className="flex items-center gap-1">
                          <ScoreBadge score={chapter.current_score} size="sm" />
                          {chapter.change !== null && (
                            <span
                              className={`text-xs ${
                                chapter.change >= 0 ? 'text-green-600' : 'text-red-600'
                              }`}
                            >
                              {chapter.change >= 0 ? '+' : ''}
                              {chapter.change.toFixed(1)}
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 truncate mb-2">{chapter.chapter_name}</p>
                      {chapter.scores.length > 1 && (
                        <Sparkline
                          data={chapter.scores.map((s) => s.score)}
                          color={
                            chapter.change && chapter.change >= 0 ? '#16a34a' : '#dc2626'
                          }
                        />
                      )}
                    </div>
                  ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default DashboardPage;
