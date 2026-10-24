import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
});

export interface DayAheadRecord {
  startTime: string;
  actual_mw: number;
  forecast_mw: number;
  residual_mw: number;
}

export interface MetricSummary {
  mae_mw: number;
  rmse_mw: number;
  bias_mw: number;
  wape_percent: number;
  data_points: number;
}

export interface DayAheadResponse {
  records: DayAheadRecord[];
  metrics: MetricSummary;
}

export async function getDayAhead(deliveryDate = "2026-01-15"): Promise<DayAheadResponse> {
  const { data } = await apiClient.get<DayAheadResponse>("/day-ahead", {
    params: { delivery_date: deliveryDate },
  });
  return data;
}
