/**
 * Reports page component.
 * PDF report generation and preview.
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  FileText,
  Download,
  Eye,
  Building2,
  RefreshCw,
  AlertTriangle,
  FileBarChart,
  FilePieChart,
  FileSearch,
  TrendingUp,
  CheckCircle,
  Clock,
} from 'lucide-react';
import { useRoleStore } from '../store/roleStore';
import { getHospitals } from '../api/dashboard';
import { apiClient } from '../api/client';
import clsx from 'clsx';

interface ReportType {
  id: string;
  name: string;
  description: string;
  pages: string;
}

// Report type icons
const REPORT_ICONS: Record<string, typeof FileText> = {
  executive_summary: FilePieChart,
  full_assessment: FileBarChart,
  gap_analysis: FileSearch,
  progress_report: TrendingUp,
};

// Report type colors
const REPORT_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  executive_summary: { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200' },
  full_assessment: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
  gap_analysis: { bg: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-200' },
  progress_report: { bg: 'bg-green-50', text: 'text-green-600', border: 'border-green-200' },
};

export function ReportsPage() {
  const { isExecutiveView } = useRoleStore();
  const [selectedHospitalId, setSelectedHospitalId] = useState('hosp-001');
  const [generatingReport, setGeneratingReport] = useState<string | null>(null);
  const [recentReports, setRecentReports] = useState<Array<{
    type: string;
    name: string;
    date: Date;
    hospitalId: string;
  }>>([]);

  // Fetch hospitals
  const { data: hospitals } = useQuery({
    queryKey: ['hospitals'],
    queryFn: getHospitals,
  });

  // Fetch report types
  const { data: reportTypesData, isLoading } = useQuery({
    queryKey: ['report-types'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/reports/types');
      return response.data;
    },
  });

  const reportTypes: ReportType[] = reportTypesData?.report_types || [];

  const handleDownload = async (reportType: string, reportName: string) => {
    setGeneratingReport(reportType);
    
    try {
      const response = await apiClient.get(
        `/api/v1/reports/generate/${reportType}`,
        {
          params: { hospital_id: selectedHospitalId },
          responseType: 'blob',
        }
      );
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ha-cie-${reportType.replace('_', '-')}-${selectedHospitalId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      // Add to recent reports
      setRecentReports((prev) => [
        {
          type: reportType,
          name: reportName,
          date: new Date(),
          hospitalId: selectedHospitalId,
        },
        ...prev.slice(0, 4),
      ]);
    } catch (error) {
      console.error('Failed to generate report:', error);
      alert('Failed to generate report. Please try again.');
    } finally {
      setGeneratingReport(null);
    }
  };

  const handlePreview = async (reportType: string) => {
    // Open preview in new tab
    const url = `${apiClient.defaults.baseURL}/api/v1/reports/preview/${reportType}?hospital_id=${selectedHospitalId}`;
    window.open(url, '_blank');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading report options...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="mt-1 text-gray-600">
            {isExecutiveView()
              ? 'Download executive summaries and key reports'
              : 'Generate and download comprehensive accreditation reports'
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

      {/* Report Types Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reportTypes.map((report) => {
          const Icon = REPORT_ICONS[report.id] || FileText;
          const colors = REPORT_COLORS[report.id] || REPORT_COLORS.executive_summary;
          const isGenerating = generatingReport === report.id;
          
          // Filter for executive mode
          if (isExecutiveView() && report.id !== 'executive_summary' && report.id !== 'progress_report') {
            return null;
          }
          
          return (
            <div
              key={report.id}
              className={clsx(
                'bg-white rounded-xl shadow-sm border p-6 transition-all hover:shadow-md',
                colors.border
              )}
            >
              <div className="flex items-start gap-4">
                <div className={clsx('p-3 rounded-xl', colors.bg)}>
                  <Icon className={clsx('h-6 w-6', colors.text)} />
                </div>
                
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{report.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{report.description}</p>
                  <p className="text-xs text-gray-400 mt-2">
                    Approximately {report.pages} pages
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 mt-4 pt-4 border-t border-gray-100">
                <button
                  onClick={() => handleDownload(report.id, report.name)}
                  disabled={isGenerating}
                  className={clsx(
                    'flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors',
                    isGenerating
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-indigo-600 text-white hover:bg-indigo-700'
                  )}
                >
                  {isGenerating ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4" />
                      Download PDF
                    </>
                  )}
                </button>
                
                <button
                  onClick={() => handlePreview(report.id)}
                  disabled={isGenerating}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  <Eye className="h-4 w-4" />
                  Preview
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Reports */}
      {recentReports.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="h-5 w-5 text-gray-400" />
            <h3 className="font-semibold text-gray-900">Recently Generated</h3>
          </div>
          
          <div className="space-y-3">
            {recentReports.map((report, index) => {
              const Icon = REPORT_ICONS[report.type] || FileText;
              const colors = REPORT_COLORS[report.type] || REPORT_COLORS.executive_summary;
              
              return (
                <div
                  key={`${report.type}-${index}`}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
                >
                  <div className={clsx('p-2 rounded-lg', colors.bg)}>
                    <Icon className={clsx('h-4 w-4', colors.text)} />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{report.name}</p>
                    <p className="text-xs text-gray-500">
                      {report.date.toLocaleTimeString()} • Hospital: {report.hospitalId}
                    </p>
                  </div>
                  <CheckCircle className="h-5 w-5 text-green-500" />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-100 p-6">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-indigo-100 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Report Generation Tips</h3>
            <ul className="mt-2 text-sm text-gray-600 space-y-1">
              <li>• <b>Executive Summary</b> - Best for board meetings and leadership updates</li>
              <li>• <b>Full Assessment</b> - Complete details for internal review and planning</li>
              <li>• <b>Gap Analysis</b> - Focus on areas needing improvement</li>
              <li>• <b>Progress Report</b> - Compare assessments over time</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportsPage;
