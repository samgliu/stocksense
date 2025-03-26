import { RouterProvider, createBrowserRouter } from 'react-router-dom';

import HomeRoute from '@/routes/HomeRoute';
import { Layout } from '@/features/layout/Layout';
import { NotFound } from '@/routes/NotFound';
import { ProtectedRoute } from './routes/ProtectedRoute';
import SignInRoute from '@/routes/SignInRoute';
import StockAnalyzePage from './features/stock/pages/StockAnalyzePage';

const router = createBrowserRouter([
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
        children: [{ path: 'analyze', element: <StockAnalyzePage /> }],
      },
    ],
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
