import { clearAuth, setAuth } from '@/features/auth/store/slice';

import { Navbar } from '@/features/layout/Navbar';
import { Outlet } from 'react-router-dom';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { useEffect } from 'react';

export const Layout = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) return;

      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/auth/auth`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error();

        const data = await res.json();

        dispatch(
          setAuth({
            isAuthenticated: true,
            name: data.fullname,
            email: data.email,
            loading: false,
            token,
          }),
        );
      } catch {
        dispatch(clearAuth());
      }
    };

    verifyToken();
  }, [dispatch]);

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <Navbar />
      <main className="mx-auto max-w-4xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
};
