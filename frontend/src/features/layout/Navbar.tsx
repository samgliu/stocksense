import { Link, useLocation } from 'react-router-dom';

import { selectAuth } from '@/features/auth/store/selectors';
import { useAppSelector } from '@/hooks/useAppSelector';

export const Navbar: React.FC = () => {
  const { isAuthenticated, name, email, loading } = useAppSelector(selectAuth);
  const location = useLocation();

  const getInitials = () => {
    if (name) {
      return name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase();
    }
    if (email) {
      return email[0]?.toUpperCase() ?? '?';
    }
    return '?';
  };

  const NavLink = ({ to, label }: { to: string; label: string }) => (
    <Link
      to={to}
      className={`text-sm font-medium transition hover:underline ${
        location.pathname === to ? 'text-white underline' : 'text-white/80'
      }`}
    >
      {label}
    </Link>
  );

  return (
    <nav className="bg-blue-600 text-white shadow-md">
      <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-lg font-semibold hover:underline">
          StockSense
        </Link>

        <div className="flex items-center gap-6">
          <NavLink to="/" label="Home" />
          {isAuthenticated && <NavLink to="/analyze" label="Analyze" />}

          <div className="flex items-center gap-4">
            {loading ? (
              <div className="h-9 w-9 animate-pulse rounded-full bg-blue-300 opacity-60" />
            ) : isAuthenticated ? (
              <Link
                to="/account"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-semibold text-blue-700 shadow transition hover:opacity-90"
                title={email ?? undefined}
              >
                {getInitials()}
              </Link>
            ) : (
              <Link
                to="/signin"
                className="rounded-md bg-white px-4 py-1.5 text-sm font-medium text-blue-700 shadow-sm transition hover:bg-blue-100"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
