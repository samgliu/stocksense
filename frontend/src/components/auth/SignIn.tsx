import React, { useEffect, useState } from 'react';
import { User, onAuthStateChanged, signInWithPopup, signOut } from 'firebase/auth';
import { auth, provider } from '@/auth/firebase';

export const SignIn = () => {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<string>('');

  const handleSignIn = async () => {
    try {
      const result = await signInWithPopup(auth, provider);
      const token = await result.user.getIdToken();
      localStorage.setItem('token', token);
      console.log('user signed in. Token stored.');
      setUser(result.user);
      console.log('Calling backend with token:', token);
      const res = await fetch('http://localhost:8000/api/protected', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!res.ok) {
        setStatus('❌ Invalid or unverified');
        console.error('Backend verification failed:', res.status);
        return;
      }
      const data = await res.json();
      setStatus(`✅ Verified as ${data.email}`);
    } catch (error) {
      console.error('Sign-in failed:', error);
      setStatus('❌ Invalid or unverified');
    }
  };

  const handleSignOut = async () => {
    await signOut(auth);
    setUser(null);
    localStorage.removeItem('token');
    setStatus('');
  };

  useEffect(() => {
    onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
  }, []);

  return (
    <div>
      {user ? (
        <div className="flex items-center gap-4">
          <p>Hello, {user.displayName}</p>
          <button onClick={handleSignOut} className="rounded bg-red-500 px-4 py-2 text-white">
            Sign Out
          </button>
        </div>
      ) : (
        <button onClick={handleSignIn} className="rounded bg-blue-600 px-4 py-2 text-white">
          Sign in with Google
        </button>
      )}
      {status && <p className="mt-2">{status}</p>}
    </div>
  );
};
