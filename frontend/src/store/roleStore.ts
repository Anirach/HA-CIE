/**
 * Role/View Mode store using Zustand.
 * Allows users to switch between QI Team and Executive views.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserRole } from '../types/auth';

export type ViewMode = 'qi_team' | 'executive';

interface RoleState {
  /**
   * Current view mode (can be different from user's actual role for demo purposes)
   */
  viewMode: ViewMode;
  
  /**
   * Set the view mode
   */
  setViewMode: (mode: ViewMode) => void;
  
  /**
   * Check if current view is QI Team mode
   */
  isQITeamView: () => boolean;
  
  /**
   * Check if current view is Executive mode
   */
  isExecutiveView: () => boolean;
  
  /**
   * Reset view mode to match user's actual role
   */
  resetToUserRole: (userRole: UserRole | undefined) => void;
}

export const useRoleStore = create<RoleState>()(
  persist(
    (set, get) => ({
      viewMode: 'qi_team',
      
      setViewMode: (mode: ViewMode) => {
        set({ viewMode: mode });
      },
      
      isQITeamView: () => {
        return get().viewMode === 'qi_team';
      },
      
      isExecutiveView: () => {
        return get().viewMode === 'executive';
      },
      
      resetToUserRole: (userRole: UserRole | undefined) => {
        if (userRole === UserRole.EXECUTIVE) {
          set({ viewMode: 'executive' });
        } else {
          set({ viewMode: 'qi_team' });
        }
      },
    }),
    {
      name: 'hacie-role-store',
    }
  )
);

export default useRoleStore;


