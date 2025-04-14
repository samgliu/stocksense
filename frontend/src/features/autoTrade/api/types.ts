export interface AutoTradeTransaction {
  id: string;
  action: 'buy' | 'sell';
  amount: number;
  price: number;
  timestamp: string;
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
}
