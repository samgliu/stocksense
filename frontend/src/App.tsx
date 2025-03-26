import { RouterProvider, createBrowserRouter } from 'react-router-dom';

import HomeRoute from '@/routes/HomeRoute';
import { Layout } from '@/features/layout/Layout';
import SignInRoute from '@/routes/SignInRoute';

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
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
