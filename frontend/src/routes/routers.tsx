import { Navigate, createBrowserRouter } from 'react-router-dom';

import { ErrorElement } from '@/features/shared/ErrorElement';
import HomeRoute from '@/routes/HomeRoute';
import { Layout } from '@/features/layout/Layout';
import { NotFound } from '@/routes/NotFound';
import { ProtectedRoute } from './ProtectedRoute';
import SignInRoute from '@/routes/SignInRoute';
import StockAnalyzePage from '../features/stock/pages/StockAnalyzePage';
import { StockHistory } from '@/features/stock/components/StockHistory';

export const routers = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Navigate to="/home" replace /> },
      { path: 'signin', element: <SignInRoute /> },

      {
        path: '',
        element: <ProtectedRoute />,
        errorElement: <ErrorElement />,
        children: [
          { path: 'home', element: <HomeRoute /> },
          { path: 'analyze', element: <StockAnalyzePage /> },
          { path: 'history', element: <StockHistory /> },
          { path: 'account', element: <SignInRoute /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);
