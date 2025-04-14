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
        className={`rounded px-3 py-2 text-sm font-medium transition-all select-none ${
          isActive ? 'bg-white/10 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="sticky top-0 z-50 bg-blue-600 shadow-sm select-none">
      <div className="mx-auto flex max-w-screen-xl items-center justify-between px-4 py-3 sm:px-6">
        {/* Left: Logo */}
        <Link
          to="/"
          className="text-xl font-bold tracking-tight text-white transition select-none hover:opacity-90"
        >
          StockSense
        </Link>

        {/* Right: Navigation + User */}
        <div className="flex items-center gap-6">
          {/* Nav */}
          <nav className="hidden items-center gap-1 md:flex">
            <NavItem to="/" label="Home" />
            {isAuthenticated && (
              <>
                <NavItem to="/semantic-search" label="Search" />
                <NavItem to="/auto-trade" label="SmartTrade" />
                <NavItem to="/analyze" label="Analyze" />
                <NavItem to="/history" label="History" />
              </>
            )}
          </nav>

          {/* User Icon or Sign In */}
          {loading ? (
            <div className="h-9 w-9 animate-pulse rounded-full bg-blue-300 opacity-60" />
          ) : isAuthenticated ? (
            <Link
              to="/account"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-semibold text-blue-700 shadow select-none hover:opacity-90"
              title={email ?? undefined}
            >
              {getInitials(name, email)}
            </Link>
          ) : (
            <Link
              to="/signin"
              className="rounded-md bg-white px-4 py-2 text-sm font-medium text-blue-700 shadow-sm transition select-none hover:bg-blue-100"
            >
              Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
