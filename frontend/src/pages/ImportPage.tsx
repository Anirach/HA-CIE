/**
 * Import page component.
 * Data import for JSON/Excel files with drag-and-drop support.
 */
import { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Upload,
  FileJson,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Download,
  Building2,
  Calendar,
  ArrowRight,
} from 'lucide-react';
import { apiClient } from '../api/client';
import clsx from 'clsx';

interface ImportResult {
  success: boolean;
  message: string;
  hospital_id?: string;
  hospital_name?: string;
  assessments_imported?: number;
  errors?: string[];
}

interface FilePreview {
  file: File;
  type: 'json' | 'excel';
  preview?: any;
  error?: string;
}

export function ImportPage() {
  const queryClient = useQueryClient();
  const [isDragOver, setIsDragOver] = useState(false);
  const [files, setFiles] = useState<FilePreview[]>([]);
  const [importResults, setImportResults] = useState<ImportResult[]>([]);

  // Import mutation
  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/api/v1/hospitals/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: (data) => {
      setImportResults((prev) => [...prev, data]);
      queryClient.invalidateQueries({ queryKey: ['hospitals'] });
      queryClient.invalidateQueries({ queryKey: ['assessments'] });
    },
    onError: (error: any) => {
      setImportResults((prev) => [
        ...prev,
        {
          success: false,
          message: error.response?.data?.detail || 'Import failed',
          errors: [error.message],
        },
      ]);
    },
  });

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    processFiles(droppedFiles);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      processFiles(selectedFiles);
    }
  }, []);

  const processFiles = async (newFiles: File[]) => {
    const validFiles: FilePreview[] = [];
    
    for (const file of newFiles) {
      const ext = file.name.toLowerCase().split('.').pop();
      
      if (ext === 'json') {
        try {
          const text = await file.text();
          const preview = JSON.parse(text);
          validFiles.push({ file, type: 'json', preview });
        } catch {
          validFiles.push({ file, type: 'json', error: 'Invalid JSON format' });
        }
      } else if (ext === 'xlsx' || ext === 'xls') {
        validFiles.push({ file, type: 'excel' });
      } else {
        validFiles.push({ 
          file, 
          type: 'json', 
          error: 'Unsupported file type. Please use JSON or Excel files.' 
        });
      }
    }
    
    setFiles((prev) => [...prev, ...validFiles]);
  };

  const handleImport = async () => {
    setImportResults([]);
    
    for (const filePreview of files) {
      if (!filePreview.error) {
        await importMutation.mutateAsync(filePreview.file);
      }
    }
    
    // Clear files after import
    setFiles([]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const downloadTemplate = (_type: 'json' | 'excel') => {
    const template = {
      hospital: {
        name: "Sample Hospital",
        bed_count: 200,
        hospital_type: "General",
        region: "Central",
        ownership: "Public"
      },
      assessments: [
        {
          assessment_date: "2024-01-15",
          criterion_scores: [
            { criterion_id: "I-1-1", score: 3.5, notes: "Good leadership culture" },
            { criterion_id: "II-1-1", score: 3.0, notes: "QMS in place" }
          ]
        }
      ]
    };
    
    const blob = new Blob([JSON.stringify(template, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'hospital-template.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Import Data</h1>
        <p className="mt-1 text-gray-600">
          Upload hospital assessment data from JSON or Excel files
        </p>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={clsx(
          'border-2 border-dashed rounded-xl p-12 transition-colors',
          isDragOver
            ? 'border-indigo-500 bg-indigo-50'
            : 'border-gray-300 bg-white hover:border-gray-400'
        )}
      >
        <div className="text-center">
          <Upload className={clsx(
            'h-12 w-12 mx-auto mb-4',
            isDragOver ? 'text-indigo-500' : 'text-gray-400'
          )} />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isDragOver ? 'Drop files here' : 'Drag and drop files'}
          </h3>
          <p className="text-gray-500 mb-4">
            or click to browse your computer
          </p>
          
          <input
            type="file"
            id="file-upload"
            className="hidden"
            accept=".json,.xlsx,.xls"
            multiple
            onChange={handleFileSelect}
          />
          <label
            htmlFor="file-upload"
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 cursor-pointer"
          >
            <Upload className="h-4 w-4" />
            Select Files
          </label>
          
          <p className="text-sm text-gray-400 mt-4">
            Supported formats: JSON, Excel (.xlsx, .xls)
          </p>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Files to Import</h3>
          
          <div className="space-y-3">
            {files.map((filePreview, index) => (
              <div
                key={`${filePreview.file.name}-${index}`}
                className={clsx(
                  'flex items-center gap-4 p-4 rounded-lg border',
                  filePreview.error
                    ? 'bg-red-50 border-red-200'
                    : 'bg-gray-50 border-gray-200'
                )}
              >
                {filePreview.type === 'json' ? (
                  <FileJson className={clsx(
                    'h-8 w-8',
                    filePreview.error ? 'text-red-400' : 'text-blue-500'
                  )} />
                ) : (
                  <FileSpreadsheet className="h-8 w-8 text-green-500" />
                )}
                
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">
                    {filePreview.file.name}
                  </p>
                  <p className="text-sm text-gray-500">
                    {(filePreview.file.size / 1024).toFixed(1)} KB
                  </p>
                  {filePreview.error && (
                    <p className="text-sm text-red-600 mt-1">{filePreview.error}</p>
                  )}
                  {filePreview.preview && (
                    <div className="text-sm text-gray-600 mt-1">
                      {filePreview.preview.hospital?.name && (
                        <span className="flex items-center gap-1">
                          <Building2 className="h-3 w-3" />
                          {filePreview.preview.hospital.name}
                        </span>
                      )}
                      {filePreview.preview.assessments?.length > 0 && (
                        <span className="flex items-center gap-1 mt-0.5">
                          <Calendar className="h-3 w-3" />
                          {filePreview.preview.assessments.length} assessment(s)
                        </span>
                      )}
                    </div>
                  )}
                </div>
                
                {filePreview.error ? (
                  <XCircle className="h-5 w-5 text-red-500" />
                ) : (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                )}
                
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 text-gray-400 hover:text-red-500"
                >
                  <XCircle className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleImport}
              disabled={files.every((f) => f.error) || importMutation.isPending}
              className={clsx(
                'flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors',
                files.every((f) => f.error) || importMutation.isPending
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              )}
            >
              {importMutation.isPending ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Importing...
                </>
              ) : (
                <>
                  <ArrowRight className="h-4 w-4" />
                  Import All
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Import Results */}
      {importResults.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Import Results</h3>
          
          <div className="space-y-3">
            {importResults.map((result, index) => (
              <div
                key={index}
                className={clsx(
                  'flex items-start gap-3 p-4 rounded-lg',
                  result.success ? 'bg-green-50' : 'bg-red-50'
                )}
              >
                {result.success ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
                )}
                <div>
                  <p className={clsx(
                    'font-medium',
                    result.success ? 'text-green-700' : 'text-red-700'
                  )}>
                    {result.message}
                  </p>
                  {result.hospital_name && (
                    <p className="text-sm text-gray-600 mt-1">
                      Hospital: {result.hospital_name}
                    </p>
                  )}
                  {result.assessments_imported !== undefined && (
                    <p className="text-sm text-gray-600">
                      Assessments imported: {result.assessments_imported}
                    </p>
                  )}
                  {result.errors && result.errors.length > 0 && (
                    <ul className="text-sm text-red-600 mt-1 list-disc list-inside">
                      {result.errors.map((err, i) => (
                        <li key={i}>{err}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Templates Section */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="font-semibold text-gray-900 mb-4">Download Templates</h3>
        <p className="text-gray-600 mb-4">
          Use these templates to format your data correctly before importing.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => downloadTemplate('json')}
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <FileJson className="h-8 w-8 text-blue-500" />
            <div>
              <p className="font-medium text-gray-900">JSON Template</p>
              <p className="text-sm text-gray-500">Hospital data with assessments</p>
            </div>
            <Download className="h-5 w-5 text-gray-400 ml-auto" />
          </button>
          
          <button
            onClick={() => downloadTemplate('excel')}
            className="flex items-center gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-left"
          >
            <FileSpreadsheet className="h-8 w-8 text-green-500" />
            <div>
              <p className="font-medium text-gray-900">Excel Template</p>
              <p className="text-sm text-gray-500">Spreadsheet format</p>
            </div>
            <Download className="h-5 w-5 text-gray-400 ml-auto" />
          </button>
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-100 p-6">
        <div className="flex items-start gap-4">
          <div className="p-2 bg-blue-100 rounded-lg">
            <AlertTriangle className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Import Guidelines</h3>
            <ul className="mt-2 text-sm text-gray-600 space-y-1">
              <li>• <b>JSON files</b> should contain hospital data with optional assessments array</li>
              <li>• <b>Excel files</b> should have columns for criterion IDs and scores</li>
              <li>• <b>Smart merge</b>: Data for existing hospitals will be merged automatically</li>
              <li>• <b>Date format</b>: Use YYYY-MM-DD for assessment dates</li>
              <li>• <b>Score range</b>: Criterion scores should be between 1.0 and 5.0</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ImportPage;
