import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { auth } from '@/features/auth/firebase';

export const dashboardApi = createApi({
  reducerPath: 'dashboardApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1/dashboard`,
    prepareHeaders: async (headers) => {
      const user = auth.currentUser;
      if (user) {
        const token = await user.getIdToken();
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
    getTopCompanies: builder.query({
      query: () => '/top-companies',
    }),
    getNewsSummary: builder.query({
      query: () => '/news-summary',
    }),
    getTopIndustries: builder.query({
      query: () => '/top-industries',
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
} = dashboardApi;
