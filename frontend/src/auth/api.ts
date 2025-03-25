import { UserCredential, signInWithPopup } from 'firebase/auth';
import { auth, provider } from './firebase';

export const signIn = async (): Promise<void> => {
  try {
    const result: UserCredential = await signInWithPopup(auth, provider);
    const token = await result.user.getIdToken();

    if (token) {
      localStorage.setItem('token', token);
      console.log('User signed in. Token stored.');
    }
  } catch (error) {
    console.error('Error during sign-in:', error);
  }
};
