import { Link, useLocation } from 'react-router-dom';
import { Activity, BarChart3, FileSearch, GitCompare, History, Home } from 'lucide-react';

const NAV_ITEMS = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/analyze', label: 'Analyze', icon: Activity },
  { to: '/dashboard', label: 'Dashboard', icon: BarChart3 },
  { to: '/evidence', label: 'Evidence', icon: FileSearch },
  { to: '/compare', label: 'Compare', icon: GitCompare },
  { to: '/history', label: 'History', icon: History },
];

export default function Navbar() {
  const location = useLocation();

  return (
    <header className="glass sticky top-0 z-50 border-x-0 border-t-0">
      <nav aria-label="Primary" className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        {/* Brand */}
        <Link to="/" className="group flex items-center gap-2.5 no-underline" aria-label="Clariq home">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-violet shadow-[0_6px_20px_-6px_rgba(109,111,245,0.9)] transition-transform group-hover:scale-105">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="white" strokeWidth="2.4" strokeLinecap="round" aria-hidden="true">
              <circle cx="11" cy="11" r="6.5" />
              <path d="M16 16l4.5 4.5" />
              <path d="M8.5 11.5l1.8 1.8 3.2-3.6" strokeWidth="2" />
            </svg>
          </div>
          <span className="font-display text-lg font-bold tracking-[0.14em] text-text-primary">
            CLAR<span className="gradient-text">IQ</span>
          </span>
        </Link>

        {/* Links */}
        <div className="flex items-center gap-1 overflow-x-auto rounded-2xl border border-border-subtle bg-bg-secondary/60 p-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                aria-current={active ? 'page' : undefined}
                className={`relative flex shrink-0 items-center gap-1.5 rounded-xl px-2.5 py-1.5 text-sm font-medium no-underline transition-all sm:px-3 ${
                  active
                    ? 'bg-accent/20 text-white shadow-[0_0_0_1px_rgba(109,111,245,0.5)_inset]'
                    : 'text-text-secondary hover:bg-bg-card hover:text-text-primary'
                }`}
              >
                <Icon size={15} aria-hidden="true" />
                <span className={active ? 'inline' : 'hidden lg:inline'}>{label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
