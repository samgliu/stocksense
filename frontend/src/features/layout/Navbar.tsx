import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { getInitials } from './helpers';
import { selectAuth } from '@/features/auth/store/selectors';
import { useAppSelector } from '@/hooks/useAppSelector';

export const Navbar: React.FC = () => {
  const { isAuthenticated, name, email, loading } = useAppSelector(selectAuth);
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const NavItem = ({ to, label, onClick }: { to: string; label: string; onClick?: () => void }) => {
    const isActive = location.pathname === to;
    return (
      <Link
        to={to}
        aria-current={isActive ? 'page' : undefined}
        className={`rounded px-3 py-2 text-sm font-medium transition-all select-none ${
          isActive ? 'bg-white/10 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'
        }`}
        onClick={onClick}
      >
        {label}
      </Link>
    );
  };

  // Navigation links
  const navLinks = [
    { to: '/', label: 'Home' },
    ...(isAuthenticated
      ? [
          { to: '/semantic-search', label: 'Search' },
          { to: '/auto-trade', label: 'SmartTrade' },
          { to: '/analyze', label: 'Analyze' },
          { to: '/history', label: 'History' },
        ]
      : []),
  ];

  return (
    <header className="sticky top-0 z-50 bg-blue-600 shadow-sm select-none">
      <div className="mx-auto flex max-w-screen-xl items-center px-4 py-3 sm:px-6">
        {/* Mobile: Logo left, Hamburger right */}
        <div className="flex flex-1 items-center md:block">
          <Link
            to="/"
            className="text-xl font-bold tracking-tight text-white transition select-none hover:opacity-90"
          >
            StockSense
          </Link>
          {/* Hamburger Button (Mobile) */}
          <button
            className="md:hidden flex items-center justify-center p-2 rounded hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-white ml-auto"
            aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((open) => !open)}
          >
            <svg
              className="h-6 w-6 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              {mobileOpen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              )}
            </svg>
          </button>
        </div>

        {/* Right: Nav + User (Desktop) */}
        <div className="hidden md:flex items-center gap-4 ml-auto">
          <nav className="flex items-center gap-1">
            {navLinks.map((link) => (
              <NavItem key={link.to} to={link.to} label={link.label} />
            ))}
          </nav>
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

      {/* Mobile Menu */}
      {mobileOpen && (
        <nav
          className="md:hidden bg-blue-600 px-2 pb-2 pt-1 shadow-lg animate-fade-in"
          aria-label="Mobile navigation"
        >
          <div className="flex flex-col gap-0.5 items-end text-right">
            {navLinks.map((link) => (
              <NavItem
                key={link.to}
                to={link.to}
                label={link.label}
                onClick={() => setMobileOpen(false)}
              />
            ))}
          </div>
          <div className="mt-2 flex flex-col gap-1 items-end text-right">
            {loading ? (
              <div className="h-8 w-8 animate-pulse rounded-full bg-blue-300 opacity-60" />
            ) : isAuthenticated ? (
              <Link
                to="/account"
                className="flex h-8 w-8 items-center justify-center rounded-full bg-white text-xs font-semibold text-blue-700 shadow select-none hover:opacity-90"
                title={email ?? undefined}
                onClick={() => setMobileOpen(false)}
              >
                {getInitials(name, email)}
              </Link>
            ) : (
              <Link
                to="/signin"
                className="rounded bg-white px-3 py-1 text-xs font-medium text-blue-700 shadow-sm transition select-none hover:bg-blue-100"
                onClick={() => setMobileOpen(false)}
              >
                Sign In
              </Link>
            )}
          </div>
        </nav>
      )}
    </header>
  );
};
