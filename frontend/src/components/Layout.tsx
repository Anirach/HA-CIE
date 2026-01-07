/**
 * Main application layout with sidebar and header.
 * Includes role-based navigation filtering and view mode switcher.
 */
import { ReactNode, useMemo } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  GitBranch,
  Sliders,
  Lightbulb,
  FileText,
  Upload,
  Settings,
  LogOut,
  Building2,
  Menu,
  X,
  Laptop,
} from 'lucide-react';
import { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useRoleStore } from '../store/roleStore';
import { UserRole } from '../types/auth';
import { Feature } from '../utils/roleAccess';
import { RoleSwitcher } from './RoleSwitcher';
import clsx from 'clsx';

interface LayoutProps {
  children: ReactNode;
}

interface NavItem {
  path: string;
  label: string;
  icon: typeof LayoutDashboard;
  /**
   * Required feature(s) to show this nav item
   * If undefined, always shown
   */
  requiredFeature?: Feature;
  /**
   * Only show in QI Team mode
   */
  qiTeamOnly?: boolean;
}

const navItems: NavItem[] = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/graph', label: 'Causal Graph', icon: GitBranch },
  { path: '/simulator', label: 'Simulator', icon: Sliders },
  { path: '/insights', label: 'AI Insights', icon: Lightbulb },
  { path: '/reports', label: 'Reports', icon: FileText },
  { path: '/digital-health', label: 'Digital Health', icon: Laptop, qiTeamOnly: true },
  { path: '/import', label: 'Import Data', icon: Upload, qiTeamOnly: true, requiredFeature: Feature.DATA_IMPORT },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const { viewMode, isQITeamView } = useRoleStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Filter nav items based on current view mode
  const filteredNavItems = useMemo(() => {
    return navItems.filter((item) => {
      // If item is QI Team only and we're not in QI mode, hide it
      if (item.qiTeamOnly && !isQITeamView()) {
        return false;
      }
      return true;
    });
  }, [viewMode, isQITeamView]);

  const getModeLabel = () => {
    return viewMode === 'qi_team' ? 'QI Team' : 'Executive';
  };

  const getModeColor = () => {
    return viewMode === 'qi_team' ? 'bg-indigo-100 text-indigo-700' : 'bg-amber-100 text-amber-700';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-200 ease-in-out lg:translate-x-0',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-4 border-b border-gray-200">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <Building2 className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">HA-CIE</h1>
              <p className="text-xs text-gray-500">Accreditation Analytics</p>
            </div>
            <button
              className="ml-auto p-1 rounded lg:hidden hover:bg-gray-100"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="h-5 w-5 text-gray-500" />
            </button>
          </div>

          {/* View Mode Indicator (Mobile) */}
          <div className="px-4 pt-4 lg:hidden">
            <div className={clsx('px-3 py-2 rounded-lg text-center text-sm font-medium', getModeColor())}>
              {getModeLabel()} View
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
            {filteredNavItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={clsx(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors',
                    isActive
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                  {item.qiTeamOnly && (
                    <span className="ml-auto text-xs bg-indigo-100 text-indigo-600 px-1.5 py-0.5 rounded">
                      QI
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* View Mode Switcher */}
          <div className="px-4 py-3 border-t border-gray-200">
            <RoleSwitcher variant="full" />
          </div>

          {/* User Section */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center gap-3 px-3 py-2">
              <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center">
                <span className="text-indigo-700 font-medium text-sm">
                  {user?.name?.charAt(0).toUpperCase() || 'U'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.role === UserRole.QI_TEAM ? 'QI Team Member' : 'Executive'}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:pl-64">
        {/* Top Header */}
        <header className="sticky top-0 z-30 bg-white border-b border-gray-200">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              className="p-2 rounded-lg hover:bg-gray-100 lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-6 w-6 text-gray-600" />
            </button>
            
            <div className="flex-1 lg:hidden text-center">
              <h1 className="text-lg font-semibold text-gray-900">HA-CIE</h1>
            </div>
            
            {/* Desktop Header Content */}
            <div className="hidden lg:flex items-center gap-4 flex-1">
              {/* Current Mode Badge */}
              <div className={clsx('px-3 py-1.5 rounded-full text-sm font-medium', getModeColor())}>
                {getModeLabel()} View
              </div>
            </div>
            
            {/* Quick Role Switcher (Desktop) */}
            <div className="hidden lg:block">
              <RoleSwitcher variant="compact" />
            </div>
            
            <div className="w-10 lg:hidden" />
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}

export default Layout;
