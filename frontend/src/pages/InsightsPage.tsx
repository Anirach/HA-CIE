/**
 * AI Insights page component.
 * AI-powered quality insights and recommendations.
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Lightbulb,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Target,
  GitBranch,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  RefreshCw,
  Shield,
  Zap,
  ArrowRight,
  Building2,
  Filter,
  Gauge,
  ClipboardCheck,
  Eye,
  FileQuestion,
  Users,
  Calendar,
  BookOpen,
} from 'lucide-react';
import { useRoleStore } from '../store/roleStore';
import { getInsights } from '../api/insights';
import { getHospitals } from '../api/dashboard';
import type { Insight, Recommendation, InsightPriority } from '../types/insights';
import clsx from 'clsx';

// Priority colors
const PRIORITY_COLORS: Record<InsightPriority, string> = {
  critical: 'bg-red-100 text-red-800 border-red-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-green-100 text-green-800 border-green-200',
};

const PRIORITY_BG: Record<InsightPriority, string> = {
  critical: 'bg-red-50 border-red-200',
  high: 'bg-orange-50 border-orange-200',
  medium: 'bg-yellow-50 border-yellow-200',
  low: 'bg-green-50 border-green-200',
};

// Category icons
const CATEGORY_ICONS: Record<string, typeof Target> = {
  gap_analysis: Target,
  trend_analysis: TrendingUp,
  risk_assessment: AlertTriangle,
  root_cause: GitBranch,
  benchmark: BarChart3,
  recommendation: Lightbulb,
};

// Risk level colors
const RISK_LEVEL_COLORS: Record<string, { bg: string; text: string; ring: string }> = {
  critical: { bg: 'bg-red-600', text: 'text-red-600', ring: 'ring-red-600' },
  high: { bg: 'bg-orange-500', text: 'text-orange-500', ring: 'ring-orange-500' },
  medium: { bg: 'bg-yellow-500', text: 'text-yellow-500', ring: 'ring-yellow-500' },
  low: { bg: 'bg-green-500', text: 'text-green-500', ring: 'ring-green-500' },
};

// Risk gauge component with smooth SVG arc
function RiskGauge({ score, level }: { score: number; level: string }) {
  const colors = RISK_LEVEL_COLORS[level] || RISK_LEVEL_COLORS.medium;
  
  // SVG dimensions
  const size = 200;
  const strokeWidth = 24;
  const radius = (size - strokeWidth) / 2;
  const center = size / 2;
  
  // Arc calculations (180 degree arc from left to right)
  const startAngle = Math.PI; // 180 degrees (left)
  const endAngle = 0; // 0 degrees (right)
  const scoreAngle = startAngle - (score / 100) * Math.PI;
  
  // Create arc path
  const createArc = (start: number, end: number) => {
    const startX = center + radius * Math.cos(start);
    const startY = center - radius * Math.sin(start);
    const endX = center + radius * Math.cos(end);
    const endY = center - radius * Math.sin(end);
    const largeArc = Math.abs(end - start) > Math.PI ? 1 : 0;
    return `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 1 ${endX} ${endY}`;
  };
  
  // Needle position
  const needleLength = radius - 15;
  const needleX = center + needleLength * Math.cos(scoreAngle);
  const needleY = center - needleLength * Math.sin(scoreAngle);
  
  return (
    <div className="relative flex flex-col items-center">
      <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        <defs>
          {/* Gradient for the arc */}
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#22c55e" />
            <stop offset="25%" stopColor="#84cc16" />
            <stop offset="50%" stopColor="#eab308" />
            <stop offset="75%" stopColor="#f97316" />
            <stop offset="100%" stopColor="#ef4444" />
          </linearGradient>
          
          {/* Shadow filter */}
          <filter id="dropShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.2"/>
          </filter>
        </defs>
        
        {/* Background track */}
        <path
          d={createArc(startAngle, endAngle)}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth + 4}
          strokeLinecap="round"
        />
        
        {/* Colored gradient arc */}
        <path
          d={createArc(startAngle, endAngle)}
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          filter="url(#dropShadow)"
        />
        
        {/* Tick marks */}
        {[0, 25, 50, 75, 100].map((tick) => {
          const tickAngle = startAngle - (tick / 100) * Math.PI;
          const innerRadius = radius - strokeWidth / 2 - 8;
          const outerRadius = radius - strokeWidth / 2 - 2;
          const x1 = center + innerRadius * Math.cos(tickAngle);
          const y1 = center - innerRadius * Math.sin(tickAngle);
          const x2 = center + outerRadius * Math.cos(tickAngle);
          const y2 = center - outerRadius * Math.sin(tickAngle);
          return (
            <line
              key={tick}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="#9ca3af"
              strokeWidth="2"
              strokeLinecap="round"
            />
          );
        })}
        
        {/* Needle */}
        <g filter="url(#dropShadow)">
          <line
            x1={center}
            y1={center}
            x2={needleX}
            y2={needleY}
            stroke={colors.bg.replace('bg-', '').includes('red') ? '#ef4444' : 
                   colors.bg.includes('orange') ? '#f97316' : 
                   colors.bg.includes('yellow') ? '#eab308' : '#22c55e'}
            strokeWidth="4"
            strokeLinecap="round"
            style={{ transition: 'all 0.7s ease-out' }}
          />
          {/* Needle tip */}
          <circle
            cx={needleX}
            cy={needleY}
            r="6"
            fill={colors.bg.includes('red') ? '#ef4444' : 
                  colors.bg.includes('orange') ? '#f97316' : 
                  colors.bg.includes('yellow') ? '#eab308' : '#22c55e'}
            style={{ transition: 'all 0.7s ease-out' }}
          />
        </g>
        
        {/* Center circle */}
        <circle cx={center} cy={center} r="12" fill="white" filter="url(#dropShadow)" />
        <circle cx={center} cy={center} r="8" fill="#6366f1" />
        
        {/* Labels */}
        <text x="20" y={center + 15} className="text-xs font-medium" fill="#22c55e">0</text>
        <text x={size - 30} y={center + 15} className="text-xs font-medium" fill="#ef4444">100</text>
      </svg>
      
      {/* Score display below gauge */}
      <div className="flex flex-col items-center -mt-2">
        <span className={clsx(
          'text-4xl font-bold',
          score <= 25 ? 'text-green-600' :
          score <= 50 ? 'text-yellow-600' :
          score <= 75 ? 'text-orange-600' : 'text-red-600'
        )}>
          {score}
        </span>
        <span className="text-sm text-gray-500">Risk Score (0-100)</span>
      </div>
    </div>
  );
}

// Insight card component
function InsightCard({ insight, isExpanded, onToggle }: { 
  insight: Insight; 
  isExpanded: boolean; 
  onToggle: () => void;
}) {
  const Icon = CATEGORY_ICONS[insight.category] || Lightbulb;
  
  return (
    <div
      className={clsx(
        'border rounded-xl transition-all cursor-pointer',
        PRIORITY_BG[insight.priority],
        isExpanded && 'ring-2 ring-indigo-500'
      )}
      onClick={onToggle}
    >
      <div className="p-4">
        <div className="flex items-start gap-3">
          <div className={clsx('p-2 rounded-lg', PRIORITY_COLORS[insight.priority])}>
            <Icon className="h-5 w-5" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={clsx(
                'text-xs font-medium px-2 py-0.5 rounded-full',
                PRIORITY_COLORS[insight.priority]
              )}>
                {insight.priority}
              </span>
              <span className="text-xs text-gray-500 capitalize">
                {insight.category.replace('_', ' ')}
              </span>
            </div>
            <h4 className="font-semibold text-gray-900">{insight.title}</h4>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{insight.description}</p>
          </div>
          <ChevronRight className={clsx(
            'h-5 w-5 text-gray-400 transition-transform',
            isExpanded && 'rotate-90'
          )} />
        </div>
        
        {/* Metric */}
        {insight.metric && (
          <div className="mt-3 flex items-center gap-3 text-sm">
            <span className="text-gray-500">{insight.metric.name}:</span>
            <span className="font-semibold text-gray-900">{insight.metric.value}</span>
            {insight.metric.trend === 'improving' && (
              <TrendingUp className="h-4 w-4 text-green-500" />
            )}
            {insight.metric.trend === 'declining' && (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
          </div>
        )}
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className="px-4 pb-4 space-y-3 border-t border-gray-200 pt-3">
          {/* Affected areas */}
          {insight.affected_criteria && insight.affected_criteria.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Affected Criteria</p>
              <div className="flex flex-wrap gap-1">
                {insight.affected_criteria.map((c) => (
                  <span key={c} className="text-xs bg-white px-2 py-0.5 rounded border border-gray-200">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {insight.affected_areas && insight.affected_areas.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Downstream Impact</p>
              <div className="flex flex-wrap gap-1">
                {insight.affected_areas.map((a) => (
                  <span key={a} className="text-xs bg-white px-2 py-0.5 rounded border border-gray-200">
                    {a}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {/* Action items */}
          {insight.action_items && insight.action_items.length > 0 && (
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Recommended Actions</p>
              <ul className="space-y-1">
                {insight.action_items.map((action, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// Recommendation card component
function RecommendationCard({ recommendation }: { recommendation: Recommendation }) {
  const impactColors: Record<string, string> = {
    very_high: 'text-red-600 bg-red-100',
    high: 'text-orange-600 bg-orange-100',
    medium: 'text-yellow-600 bg-yellow-100',
    low: 'text-green-600 bg-green-100',
  };
  
  const effortColors: Record<string, string> = {
    high: 'text-red-600 bg-red-100',
    medium: 'text-yellow-600 bg-yellow-100',
    low: 'text-green-600 bg-green-100',
  };
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
          {recommendation.rank}
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900">{recommendation.title}</h4>
          <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
          
          <div className="flex items-center gap-4 mt-3">
            <div className="flex items-center gap-1">
              <Zap className="h-4 w-4 text-gray-400" />
              <span className="text-xs text-gray-500">Impact:</span>
              <span className={clsx('text-xs px-1.5 py-0.5 rounded', impactColors[recommendation.estimated_impact] || 'bg-gray-100')}>
                {recommendation.estimated_impact.replace('_', ' ')}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Target className="h-4 w-4 text-gray-400" />
              <span className="text-xs text-gray-500">Effort:</span>
              <span className={clsx('text-xs px-1.5 py-0.5 rounded', effortColors[recommendation.estimated_effort] || 'bg-gray-100')}>
                {recommendation.estimated_effort}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

type InsightsTab = 'overview' | 'gaps' | 'recommendations' | 'surveyor';

export function InsightsPage() {
  const { isExecutiveView } = useRoleStore();
  const [selectedHospitalId, setSelectedHospitalId] = useState('hosp-001');
  const [expandedInsightId, setExpandedInsightId] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<InsightsTab>('overview');

  // Fetch hospitals
  const { data: hospitals } = useQuery({
    queryKey: ['hospitals'],
    queryFn: getHospitals,
  });

  // Fetch insights
  const { data: insightsData, isLoading, error, refetch } = useQuery({
    queryKey: ['insights', selectedHospitalId],
    queryFn: () => getInsights(selectedHospitalId),
    staleTime: 5 * 60 * 1000,
  });

  // Filter insights
  const filteredInsights = insightsData?.insights.filter((insight) => {
    if (categoryFilter !== 'all' && insight.category !== categoryFilter) return false;
    if (priorityFilter !== 'all' && insight.priority !== priorityFilter) return false;
    return true;
  }) || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Generating AI insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to generate insights</h3>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview' as const, label: 'Overview', icon: Gauge },
    { id: 'gaps' as const, label: 'Gaps & Risks', icon: AlertTriangle },
    { id: 'recommendations' as const, label: 'Recommendations', icon: Lightbulb },
    { id: 'surveyor' as const, label: 'Surveyor Prep', icon: ClipboardCheck },
  ];

  // Mock surveyor data
  const surveyorData = {
    focusAreas: [
      { id: 1, criterion: 'II-1', name: 'Quality Management System', reason: 'Recent score decline', risk: 'high' },
      { id: 2, criterion: 'II-4', name: 'Infection Prevention', reason: 'Below benchmark', risk: 'high' },
      { id: 3, criterion: 'II-6', name: 'Medication Management', reason: 'Essential criteria gap', risk: 'medium' },
      { id: 4, criterion: 'III-4', name: 'Patient Care Delivery', reason: 'Inconsistent documentation', risk: 'medium' },
      { id: 5, criterion: 'I-1', name: 'Leadership', reason: 'Governance gaps identified', risk: 'low' },
    ],
    potentialIFI: [
      { id: 1, area: 'Hand hygiene compliance tracking', likelihood: 85, category: 'IPC' },
      { id: 2, area: 'High-alert medication protocols', likelihood: 75, category: 'Medication Safety' },
      { id: 3, area: 'Surgical safety checklist adherence', likelihood: 70, category: 'Patient Safety' },
      { id: 4, area: 'Patient identification process', likelihood: 65, category: 'Care Process' },
      { id: 5, area: 'Emergency response documentation', likelihood: 60, category: 'Emergency Care' },
    ],
    documentsToReview: [
      { name: 'Quality Management Manual', status: 'needs_update', lastReviewed: '2023-06-15' },
      { name: 'IPC Guidelines', status: 'current', lastReviewed: '2024-03-01' },
      { name: 'Medication Safety Protocol', status: 'needs_update', lastReviewed: '2023-09-20' },
      { name: 'Patient Safety Goals', status: 'current', lastReviewed: '2024-01-10' },
      { name: 'Staff Competency Records', status: 'incomplete', lastReviewed: '2024-02-15' },
    ],
    tracerTopics: [
      { name: 'Medication Administration', criteria: ['II-6', 'III-4'], priority: 'high' },
      { name: 'Infection Control', criteria: ['II-4', 'II-3'], priority: 'high' },
      { name: 'Patient Assessment Flow', criteria: ['III-2', 'III-3'], priority: 'medium' },
      { name: 'Emergency Response', criteria: ['III-4', 'II-1'], priority: 'medium' },
    ],
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
    <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Insights</h1>
        <p className="mt-1 text-gray-600">
            {isExecutiveView()
              ? 'Key insights and strategic recommendations'
              : 'AI-powered analysis and improvement recommendations'
            }
        </p>
      </div>

        {/* Hospital Selector */}
        <div className="flex items-center gap-3">
          <Building2 className="h-5 w-5 text-gray-400" />
          <select
            value={selectedHospitalId}
            onChange={(e) => setSelectedHospitalId(e.target.value)}
            className="px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium focus:ring-2 focus:ring-indigo-500"
          >
            {hospitals?.map((h) => (
              <option key={h.id} value={h.id}>{h.name}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Tabs */}
      {!isExecutiveView() && (
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              )}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {insightsData && (
        <>
          {/* Surveyor Prep Tab */}
          {activeTab === 'surveyor' && !isExecutiveView() && (
            <div className="space-y-6">
              {/* Surveyor Prep Header */}
              <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl border border-amber-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-amber-100 rounded-lg">
                    <ClipboardCheck className="h-6 w-6 text-amber-600" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">Surveyor Preparation Guide</h2>
                    <p className="text-gray-600 mt-1">
                      AI-identified focus areas and potential Items for Improvement (IFI) based on your current assessment data.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Surveyor Focus Areas */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Eye className="h-5 w-5 text-red-500" />
                    <h3 className="font-semibold text-gray-900">Likely Surveyor Focus Areas</h3>
                  </div>
                  
                  <div className="space-y-3">
                    {surveyorData.focusAreas.map((area) => (
                      <div
                        key={area.id}
                        className={clsx(
                          'p-3 rounded-lg border-l-4',
                          area.risk === 'high' ? 'bg-red-50 border-red-500' :
                          area.risk === 'medium' ? 'bg-yellow-50 border-yellow-500' :
                          'bg-green-50 border-green-500'
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-gray-900">{area.criterion}</span>
                          <span className={clsx(
                            'text-xs px-2 py-0.5 rounded-full',
                            area.risk === 'high' ? 'bg-red-100 text-red-700' :
                            area.risk === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-green-100 text-green-700'
                          )}>
                            {area.risk} risk
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mt-1">{area.name}</p>
                        <p className="text-xs text-gray-500 mt-1">{area.reason}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Potential IFI Items */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <FileQuestion className="h-5 w-5 text-orange-500" />
                    <h3 className="font-semibold text-gray-900">Potential IFI Items</h3>
                  </div>
                  
                  <div className="space-y-3">
                    {surveyorData.potentialIFI.map((item) => (
                      <div key={item.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-900">{item.area}</span>
                          <span className="text-xs text-gray-500">{item.category}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                              className={clsx(
                                'h-full transition-all',
                                item.likelihood >= 80 ? 'bg-red-500' :
                                item.likelihood >= 60 ? 'bg-orange-500' :
                                'bg-yellow-500'
                              )}
                              style={{ width: `${item.likelihood}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium text-gray-600 w-10">
                            {item.likelihood}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Documents to Review */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <BookOpen className="h-5 w-5 text-blue-500" />
                    <h3 className="font-semibold text-gray-900">Documents to Review</h3>
                  </div>
                  
                  <div className="space-y-2">
                    {surveyorData.documentsToReview.map((doc) => (
                      <div key={doc.name} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {doc.status === 'current' ? (
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                          ) : doc.status === 'needs_update' ? (
                            <AlertTriangle className="h-5 w-5 text-yellow-500" />
                          ) : (
                            <AlertTriangle className="h-5 w-5 text-red-500" />
                          )}
                          <div>
                            <p className="text-sm font-medium text-gray-900">{doc.name}</p>
                            <p className="text-xs text-gray-500 flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Last reviewed: {doc.lastReviewed}
                            </p>
                          </div>
                        </div>
                        <span className={clsx(
                          'text-xs px-2 py-1 rounded',
                          doc.status === 'current' ? 'bg-green-100 text-green-700' :
                          doc.status === 'needs_update' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-red-100 text-red-700'
                        )}>
                          {doc.status === 'current' ? 'Current' : 
                           doc.status === 'needs_update' ? 'Needs Update' : 'Incomplete'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Tracer Topics */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Users className="h-5 w-5 text-purple-500" />
                    <h3 className="font-semibold text-gray-900">Recommended Tracer Topics</h3>
                  </div>
                  
                  <div className="space-y-3">
                    {surveyorData.tracerTopics.map((topic) => (
                      <div key={topic.name} className="p-3 bg-purple-50 rounded-lg border border-purple-100">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-900">{topic.name}</span>
                          <span className={clsx(
                            'text-xs px-2 py-0.5 rounded-full',
                            topic.priority === 'high' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                          )}>
                            {topic.priority}
                          </span>
                        </div>
                        <div className="flex gap-2">
                          {topic.criteria.map((c) => (
                            <span key={c} className="text-xs bg-white px-2 py-1 rounded border border-purple-200">
                              {c}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Preparation Timeline */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Preparation Timeline</h3>
                <div className="relative">
                  <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                  <div className="space-y-6">
                    {[
                      { week: '12 weeks', task: 'Complete gap analysis and identify priority areas', done: true },
                      { week: '10 weeks', task: 'Update all critical documentation', done: true },
                      { week: '8 weeks', task: 'Conduct internal mock surveys', done: false },
                      { week: '6 weeks', task: 'Address identified gaps and train staff', done: false },
                      { week: '4 weeks', task: 'Final document review and quality checks', done: false },
                      { week: '2 weeks', task: 'Final preparation and staff briefing', done: false },
                    ].map((item, index) => (
                      <div key={index} className="flex items-start gap-4 ml-1">
                        <div className={clsx(
                          'w-7 h-7 rounded-full flex items-center justify-center border-2 bg-white z-10',
                          item.done ? 'border-green-500' : 'border-gray-300'
                        )}>
                          {item.done ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                          ) : (
                            <div className="w-2 h-2 rounded-full bg-gray-300" />
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{item.week} before survey</p>
                          <p className="text-sm text-gray-600">{item.task}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Overview Tab - Risk Overview */}
          {(activeTab === 'overview' || isExecutiveView()) && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Risk Score */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Risk Assessment</h3>
                <span className={clsx(
                  'px-3 py-1 rounded-full text-sm font-medium',
                  PRIORITY_COLORS[insightsData.risk_level as InsightPriority]
                )}>
                  {insightsData.risk_level} risk
                </span>
              </div>
              
              <div className="flex justify-center">
                <RiskGauge score={insightsData.risk_score} level={insightsData.risk_level} />
              </div>
            </div>

            {/* Summary Stats */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Insight Summary</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-red-50 rounded-lg">
                  <p className="text-2xl font-bold text-red-600">
                    {insightsData.summary.by_priority.critical || 0}
                  </p>
                  <p className="text-xs text-red-600">Critical</p>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">
                    {insightsData.summary.by_priority.high || 0}
                  </p>
                  <p className="text-xs text-orange-600">High Priority</p>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <p className="text-2xl font-bold text-yellow-600">
                    {insightsData.summary.by_priority.medium || 0}
                  </p>
                  <p className="text-xs text-yellow-600">Medium</p>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {insightsData.summary.by_priority.low || 0}
                  </p>
                  <p className="text-xs text-green-600">Low</p>
                </div>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-sm text-gray-500">
                  Total: <span className="font-semibold text-gray-900">{insightsData.summary.total}</span> insights generated
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  Last updated: {new Date(insightsData.generated_at).toLocaleString()}
                </p>
              </div>
            </div>

            {/* Current Score */}
            <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-xl shadow-sm p-6 text-white">
              <h3 className="font-semibold mb-4">Current Status</h3>
              
              <div className="text-center py-4">
                <p className="text-5xl font-bold">{insightsData.overall_score.toFixed(1)}</p>
                <p className="text-indigo-200 mt-1">Overall Maturity Score</p>
              </div>
              
              <div className="mt-4 pt-4 border-t border-indigo-500">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-indigo-200">Target (HA)</span>
                  <span className="font-medium">4.0</span>
                </div>
                <div className="mt-2 h-2 bg-indigo-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white transition-all duration-500"
                    style={{ width: `${Math.min(100, (insightsData.overall_score / 4) * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
          )}

          {/* Recommendations Tab */}
          {(activeTab === 'recommendations' || activeTab === 'overview' || isExecutiveView()) && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                <h3 className="font-semibold text-gray-900">Top Recommendations</h3>
              </div>
              <span className="text-sm text-gray-500">
                Prioritized by impact and urgency
              </span>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {insightsData.recommendations.slice(0, isExecutiveView() ? 4 : 6).map((rec) => (
                <RecommendationCard key={rec.rank} recommendation={rec} />
              ))}
            </div>
          </div>
          )}

          {/* All Insights - Gaps Tab (QI Team Mode) */}
          {(activeTab === 'gaps' || activeTab === 'overview') && !isExecutiveView() && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <Shield className="h-5 w-5 text-indigo-600" />
                  <h3 className="font-semibold text-gray-900">All Insights</h3>
                  <span className="text-sm text-gray-500">
                    ({filteredInsights.length} of {insightsData.insights.length})
                  </span>
                </div>
                
                {/* Filters */}
                <div className="flex items-center gap-3">
                  <Filter className="h-4 w-4 text-gray-400" />
                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="all">All Categories</option>
                    <option value="gap_analysis">Gap Analysis</option>
                    <option value="trend_analysis">Trend Analysis</option>
                    <option value="risk_assessment">Risk Assessment</option>
                    <option value="root_cause">Root Cause</option>
                    <option value="benchmark">Benchmark</option>
                  </select>
                  <select
                    value={priorityFilter}
                    onChange={(e) => setPriorityFilter(e.target.value)}
                    className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="all">All Priorities</option>
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
              </div>
              
              <div className="space-y-3">
                {filteredInsights.map((insight) => (
                  <InsightCard
                    key={insight.id}
                    insight={insight}
                    isExpanded={expandedInsightId === insight.id}
                    onToggle={() => setExpandedInsightId(
                      expandedInsightId === insight.id ? null : insight.id
                    )}
                  />
                ))}
                
                {filteredInsights.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <Filter className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p>No insights match the current filters</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Executive Mode - Simplified View */}
          {isExecutiveView() && activeTab === 'overview' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Critical Items Requiring Attention</h3>
              
              <div className="space-y-3">
                {insightsData.insights
                  .filter((i) => i.priority === 'critical' || i.priority === 'high')
                  .slice(0, 5)
                  .map((insight) => (
                    <div
                      key={insight.id}
                      className={clsx('p-4 rounded-lg border', PRIORITY_BG[insight.priority])}
                    >
                      <div className="flex items-start gap-3">
                        <AlertTriangle className={clsx(
                          'h-5 w-5 flex-shrink-0',
                          insight.priority === 'critical' ? 'text-red-600' : 'text-orange-600'
                        )} />
                        <div>
                          <h4 className="font-medium text-gray-900">{insight.title}</h4>
                          <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                          {insight.action_items && insight.action_items[0] && (
                            <div className="flex items-center gap-2 mt-2 text-sm text-indigo-600">
                              <ArrowRight className="h-4 w-4" />
                              {insight.action_items[0]}
                            </div>
                          )}
                        </div>
                      </div>
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

export default InsightsPage;
