import React, { useState } from 'react';
import { auth, provider } from '@/features/auth/firebase';

import { setAuth } from '@/features/auth/store/slice';
import { signInWithPopup } from 'firebase/auth';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { useLazyVerifyTokenQuery } from '@/features/auth/api';
import { useNavigate } from 'react-router-dom';

export const SignIn: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const [triggerVerifyToken] = useLazyVerifyTokenQuery();

  const handleSignIn = async () => {
    try {
      setLoading(true);
      setStatus('');

      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken(true);

      const backendUser = await triggerVerifyToken().unwrap();

      dispatch(
        setAuth({
          isAuthenticated: true,
          name: backendUser.name,
          email: backendUser.email,
          token,
          loading: false,
          role: backendUser.role,
          usage: backendUser.usage_count_today ?? null,
        }),
      );

      navigate('/account');
    } catch (err) {
      console.error('Sign-in error:', err);
      setStatus('❌ Sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-10 flex flex-col items-center">
      <button
        onClick={handleSignIn}
        disabled={loading}
        className="cursor-pointer rounded-md bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? 'Signing in...' : 'Sign in with Google'}
      </button>
      {status && <p className="mt-2 text-sm text-red-500">{status}</p>}
    </div>
  );
};
