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

export interface AnalysisReport {
  id: string;
  company_id: string;
  ticker: string;
  exchange: string;
  model_version: string;
  current_price: number;
  min_price: number;
  max_price: number;
  avg_price: number;
  time_horizon: string;
  prediction_json: Record<string, any>;
  insights: string;
  summary: string;
  created_at: string;
}

export type CompanyNews = {
  title: string;
  description?: string;
  snippet?: string;
  url: string;
  image_url?: string;
  published_at: string;
  source?: string;
  language?: string;
  categories?: string[];
  relevance_score?: string;
};
