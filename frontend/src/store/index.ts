import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: "platform_admin" | "dealer" | "fleet_manager" | "read_only";
  is_active: boolean;
  created_at: string;
}

export interface Vehicle {
  id: number;
  vin: string;
  brand: string;
  model: string;
  year: number;
  mileage: number;
  color?: string;
  is_active: boolean;
  created_at: string;
}

export interface SOHRecord {
  id: number;
  vehicle_id: number;
  soh_percentage: number;
  soc_percentage?: number;
  cycle_count?: number;
  health_status: "pass" | "warning" | "fail";
  calculated_at: string;
}

export interface Alert {
  id: number;
  vehicle_id: number;
  alert_type: string;
  severity: "info" | "warning" | "critical";
  status: "open" | "acknowledged" | "resolved";
  title: string;
  message: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
}

interface VehicleState {
  vehicles: Vehicle[];
  selectedVehicle: Vehicle | null;
  isLoading: boolean;
  error: string | null;

  setVehicles: (vehicles: Vehicle[]) => void;
  addVehicle: (vehicle: Vehicle) => void;
  setSelectedVehicle: (vehicle: Vehicle | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

interface SOHState {
  sohRecords: SOHRecord[];
  currentSOH: SOHRecord | null;
  isLoading: boolean;
  error: string | null;

  setSOHRecords: (records: SOHRecord[]) => void;
  setCurrentSOH: (record: SOHRecord | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

interface AlertState {
  alerts: Alert[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;

  setAlerts: (alerts: Alert[]) => void;
  addAlert: (alert: Alert) => void;
  updateAlert: (id: number, updates: Partial<Alert>) => void;
  setUnreadCount: (count: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// Auth Store
export const useAuthStore = create<AuthState>(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      logout: () =>
        set({ user: null, token: null, isAuthenticated: false, error: null })
    }),
    {
      name: "auth-store",
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);

// Vehicle Store
export const useVehicleStore = create<VehicleState>((set) => ({
  vehicles: [],
  selectedVehicle: null,
  isLoading: false,
  error: null,

  setVehicles: (vehicles) => set({ vehicles }),
  addVehicle: (vehicle) =>
    set((state) => ({ vehicles: [...state.vehicles, vehicle] })),
  setSelectedVehicle: (vehicle) => set({ selectedVehicle: vehicle }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error })
}));

// SOH Store
export const useSOHStore = create<SOHState>((set) => ({
  sohRecords: [],
  currentSOH: null,
  isLoading: false,
  error: null,

  setSOHRecords: (records) => set({ sohRecords: records }),
  setCurrentSOH: (record) => set({ currentSOH: record }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error })
}));

// Alert Store
export const useAlertStore = create<AlertState>((set) => ({
  alerts: [],
  unreadCount: 0,
  isLoading: false,
  error: null,

  setAlerts: (alerts) => set({ alerts }),
  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
      unreadCount: state.unreadCount + 1
    })),
  updateAlert: (id, updates) =>
    set((state) => ({
      alerts: state.alerts.map((alert) =>
        alert.id === id ? { ...alert, ...updates } : alert
      )
    })),
  setUnreadCount: (count) => set({ unreadCount: count }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error })
}));
