import { clearAuth, setAuth } from './features/auth/store/slice';

import { RouterProvider } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
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
        console.log('setAuth name in app', user.displayName);
        dispatch(
          setAuth({
            isAuthenticated: true,
            name: user.displayName,
            email: user.email,
            token: token,
            loading: false,
            role: null,
            usage: null,
          }),
        );
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
