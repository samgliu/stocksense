import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const dashboardApi = createApi({
  reducerPath: 'dashboardApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1/dashboard`,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('token');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  endpoints: (builder) => ({
    getMonthlySummary: builder.query({
      query: () => '/monthly-summary',
    }),
    getDailyAnalysis: builder.query({
      query: () => '/daily-analysis',
    }),
    getUsageCount: builder.query({
      query: () => '/usage-count',
    }),
    getHistorySummary: builder.query({
      query: () => '/history-summary',
    }),
  }),
});

export const {
  useGetMonthlySummaryQuery,
  useGetDailyAnalysisQuery,
  useGetUsageCountQuery,
  useGetHistorySummaryQuery,
} = dashboardApi;
