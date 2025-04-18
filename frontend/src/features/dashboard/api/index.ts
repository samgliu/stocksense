import { createApi } from '@reduxjs/toolkit/query/react';
import { baseQueryWithErrorHandling } from '@/features/helpers';

export const dashboardApi = createApi({
  reducerPath: 'dashboardApi',
  baseQuery: baseQueryWithErrorHandling(`${import.meta.env.VITE_BACKEND_URL}/api/v1/dashboard`),
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
    getTopCompanies: builder.query({
      query: () => '/top-companies',
    }),
    getNewsSummary: builder.query({
      query: () => '/news-summary',
    }),
    getTopIndustries: builder.query({
      query: () => '/top-industries',
    }),
    getBuySellDaily: builder.query({
      query: () => '/buy-sell-daily',
    }),
    getSnapshotsDaily: builder.query({
      query: () => '/snapshots/daily',
    }),
  }),
});

export const {
  useGetMonthlySummaryQuery,
  useGetDailyAnalysisQuery,
  useGetUsageCountQuery,
  useGetHistorySummaryQuery,
  useGetTopCompaniesQuery,
  useGetNewsSummaryQuery,
  useGetTopIndustriesQuery,
  useGetBuySellDailyQuery,
  useGetSnapshotsDailyQuery,
} = dashboardApi;
