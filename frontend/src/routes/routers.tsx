import HomeRoute from '@/routes/HomeRoute';
import { Layout } from '@/features/layout/Layout';
import { NotFound } from '@/routes/NotFound';
import { ProtectedRoute } from './ProtectedRoute';
import SignInRoute from '@/routes/SignInRoute';
import StockAnalyzePage from '../features/stock/pages/StockAnalyzePage';
import { StockHistory } from '@/features/stock/components/StockHistory';
import { createBrowserRouter } from 'react-router-dom';

export const routers = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <HomeRoute /> },
      { path: 'signin', element: <SignInRoute /> },
      {
        path: 'account',
        element: <SignInRoute />,
      },
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'analyze', element: <StockAnalyzePage /> },
          { path: 'history', element: <StockHistory /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);
