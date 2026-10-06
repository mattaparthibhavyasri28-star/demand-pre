import {
  DailyForecastSummary,
  NearRealTimeUpdate,
  PurchaseRecommendationResponse,
  WasteAnalytics,
  WhatIfSimulationResponse,
  AlertItem,
  SurplusCandidate,
  DonationRecord,
  SustainabilitySummary,
  BranchInfo
} from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error (${res.status}): ${errorText}`);
  }
  return res.json();
}

export const api = {
  async getBranches(): Promise<BranchInfo[]> {
    try {
      return await fetchJson<BranchInfo[]>(`${API_BASE}/branches`);
    } catch {
      return [
        {
          id: 'branch-downtown-01',
          name: 'Downtown Flagship Branch',
          restaurant_name: 'The Green Plate Bistro',
          city: 'Metropolis',
          address: '100 Innovation Avenue'
        }
      ];
    }
  },

  async getDailyForecast(branchId: string, dateStr: string, weather: string = 'Clear', rain: number = 0, holiday: boolean = false): Promise<DailyForecastSummary> {
    return fetchJson<DailyForecastSummary>(
      `${API_BASE}/demand/daily-forecast?branch_id=${branchId}&target_date=${dateStr}&weather_condition=${encodeURIComponent(weather)}&rainfall_mm=${rain}&is_holiday=${holiday}`
    );
  },

  async updateNearRealTime(payload: {
    branch_id: string;
    menu_item_id: string;
    target_date: string;
    current_hour: number;
    cumulative_sales_so_far: number;
    current_weather_condition?: string;
  }): Promise<NearRealTimeUpdate> {
    return fetchJson<NearRealTimeUpdate>(`${API_BASE}/demand/near-real-time-update`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getInventoryRecommendations(branchId: string, planningDate?: string): Promise<PurchaseRecommendationResponse> {
    const query = planningDate ? `&planning_date=${planningDate}` : '';
    return fetchJson<PurchaseRecommendationResponse>(`${API_BASE}/inventory/recommendations?branch_id=${branchId}${query}`);
  },

  async getWasteAnalytics(branchId: string, startDate?: string, endDate?: string): Promise<WasteAnalytics> {
    const params = new URLSearchParams({ branch_id: branchId });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return fetchJson<WasteAnalytics>(`${API_BASE}/waste/analytics?${params.toString()}`);
  },

  async logWaste(payload: {
    branch_id: string;
    menu_item_id: string;
    record_date: string;
    prepared_quantity: number;
    sold_quantity: number;
    remaining_quantity: number;
    wasted_quantity: number;
    waste_reason: string;
    notes?: string;
  }) {
    return fetchJson(`${API_BASE}/waste/log`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async runSimulation(payload: {
    branch_id: string;
    target_date: string;
    weather_scenario: string;
    is_holiday: boolean;
    active_promotion: boolean;
    demand_shift_percentage: number;
    rainfall_override?: number;
    temperature_override?: number;
  }): Promise<WhatIfSimulationResponse> {
    return fetchJson<WhatIfSimulationResponse>(`${API_BASE}/simulation/what-if`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getAlerts(branchId: string): Promise<AlertItem[]> {
    return fetchJson<AlertItem[]>(`${API_BASE}/alerts?branch_id=${branchId}`);
  },

  async acknowledgeAlert(alertId: string) {
    return fetchJson(`${API_BASE}/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify({ alert_id: alertId, status: 'acknowledged' }),
    });
  },

  async getSurplusCandidates(branchId: string): Promise<SurplusCandidate[]> {
    return fetchJson<SurplusCandidate[]>(`${API_BASE}/donations/surplus-candidates?branch_id=${branchId}`);
  },

  async certifyAndDispatchDonation(payload: {
    branch_id: string;
    menu_item_id: string;
    surplus_quantity: number;
    certified_by: string;
    temperature_verified_celsius: number;
    visual_inspection_passed: boolean;
    packaging_intact: boolean;
    recipient_ngo: string;
    contact_phone?: string;
  }): Promise<DonationRecord> {
    return fetchJson<DonationRecord>(`${API_BASE}/donations/certify-and-dispatch`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getDonations(branchId: string): Promise<DonationRecord[]> {
    return fetchJson<DonationRecord[]>(`${API_BASE}/donations?branch_id=${branchId}`);
  },

  async getSustainability(branchId: string, days: number = 30): Promise<SustainabilitySummary> {
    return fetchJson<SustainabilitySummary>(`${API_BASE}/sustainability/summary?branch_id=${branchId}&days=${days}`);
  },

  async sendMockPOSEvent(payload: {
    branch_id: string;
    menu_item_id: string;
    sale_date: string;
    sale_hour: number;
    quantity_sold: number;
    unit_price: number;
  }) {
    return fetchJson(`${API_BASE}/pos/webhook`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
};
