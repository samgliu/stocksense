import { Navigate, createHashRouter } from 'react-router-dom';

import { CompanyProfile } from '@/features/company/components/CompanyProfile';
import { Layout } from '@/features/layout/Layout';
import { SemanticSearch } from '@/features/search/components/SemanticSearch';
import { ErrorElement } from '@/features/shared/ErrorElement';
import { StockHistory } from '@/features/stock/components/StockHistory';
import AccountRoute from '@/routes/AccountRoute';
import AutoTraderRoute from '@/routes/AutoTraderRoute';
import HomeRoute from '@/routes/HomeRoute';
import { NotFound } from '@/routes/NotFound';
import SignInRoute from '@/routes/SignInRoute';
import StockAnalyzePage from '../features/stock/pages/StockAnalyzePage';
import { ProtectedRoute } from './ProtectedRoute';

export const routers = createHashRouter([
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
          { path: 'semantic-search', element: <SemanticSearch /> },
          { path: 'company/profile/:id/:ticker', element: <CompanyProfile /> },
          { path: 'auto-trade', element: <AutoTraderRoute /> },
          { path: 'analyze', element: <StockAnalyzePage /> },
          { path: 'history', element: <StockHistory /> },
          { path: 'account', element: <AccountRoute /> },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);
