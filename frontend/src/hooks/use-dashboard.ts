'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import type { DashboardSummaryResponse } from '@/types/dashboard';

export function useDashboard() {
  return useQuery<DashboardSummaryResponse>({
    queryKey: ['dashboard-summary'],
    queryFn: () => api.get<DashboardSummaryResponse>('/dashboard/summary'),
    staleTime: 60_000,
    refetchOnWindowFocus: false,
  });
}
