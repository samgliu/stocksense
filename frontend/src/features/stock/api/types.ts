export interface HistoryItem {
  id: string;
  summary: string;
  created_at: string;
  source_type: string;
  model_used: string;
  text_input: string | null;
}
