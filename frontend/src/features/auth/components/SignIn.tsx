import { auth, provider } from '@/features/auth/firebase';
import { signInWithEmailAndPassword, signInWithPopup } from 'firebase/auth';
import React, { useState } from 'react';

import { useLazyVerifyTokenQuery } from '@/features/auth/api';
import { setAuth } from '@/features/auth/store/slice';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { useNavigate } from 'react-router';

export const SignIn: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const [triggerVerifyToken] = useLazyVerifyTokenQuery();

  const handleGoogleSignIn = async () => {
    try {
      setLoading(true);
      setStatus('');
      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken(true);
      const backendUser = await triggerVerifyToken().unwrap();

      dispatch(
        setAuth({
          id: backendUser.id,
          isAuthenticated: true,
          name: backendUser.name,
          email: backendUser.email,
          token,
          loading: false,
          role: backendUser.role,
          usage: backendUser.usage_count_today ?? null,
        }),
      );

      navigate('/');
    } catch (err) {
      console.error('Google sign-in error:', err);
      setStatus('❌ Google sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnonymousSignIn = async () => {
    try {
      setLoading(true);
      setStatus('');
      const result = await signInWithEmailAndPassword(
        auth,
        import.meta.env.VITE_GUEST_EMAIL,
        import.meta.env.VITE_GUEST_PASSWORD,
      );
      const token = await result.user.getIdToken(true);
      const backendUser = await triggerVerifyToken().unwrap();

      dispatch(
        setAuth({
          id: backendUser.id,
          isAuthenticated: true,
          name: backendUser.name ?? 'Anonymous',
          email: backendUser.email ?? '',
          token,
          loading: false,
          role: backendUser.role,
          usage: backendUser.usage_count_today ?? null,
        }),
      );

      navigate('/');
    } catch (err) {
      console.error('Anonymous sign-in error:', err);
      setStatus('❌ Anonymous sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-10 flex flex-col items-center space-y-4">
      <button
        onClick={handleGoogleSignIn}
        disabled={loading}
        className="cursor-pointer rounded-md bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Signing in...' : 'Sign in with Google'}
      </button>

      <button
        onClick={handleAnonymousSignIn}
        disabled={loading}
        className="cursor-pointer rounded-md bg-gray-600 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Signing in...' : 'Continue as Guest'}
      </button>

      {status && <p className="mt-2 text-sm text-red-500">{status}</p>}
    </div>
  );
};
