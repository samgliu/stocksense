import { Navigate, createHashRouter } from 'react-router-dom';

import AccountRoute from '@/routes/AccountRoute';
import AutoTraderRoute from '@/routes/AutoTraderRoute';
import { CompanyProfile } from '@/features/company/components/CompanyProfile';
import { ErrorElement } from '@/features/shared/ErrorElement';
import HomeRoute from '@/routes/HomeRoute';
import { Layout } from '@/features/layout/Layout';
import { NotFound } from '@/routes/NotFound';
import { ProtectedRoute } from './ProtectedRoute';
import { SemanticSearch } from '@/features/search/components/SemanticSearch';
import SignInRoute from '@/routes/SignInRoute';
import StockAnalyzePage from '../features/stock/pages/StockAnalyzePage';
import { StockHistory } from '@/features/stock/components/StockHistory';

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
