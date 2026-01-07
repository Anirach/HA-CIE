/**
 * Settings page component.
 * Hospital settings, profile, and application configuration.
 */
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Settings,
  Building2,
  Users,
  MapPin,
  Bed,
  Save,
  RefreshCw,
  CheckCircle2,
  Shield,
  Globe,
  Bell,
  Palette,
  Database,
  Trash2,
  AlertTriangle,
  Building,
  Calendar,
  Award,
} from 'lucide-react';
import { apiClient } from '../api/client';
import clsx from 'clsx';

interface Hospital {
  id: string;
  name: string;
  bed_count: number;
  hospital_type: string;
  region: string;
  ownership: string;
}

interface HospitalUpdateData {
  name?: string;
  bed_count?: number;
  hospital_type?: string;
  region?: string;
  ownership?: string;
}

type SettingsTab = 'profile' | 'accreditation' | 'notifications' | 'appearance' | 'data';

export function SettingsPage() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [formData, setFormData] = useState<HospitalUpdateData>({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Fetch hospitals list
  const { data: hospitals, isLoading } = useQuery({
    queryKey: ['hospitals'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/hospitals');
      return response.data.hospitals as Hospital[];
    },
  });

  // Get selected hospital (use first for now)
  const selectedHospital = hospitals?.[0];

  // Update hospital mutation
  const updateMutation = useMutation({
    mutationFn: async (data: HospitalUpdateData) => {
      if (!selectedHospital) return;
      const response = await apiClient.patch(
        `/api/v1/hospitals/${selectedHospital.id}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hospitals'] });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    },
  });

  const handleInputChange = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (Object.keys(formData).length > 0) {
      updateMutation.mutate(formData);
    }
  };

  const tabs = [
    { id: 'profile' as const, label: 'Hospital Profile', icon: Building2 },
    { id: 'accreditation' as const, label: 'Accreditation', icon: Award },
    { id: 'notifications' as const, label: 'Notifications', icon: Bell },
    { id: 'appearance' as const, label: 'Appearance', icon: Palette },
    { id: 'data' as const, label: 'Data Management', icon: Database },
  ];

  const hospitalTypes = ['General', 'Specialty', 'University', 'Community'];
  const regions = ['Central', 'North', 'Northeast', 'East', 'West', 'South'];
  const ownershipTypes = ['Public', 'Private', 'Foundation', 'University'];

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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="mt-1 text-gray-600">
            Manage hospital profile and application preferences
          </p>
        </div>
        
        {saveSuccess && (
          <div className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg">
            <CheckCircle2 className="h-4 w-4" />
            Settings saved successfully
          </div>
        )}
      </div>

      <div className="flex gap-6">
        {/* Sidebar Tabs */}
        <div className="w-56 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors',
                activeTab === tab.id
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              <tab.icon className="h-5 w-5" />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <Building2 className="h-5 w-5 text-indigo-500" />
                Hospital Profile
              </h2>

              {selectedHospital ? (
                <div className="space-y-6">
                  {/* Hospital Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Hospital Name
                    </label>
                    <input
                      type="text"
                      defaultValue={selectedHospital.name}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>

                  {/* Two Column Grid */}
                  <div className="grid grid-cols-2 gap-6">
                    {/* Bed Count */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <Bed className="h-4 w-4 inline mr-1" />
                        Bed Count
                      </label>
                      <input
                        type="number"
                        defaultValue={selectedHospital.bed_count}
                        onChange={(e) => handleInputChange('bed_count', parseInt(e.target.value))}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      />
                    </div>

                    {/* Hospital Type */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <Building className="h-4 w-4 inline mr-1" />
                        Hospital Type
                      </label>
                      <select
                        defaultValue={selectedHospital.hospital_type}
                        onChange={(e) => handleInputChange('hospital_type', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        {hospitalTypes.map((type) => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>

                    {/* Region */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <MapPin className="h-4 w-4 inline mr-1" />
                        Region
                      </label>
                      <select
                        defaultValue={selectedHospital.region}
                        onChange={(e) => handleInputChange('region', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        {regions.map((region) => (
                          <option key={region} value={region}>{region}</option>
                        ))}
                      </select>
                    </div>

                    {/* Ownership */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <Users className="h-4 w-4 inline mr-1" />
                        Ownership
                      </label>
                      <select
                        defaultValue={selectedHospital.ownership}
                        onChange={(e) => handleInputChange('ownership', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                      >
                        {ownershipTypes.map((type) => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Save Button */}
                  <div className="flex justify-end pt-4 border-t">
                    <button
                      onClick={handleSave}
                      disabled={updateMutation.isPending || Object.keys(formData).length === 0}
                      className={clsx(
                        'flex items-center gap-2 px-6 py-2 rounded-lg font-medium transition-colors',
                        Object.keys(formData).length === 0
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-indigo-600 text-white hover:bg-indigo-700'
                      )}
                    >
                      {updateMutation.isPending ? (
                        <RefreshCw className="h-4 w-4 animate-spin" />
                      ) : (
                        <Save className="h-4 w-4" />
                      )}
                      Save Changes
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">No hospital configured. Please import data first.</p>
              )}
            </div>
          )}

          {activeTab === 'accreditation' && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                  <Award className="h-5 w-5 text-indigo-500" />
                  Accreditation Settings
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Accreditation Level
                    </label>
                    <div className="px-4 py-3 bg-green-50 border border-green-200 rounded-lg text-green-700 font-medium">
                      Good (Score: 3.2)
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      <Calendar className="h-4 w-4 inline mr-1" />
                      Last Assessment Date
                    </label>
                    <input
                      type="date"
                      defaultValue="2024-06-15"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Target Accreditation Level
                    </label>
                    <select 
                      defaultValue="verygood"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="pass">Pass (2.5-2.9)</option>
                      <option value="good">Good (3.0-3.4)</option>
                      <option value="verygood">Very Good (3.5-3.9)</option>
                      <option value="excellent">Excellent (4.0+)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Next Survey Target Date
                    </label>
                    <input
                      type="date"
                      defaultValue="2025-06-15"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                </div>
              </div>
              
              {/* Standards Framework */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 className="font-semibold text-gray-900 mb-4">Active Standards</h3>
                <div className="space-y-3">
                  <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-indigo-600" />
                    <div>
                      <p className="font-medium text-gray-900">HA Thailand Standards 5th Edition</p>
                      <p className="text-sm text-gray-500">Healthcare Accreditation Institute</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input type="checkbox" defaultChecked className="h-4 w-4 text-indigo-600" />
                    <div>
                      <p className="font-medium text-gray-900">ISQua EEA Guidelines 6th Edition</p>
                      <p className="text-sm text-gray-500">International Society for Quality</p>
                    </div>
                  </label>
                  <label className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input type="checkbox" defaultChecked={false} className="h-4 w-4 text-indigo-600" />
                    <div>
                      <p className="font-medium text-gray-900">WHO DISAH Framework</p>
                      <p className="text-sm text-gray-500">Digital Health Interventions</p>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <Bell className="h-5 w-5 text-indigo-500" />
                Notification Preferences
              </h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Assessment Reminders</p>
                    <p className="text-sm text-gray-500">Get notified before upcoming assessments</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Score Changes</p>
                    <p className="text-sm text-gray-500">Alert when scores drop below threshold</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Weekly Report Summary</p>
                    <p className="text-sm text-gray-500">Receive weekly progress summary via email</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked={false} className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">AI Insights Updates</p>
                    <p className="text-sm text-gray-500">Notify when new insights are available</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked className="sr-only peer" />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <Palette className="h-5 w-5 text-indigo-500" />
                Appearance Settings
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Color Theme
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    <button className="p-4 border-2 border-indigo-500 rounded-lg bg-indigo-50">
                      <div className="h-8 bg-gradient-to-r from-indigo-500 to-indigo-600 rounded mb-2"></div>
                      <span className="text-sm font-medium text-indigo-700">Indigo</span>
                    </button>
                    <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                      <div className="h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded mb-2"></div>
                      <span className="text-sm font-medium text-gray-600">Blue</span>
                    </button>
                    <button className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                      <div className="h-8 bg-gradient-to-r from-teal-500 to-teal-600 rounded mb-2"></div>
                      <span className="text-sm font-medium text-gray-600">Teal</span>
                    </button>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Display Mode
                  </label>
                  <div className="flex gap-3">
                    <button className="flex-1 p-4 border-2 border-indigo-500 rounded-lg bg-indigo-50 text-center">
                      <Globe className="h-6 w-6 mx-auto mb-2 text-indigo-600" />
                      <span className="text-sm font-medium text-indigo-700">Light</span>
                    </button>
                    <button className="flex-1 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
                      <Globe className="h-6 w-6 mx-auto mb-2 text-gray-400" />
                      <span className="text-sm font-medium text-gray-600">Dark</span>
                    </button>
                    <button className="flex-1 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-center">
                      <Globe className="h-6 w-6 mx-auto mb-2 text-gray-400" />
                      <span className="text-sm font-medium text-gray-600">System</span>
                    </button>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Graph Layout
                  </label>
                  <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500">
                    <option value="cose">COSE (Force-directed)</option>
                    <option value="dagre">Dagre (Hierarchical)</option>
                    <option value="circle">Circle</option>
                    <option value="grid">Grid</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                  <Database className="h-5 w-5 text-indigo-500" />
                  Data Management
                </h2>
                
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">Storage Mode</span>
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                        JSON (Development)
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">
                      Data is stored in local JSON files. Use PostgreSQL for production.
                    </p>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">Export All Data</p>
                      <p className="text-sm text-gray-500">Download complete backup as JSON</p>
                    </div>
                    <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                      Export
                    </button>
                  </div>
                  
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">Clear Cache</p>
                      <p className="text-sm text-gray-500">Remove temporary data and insights cache</p>
                    </div>
                    <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
                      Clear
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Danger Zone */}
              <div className="bg-white rounded-xl shadow-sm border border-red-100 p-6">
                <h3 className="font-semibold text-red-700 mb-4 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Danger Zone
                </h3>
                
                <div className="flex items-center justify-between p-4 border border-red-200 rounded-lg bg-red-50">
                  <div>
                    <p className="font-medium text-red-700">Delete All Hospital Data</p>
                    <p className="text-sm text-red-600">This action cannot be undone</p>
                  </div>
                  {!showDeleteConfirm ? (
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                      Delete
                    </button>
                  ) : (
                    <div className="flex gap-2">
                      <button
                        onClick={() => setShowDeleteConfirm(false)}
                        className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
                      >
                        Cancel
                      </button>
                      <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">
                        Confirm Delete
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
