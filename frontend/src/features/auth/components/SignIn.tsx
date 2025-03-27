import React, { useEffect, useState } from 'react';
import { auth, provider } from '@/features/auth/firebase';
import { clearAuth, setAuth } from '@/features/auth/store/slice';
import { signInWithPopup, signOut } from 'firebase/auth';

import { BackendUser } from '../store/types';
import { selectAuth } from '@/features/auth/store/selectors';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { useAppSelector } from '@/hooks/useAppSelector';

export const SignIn: React.FC = () => {
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [role, setRole] = useState<'admin' | 'user' | ''>('');
  const [usage, setUsage] = useState<number | null>(null);

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

      setRole(data.role);
      setUsage(data.usage_count_today ?? null);
      setStatus(`✅ Verified as ${data.email}`);
    } catch (err) {
      console.error('Backend verification failed:', err);
      dispatch(clearAuth());
      setStatus('❌ Invalid or unverified');
    }
  };

  const handleSignIn = async () => {
    try {
      setLoading(true);
      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken();
      localStorage.setItem('token', token);
      await fetchBackendUser(token);
    } catch (err) {
      console.error('Sign-in failed:', err);
      setStatus('❌ Sign-in failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await signOut(auth);
    localStorage.removeItem('token');
    dispatch(clearAuth());
    setRole('');
    setUsage(null);
    setStatus('');
  };

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) fetchBackendUser(token);
  }, []);

  return (
    <div className="mt-10 flex flex-col items-center gap-6">
      {isAuthenticated ? (
        <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-md">
          <p className="mb-2 text-lg font-semibold text-gray-800">👋 Hello, {name || email}</p>
          <p className="text-sm text-gray-600">
            Role: <span className="font-medium text-blue-700">{role}</span>
          </p>
          {usage !== null && (
            <p className="mt-1 text-sm text-gray-600">
              Usage today:{' '}
              <span className="font-medium">
                {usage} / {role === 'user' ? 1 : '∞'}
              </span>
            </p>
          )}

          <button
            onClick={handleSignOut}
            className="mt-4 w-full cursor-pointer rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition hover:bg-gray-200"
          >
            Sign Out
          </button>
        </div>
      ) : (
        <button
          onClick={handleSignIn}
          disabled={loading}
          className="cursor-pointer rounded-md bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? 'Signing in...' : 'Sign in with Google'}
        </button>
      )}
      {status && <p className="text-sm text-gray-500">{status}</p>}
    </div>
  );
};
