import {
  AnalysisReport,
  CompanyData,
  CompanyHistoricalPrice,
  CompanyNews,
  JobResult,
} from './types';
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { auth } from '@/features/auth/firebase';

export const companyApi = createApi({
  reducerPath: 'companyApi',
  baseQuery: fetchBaseQuery({
    baseUrl: `${import.meta.env.VITE_BACKEND_URL}/api/v1`,
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
    getCompanyById: builder.query<CompanyData, { id: string; ticker: string }>({
      query: ({ id, ticker }) => `/companies/profile/{${id}/${ticker}`,
    }),
    getCompanyHistoricalPrice: builder.query<
      CompanyHistoricalPrice,
      { exchange: string; ticker: string }
    >({
      query: ({ ticker, exchange }) => `/companies/historical/${exchange}/${ticker}`,
    }),
    analyzeCompany: builder.mutation<
      JobResult,
      {
        company_id: string;
        company: CompanyData;
        history?: CompanyHistoricalPrice;
        news?: CompanyNews[];
      }
    >({
      query: ({ company_id, company, history, news }) => ({
        url: `/companies/analyze`,
        method: 'POST',
        body: { company_id, company, history, news },
      }),
    }),
    getJobStatus: builder.query<{ job_id?: string; status: string; result?: string }, string>({
      query: (jobId) => `/worker/job-status/${jobId}`,
    }),
    getCompanyAnalysisReports: builder.query<AnalysisReport[], string>({
      query: (companyId) => `/companies/analysis-reports/${companyId}`,
    }),
    getCompanyNews: builder.query<CompanyNews[], { companyId: string; companyName: string }>({
      query: ({ companyId, companyName }) =>
        `/companies/news/${companyId}?company_name=${companyName}`,
    }),
  }),
});

export const {
  useGetCompanyByIdQuery,
  useAnalyzeCompanyMutation,
  useGetCompanyHistoricalPriceQuery,
  useGetJobStatusQuery,
  useGetCompanyAnalysisReportsQuery,
  useGetCompanyNewsQuery,
} = companyApi;
