import { api } from "./api";

export interface StatsOverview {
  total_sessions: number;
  status_distribution: {
    active: number;
    completed: number;
    abandoned: number;
  };
  top_tags: Array<{
    tag: string;
    count: number;
  }>;
  daily_trend: Array<{
    date: string;
    count: number;
  }>;
  action_completion: {
    total: number;
    completed: number;
    completion_rate: number;
  };
  step_distribution: {
    receive: number;
    clarify: number;
    reframe: number;
    options: number;
    commit: number;
  };
}

export const getStatsOverview = async (): Promise<StatsOverview> => {
  const response = await api.get<StatsOverview>("/stats/overview");
  return response.data;
};

export const exportStats = async (
  format: "json" | "csv" = "json",
): Promise<Blob> => {
  const response = await api.get(`/stats/export?format=${format}`, {
    responseType: "blob",
  });
  return response.data;
};
