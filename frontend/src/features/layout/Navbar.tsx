import { Link, useLocation } from 'react-router-dom';

import { getInitials } from './helpers';
import { selectAuth } from '@/features/auth/store/selectors';
import { useAppSelector } from '@/hooks/useAppSelector';

export const Navbar: React.FC = () => {
  const { isAuthenticated, name, email, loading } = useAppSelector(selectAuth);
  const location = useLocation();

  const NavItem = ({ to, label }: { to: string; label: string }) => {
    const isActive = location.pathname === to;
    return (
      <Link
        to={to}
        aria-current={isActive ? 'page' : undefined}
        className={`text-sm font-medium transition-colors duration-300 ${
          isActive ? 'text-white underline' : 'text-white/80 hover:text-white'
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <nav className="bg-blue-600 py-4 text-white shadow-md">
      <div className="mx-auto flex max-w-screen-xl items-center justify-between px-6">
        <Link to="/" className="text-2xl font-semibold tracking-tight hover:underline">
          StockSense
        </Link>

        <div className="flex items-center gap-8">
          <div className="hidden gap-6 md:flex">
            <NavItem to="/" label="Home" />
            {isAuthenticated && (
              <>
                <NavItem to="/semantic-search" label="Search" />
                <NavItem to="/analyze" label="Analyze" />
                <NavItem to="/history" label="History" />
              </>
            )}
          </div>

          {/* User Icon and Sign-In Button */}
          <div className="flex items-center gap-4">
            {loading ? (
              <div className="h-9 w-9 animate-pulse rounded-full bg-blue-300 opacity-60" />
            ) : isAuthenticated ? (
              <Link
                to="/account"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-semibold text-blue-700 shadow-lg transition-all hover:opacity-80"
                title={email ?? undefined}
              >
                {getInitials(name, email)}
              </Link>
            ) : (
              <Link
                to="/signin"
                className="rounded-md bg-white px-4 py-2 text-sm font-medium text-blue-700 shadow-md transition-colors hover:bg-blue-100"
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
