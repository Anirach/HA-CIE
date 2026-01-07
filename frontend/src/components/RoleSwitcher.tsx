/**
 * Role/View Mode Switcher Component.
 * Allows users to toggle between QI Team and Executive views.
 */
import { Users, Briefcase } from 'lucide-react';
import { useRoleStore, ViewMode } from '../store/roleStore';
import clsx from 'clsx';

interface RoleSwitcherProps {
  /**
   * Display mode: 'compact' for header, 'full' for sidebar
   */
  variant?: 'compact' | 'full';
}

export function RoleSwitcher({ variant = 'full' }: RoleSwitcherProps) {
  const { viewMode, setViewMode } = useRoleStore();

  const modes: { value: ViewMode; label: string; shortLabel: string; icon: typeof Users; description: string }[] = [
    {
      value: 'qi_team',
      label: 'QI Team Mode',
      shortLabel: 'QI',
      icon: Users,
      description: 'Full access to all features and technical details',
    },
    {
      value: 'executive',
      label: 'Executive Mode',
      shortLabel: 'Exec',
      icon: Briefcase,
      description: 'Simplified view with key insights and summaries',
    },
  ];

  if (variant === 'compact') {
    return (
      <div className="flex items-center bg-gray-100 rounded-lg p-1">
        {modes.map((mode) => {
          const Icon = mode.icon;
          const isActive = viewMode === mode.value;
          return (
            <button
              key={mode.value}
              onClick={() => setViewMode(mode.value)}
              className={clsx(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all',
                isActive
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              )}
              title={mode.description}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{mode.shortLabel}</span>
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wider px-1">
        View Mode
      </p>
      <div className="space-y-1">
        {modes.map((mode) => {
          const Icon = mode.icon;
          const isActive = viewMode === mode.value;
          return (
            <button
              key={mode.value}
              onClick={() => setViewMode(mode.value)}
              className={clsx(
                'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-left',
                isActive
                  ? 'bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200'
                  : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
              )}
            >
              <div
                className={clsx(
                  'p-1.5 rounded-md',
                  isActive ? 'bg-indigo-100' : 'bg-gray-100'
                )}
              >
                <Icon className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{mode.label}</p>
                <p className="text-xs text-gray-500 truncate">{mode.description}</p>
              </div>
              {isActive && (
                <div className="h-2 w-2 rounded-full bg-indigo-600" />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default RoleSwitcher;

