export interface AutoTradeTransaction {
  id: string;
  action: 'buy' | 'sell';
  amount: number;
  price: number;
  timestamp: string;
}

export interface HoldingSummary {
  shares: number | null;
  average_cost: number | null;
  current_price: number | null;
  market_value: number | null;
  unrealized_gain: number | null;
  gain_pct: number | null;
}

export interface HoldingSummaryDisplay {
  shares: string;
  average_cost: string;
  current_price: string;
  market_value: string;
  unrealized_gain: string;
  gain_pct: string;
}

export interface UserAutoTradeSubscriptions {
  balance: number | null;
  portfolio_value: number | null;
  total_value: number | null;
  total_return: number | null;
  subscriptions: AutoTradeSubscription[];
}

export interface AutoTradeSubscription {
  id: string;
  user_id: string;
  company_id: string;
  ticker: string;
  frequency: 'hourly' | 'daily' | 'weekly';
  risk_tolerance: 'low' | 'medium' | 'high';
  wash_sale: boolean;
  created_at: string;
  last_run_at: string | null;
  active: boolean;
  company_name?: string | null;
  transactions?: AutoTradeTransaction[];
  holding_summary?: HoldingSummary;
}
