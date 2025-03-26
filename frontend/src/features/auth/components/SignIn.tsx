import React, { useEffect, useState } from 'react';
import { auth, provider } from '@/features/auth/firebase';
import { clearAuth, setAuth } from '@/features/auth/store/slices';
import { signInWithPopup, signOut } from 'firebase/auth';

import { BackendUser } from '../store/types';
import { selectAuth } from '@/features/auth/store/selectors';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { useAppSelector } from '@/hooks/useAppSelector';

export const SignIn: React.FC = () => {
  const [status, setStatus] = useState<string>('');
  const dispatch = useAppDispatch();
  const { isAuthenticated, name, email } = useAppSelector(selectAuth);

  const fetchBackendUser = async (token: string) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/v1/auth/auth`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error(`Status: ${res.status}`);

      const data: BackendUser = await res.json();

      dispatch(
        setAuth({
          isAuthenticated: true,
          name: data.name,
          email: data.email,
          loading: false,
          token,
        }),
      );

      setStatus(`✅ Verified as ${data.email}`);
    } catch (err) {
      console.error('Backend verification failed:', err);
      dispatch(clearAuth());
      setStatus('❌ Invalid or unverified');
    }
  };

  const handleSignIn = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken();
      localStorage.setItem('token', token);
      await fetchBackendUser(token);
    } catch (err) {
      console.error('Sign-in failed:', err);
      setStatus('❌ Sign-in failed');
    }
  };

  const handleSignOut = async () => {
    await signOut(auth);
    localStorage.removeItem('token');
    dispatch(clearAuth());
    setStatus('');
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) fetchBackendUser(token);
  }, []);

  return (
    <div className="mt-8 flex flex-col items-center gap-4">
      {isAuthenticated ? (
        <div className="flex flex-col items-center gap-2 rounded-xl border border-gray-200 bg-white px-6 py-4 shadow-sm">
          <p className="text-lg font-medium text-gray-800">Hello, {name || email}</p>
          <button
            onClick={handleSignOut}
            className="rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-200"
          >
            Sign Out
          </button>
        </div>
      ) : (
        <button
          onClick={handleSignIn}
          className="rounded-md bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
        >
          Sign in with Google
        </button>
      )}
      {status && <p className="text-sm text-gray-500">{status}</p>}
    </div>
  );
};
