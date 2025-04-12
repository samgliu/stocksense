import { clearAuth, setAuth } from '@/features/auth/store/slice';

import { auth } from '@/features/auth/firebase';
import { selectAuth } from '@/features/auth/store/selectors';
import { signOut } from 'firebase/auth';
import { useAppDispatch } from '@/hooks/useAppDispatch';
import { useAppSelector } from '@/hooks/useAppSelector';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVerifyTokenQuery } from '../api';

export const Account = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { name, email, role, usage, token } = useAppSelector(selectAuth);

  const { data, isSuccess } = useVerifyTokenQuery();

  useEffect(() => {
    if (isSuccess && data) {
      dispatch(
        setAuth({
          isAuthenticated: true,
          name: data.name,
          email: data.email ?? email,
          token,
          loading: false,
          role: data.role,
          usage: data.usage_count_today ?? null,
        }),
      );
    }
  }, [isSuccess, data, dispatch, email, name, token]);

  const handleSignOut = async () => {
    await signOut(auth);
    dispatch(clearAuth());
    navigate('/signin');
  };

  return (
    <div className="mx-auto mt-12 max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-xl font-semibold text-gray-800">👤 Account Overview</h2>

      <ul className="space-y-2 text-sm text-gray-700">
        <li>
          <span className="font-medium text-gray-600">Name:</span>{' '}
          {name || <span className="text-gray-400 italic">N/A</span>}
        </li>
        <li>
          <span className="font-medium text-gray-600">Email:</span>{' '}
          {email || <span className="text-gray-400 italic">N/A</span>}
        </li>
        <li>
          <span className="font-medium text-gray-600">Role:</span>{' '}
          <span className="font-medium text-blue-700">{role || 'user'}</span>
        </li>
        {usage !== null && (
          <li>
            <span className="font-medium text-gray-600">Usage Today:</span>{' '}
            <span className="font-medium">
              {usage} / {role !== 'admin' ? 20 : '∞'}
            </span>
          </li>
        )}
      </ul>

      <button
        onClick={handleSignOut}
        className="mt-6 w-full cursor-pointer rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-800 transition hover:bg-gray-200"
      >
        Sign Out
      </button>
    </div>
  );
};
