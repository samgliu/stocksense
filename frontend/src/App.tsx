import { clearAuth, setAuth } from './features/auth/store/slice';

import { onAuthStateChanged } from 'firebase/auth';
import { useEffect } from 'react';
import { RouterProvider } from 'react-router';
import { ToastContainer } from 'react-toastify';
import { useLazyVerifyTokenQuery } from './features/auth/api';
import { auth } from './features/auth/firebase';
import { useAppDispatch } from './hooks/useAppDispatch';
import { routers } from './routes/routers';

export default function App() {
  const dispatch = useAppDispatch();
  const [triggerVerifyToken] = useLazyVerifyTokenQuery();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        const token = await user.getIdToken();
        dispatch(
          setAuth({
            id: '',
            isAuthenticated: true,
            name: user.displayName,
            email: user.email,
            token: token,
            loading: false,
            role: null,
            usage: null,
          }),
        );
        try {
          const backendUser = await triggerVerifyToken().unwrap();

          dispatch(
            setAuth({
              id: backendUser.id,
              isAuthenticated: true,
              name: backendUser.name ?? user.displayName ?? '',
              email: backendUser.email ?? user.email ?? '',
              token,
              loading: false,
              role: backendUser.role,
              usage: backendUser.usage_count_today ?? null,
            }),
          );
        } catch {
          dispatch(clearAuth());
        }
      } else {
        dispatch(clearAuth());
      }
    });

    return () => unsubscribe();
  }, []);

  return (
    <>
      <RouterProvider router={routers} />
      <ToastContainer position="bottom-right" autoClose={3000} />
    </>
  );
}
