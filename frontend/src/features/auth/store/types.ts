export interface BackendUser {
  uid: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  usage_count_today?: number;
}
