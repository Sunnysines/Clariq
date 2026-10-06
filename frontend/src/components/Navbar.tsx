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
    <nav className="glass sticky top-0 z-50 border-b border-border px-6 py-3">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2 no-underline">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent">
            <span className="text-sm font-bold text-white">C</span>
          </div>
          <span className="text-lg font-bold tracking-wider text-text-primary">
            CLAR<span className="text-accent">IQ</span>
          </span>
        </Link>

        {/* Links */}
        <div className="hidden items-center gap-1 md:flex">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium no-underline transition-colors ${
                  active
                    ? 'bg-accent/15 text-accent'
                    : 'text-text-secondary hover:bg-bg-card hover:text-text-primary'
                }`}
              >
                <Icon size={16} />
                {label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
