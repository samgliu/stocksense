import { baseQueryWithErrorHandling } from '@/features/helpers';
import { createApi } from '@reduxjs/toolkit/query/react';
import {
  AnalysisReport,
  CompanyData,
  CompanyHistoricalPrice,
  CompanyNews,
  JobResult,
} from './types';

export const companyApi = createApi({
  reducerPath: 'companyApi',
  baseQuery: baseQueryWithErrorHandling(`${import.meta.env.VITE_BACKEND_URL}/api/v1`),
  endpoints: (builder) => ({
    getCompanyById: builder.query<CompanyData, { id: string; ticker: string }>({
      query: ({ id, ticker }) => `/companies/profile/${id}/${ticker}`,
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
    analyzeCompanyStream: builder.mutation<
      JobResult,
      {
        company_id: string;
        company: CompanyData;
        history?: CompanyHistoricalPrice;
        news?: CompanyNews[];
      }
    >({
      query: ({ company_id, company, history, news }) => ({
        url: `/ws/analyze`,
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
  useAnalyzeCompanyStreamMutation,
  useGetCompanyHistoricalPriceQuery,
  useGetJobStatusQuery,
  useGetCompanyAnalysisReportsQuery,
  useGetCompanyNewsQuery,
} = companyApi;
