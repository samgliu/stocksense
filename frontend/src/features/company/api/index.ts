import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { auth } from '@/features/auth/firebase';

export interface CompanyData {
  id: string;
  ticker: string;
  name: string;
  shortname?: string;
  current_price?: number;
  market_cap?: number;
  summary?: string;
  image?: string;
  sector?: string;
  industry?: string;
  website?: string;
  ceo?: string;
  ipo_date?: string;
  address?: string;
  city?: string;
  state?: string;
  zip?: string;
  phone?: string;
  exchange?: string;
  country?: string;
  fulltime_employees?: number;
}

export interface CompanyAnalysisResult {
  analysis: {
    insights: string;
    prediction: {};
  };
}

export type CompanyHistoricalPrice = { date: string; close: number }[];

export interface JobResult {
  status: string;
  job_id: string;
}

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
      query: ({ id, ticker }) => `/companies/${id}/${ticker}`,
    }),
    getCompanyHistoricalPrice: builder.query<
      CompanyHistoricalPrice,
      { exchange: string; ticker: string }
    >({
      query: ({ ticker, exchange }) => `/companies/historical/${exchange}/${ticker}`,
    }),
    analyzeCompany: builder.mutation<
      JobResult,
      { company_id: string; company: CompanyData; history?: CompanyHistoricalPrice }
    >({
      query: ({ company_id, company, history }) => ({
        url: `/companies/analyze`,
        method: 'POST',
        body: { company_id, company, history },
      }),
    }),
    getJobStatus: builder.query<{ job_id?: string; status: string; result?: string }, string>({
      query: (jobId) => `/worker/job-status/${jobId}`,
    }),
  }),
});

export const {
  useGetCompanyByIdQuery,
  useAnalyzeCompanyMutation,
  useGetCompanyHistoricalPriceQuery,
  useGetJobStatusQuery,
} = companyApi;
