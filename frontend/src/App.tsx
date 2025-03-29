import { clearAuth, setAuth } from './features/auth/store/slice';

import { RouterProvider } from 'react-router-dom';
import { auth } from './features/auth/firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { routers } from './routes/routers';
import { useAppDispatch } from './hooks/useAppDispatch';
import { useEffect } from 'react';

export default function App() {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (user) {
        const token = await user.getIdToken();
        dispatch(
          setAuth({
            isAuthenticated: true,
            name: user.displayName,
            email: user.email,
            token: null,
            loading: false,
          }),
        );
      } else {
        dispatch(clearAuth());
      }
    });

    return () => unsubscribe();
  }, []);

  return <RouterProvider router={routers} />;
}
