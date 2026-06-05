const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export class ApiClient {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = localStorage.getItem("access_token");
    
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...(options.headers || {})
      },
      ...options
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
      
      try {
        const error = await response.json();
        throw new Error(error.detail || "API request failed");
      } catch {
        throw new Error(`HTTP ${response.status}: API request failed`);
      }
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  static get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  static post<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined
    });
  }

  static put<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined
    });
  }

  static patch<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined
    });
  }

  static delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

// Specific API methods
export const authApi = {
  login: (email: string, password: string) =>
    ApiClient.post("/auth/login", { email, password }),
  register: (data: Record<string, unknown>) =>
    ApiClient.post("/auth/register", data),
  logout: () => ApiClient.post("/auth/logout")
};

export const vehicleApi = {
  list: () => ApiClient.get("/vehicles"),
  get: (id: number) => ApiClient.get(`/vehicles/${id}`),
  create: (data: Record<string, unknown>) => ApiClient.post("/vehicles", data),
  update: (id: number, data: Record<string, unknown>) =>
    ApiClient.put(`/vehicles/${id}`, data),
  delete: (id: number) => ApiClient.delete(`/vehicles/${id}`)
};

export const measurementApi = {
  list: (vehicleId: number) => ApiClient.get(`/measurements/${vehicleId}`),
  create: (data: Record<string, unknown>) =>
    ApiClient.post("/measurements", data)
};

export const sohApi = {
  getLatest: (vehicleId: number) => ApiClient.get(`/soh/${vehicleId}`),
  getHistory: (vehicleId: number, days?: number) =>
    ApiClient.get(`/soh/${vehicleId}/history?days=${days || 30}`)
};

export const alertApi = {
  list: (vehicleId: number) => ApiClient.get(`/alerts/${vehicleId}`),
  update: (id: number, status: string) =>
    ApiClient.patch(`/alerts/${id}`, { status })
};

export const reportApi = {
  generate: (vehicleId: number, data: Record<string, unknown>) =>
    ApiClient.post(`/reports/${vehicleId}`, data),
  list: (vehicleId: number) => ApiClient.get(`/reports/${vehicleId}`),
  download: (reportId: number) =>
    ApiClient.get(`/reports/${reportId}/download`)
};
