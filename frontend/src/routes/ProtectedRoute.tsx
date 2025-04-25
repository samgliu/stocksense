import { Navigate, Outlet } from 'react-router';

import { selectAuth } from '@/features/auth/store/selectors';
import { useAppSelector } from '@/hooks/useAppSelector';

export const ProtectedRoute = () => {
  const { isAuthenticated, loading } = useAppSelector(selectAuth);

  if (loading) return <></>;

  return isAuthenticated ? <Outlet /> : <Navigate to="/signin" replace />;
};
