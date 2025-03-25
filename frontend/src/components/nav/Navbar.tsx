import { auth, provider } from '../../auth/firebase';

import React from 'react';
import { SignIn } from '../auth/SignIn';

export const Navbar = () => {
  return (
    <nav className="bg-blue-600 p-4">
      <SignIn />
    </nav>
  );
};
