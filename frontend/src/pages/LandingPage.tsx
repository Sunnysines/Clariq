import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  Brain,
  Briefcase,
  Building2,
  ChevronRight,
  Cpu,
  GitCompare,
  Globe,
  Layers,
  MapPin,
  Newspaper,
  Search,
  Shield,
  Sparkles,
  TrendingUp,
  Zap,
} from 'lucide-react';

const EXAMPLE_QUESTIONS = [
  'Which Indian city is best for an entry-level AI/ML career in 2026?',
  'Which Indian companies currently show strong AI hiring signals?',
  'Is AI agent development worth learning for a software engineering student in 2026?',
];

const MODES = [
  {
    icon: TrendingUp,
    title: 'Career Intelligence',
    description: 'Compare cities and markets for career decisions using live job, news, and trend data.',
    color: '#6d6ff5',
  },
  {
    icon: Building2,
    title: 'Company Intelligence',
    description: 'Detect hiring signals, growth patterns, and risks across companies.',
    color: '#34d399',
  },
  {
    icon: Cpu,
    title: 'Technology Intelligence',
    description: 'Evaluate whether a technology is worth learning based on real market evidence.',
    color: '#fbbf24',
  },
  {
    icon: GitCompare,
    title: 'Compare',
    description: 'Side-by-side entity comparison with traceable evidence scoring.',
    color: '#60a5fa',
  },
];

const PIPELINE_STEPS = [
  'Understand',
  'Plan Search',
  'Search',
  'Normalize',
  'Verify',
  'Resolve Entities',
  'Analyze Signals',
  'Detect Conflicts',
  'Score',
  'Explain',
  'Recommend',
];

const SOURCES = [
  { icon: Globe, label: 'Google Search' },
  { icon: Briefcase, label: 'Google Jobs' },
  { icon: Newspaper, label: 'Google News' },
  { icon: TrendingUp, label: 'Google Trends' },
  { icon: MapPin, label: 'Google Maps' },
];

const STATS = [
  { value: '5', label: 'SerpApi engines' },
  { value: '11', label: 'pipeline stages' },
  { value: '100%', label: 'traceable evidence' },
  { value: 'Live', label: 'real-time data' },
];

const DIFFERENTIATORS = [
  { icon: Layers, title: 'Multi-Source Evidence', desc: 'Jobs, News, Web, Trends, Maps — cross-referenced and scored together.' },
  { icon: Shield, title: 'Full Traceability', desc: 'Every score traces back to specific evidence with source URLs.' },
  { icon: Brain, title: 'Conflict Detection', desc: 'Contradictions are surfaced, not hidden. Make decisions with open eyes.' },
  { icon: Zap, title: 'Live Data', desc: 'Powered by SerpApi. Results reflect the real world, right now.' },
  { icon: TrendingUp, title: 'Confidence Scoring', desc: 'Source diversity and agreement level produce an honest confidence score.' },
  { icon: Sparkles, title: 'Explainable AI', desc: 'Every recommendation has a "Why?" button backed by evidence chains.' },
];

export default function LandingPage() {
  const [question, setQuestion] = useState('');
  const navigate = useNavigate();

  const handleAnalyze = () => {
    const q = question.trim();
    if (q.length < 5) return;
    navigate(`/analyze?q=${encodeURIComponent(q)}`);
  };

  const handleExample = (ex: string) => {
    setQuestion(ex);
    navigate(`/analyze?q=${encodeURIComponent(ex)}`);
  };

  return (
    <div className="flex min-h-[calc(100vh-60px)] flex-col">
      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center px-4 pb-20 pt-24 md:pt-32">
        <div
          className="pointer-events-none absolute left-1/2 top-24 h-[420px] w-[420px] -translate-x-1/2 rounded-full opacity-60 blur-3xl animate-float"
          style={{ background: 'radial-gradient(circle, rgba(109,111,245,0.35), transparent 70%)' }}
          aria-hidden="true"
        />

        <div className="animate-fade-in-up relative z-10 mx-auto max-w-4xl text-center">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs font-medium text-accent-hover backdrop-blur">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-success opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-success" />
            </span>
            Evidence-Powered Decision Intelligence · Live via SerpApi
          </div>

          <h1 className="mb-5 text-5xl font-bold leading-[1.05] md:text-7xl">
            Turn live information
            <br />
            into <span className="gradient-text">clear decisions</span>.
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-base leading-relaxed text-text-secondary md:text-lg">
            CLARIQ searches live sources across jobs, news, trends, and maps — then normalizes,
            scores, and explains the evidence so you can decide with confidence.
          </p>

          {/* Search Bar */}
          <div className="relative mx-auto max-w-2xl">
            <div className="absolute -inset-1 rounded-3xl bg-gradient-to-r from-accent/40 via-violet/30 to-cyan/30 opacity-60 blur-xl" aria-hidden="true" />
            <div className="gradient-border relative flex items-center gap-2 rounded-2xl bg-bg-card p-2">
              <Search size={20} className="ml-3 shrink-0 text-text-muted" aria-hidden="true" />
              <input
                id="decision-question"
                type="text"
                aria-label="Decision question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                placeholder="Ask a decision question…"
                className="min-w-0 flex-1 border-none bg-transparent py-3 text-base text-text-primary outline-none placeholder:text-text-muted"
              />
              <button
                onClick={handleAnalyze}
                disabled={question.trim().length < 5}
                className="btn-primary shrink-0"
              >
                ANALYZE
                <ArrowRight size={16} aria-hidden="true" />
              </button>
            </div>
          </div>

          {/* Examples */}
          <div className="mt-7 flex flex-wrap justify-center gap-2">
            {EXAMPLE_QUESTIONS.map((ex) => (
              <button
                key={ex}
                onClick={() => handleExample(ex)}
                className="group flex items-center gap-1 rounded-full border border-border bg-bg-card/70 px-3.5 py-1.5 text-xs text-text-secondary backdrop-blur transition-all hover:-translate-y-0.5 hover:border-accent hover:text-white"
              >
                <ChevronRight size={12} className="transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
                {ex.length > 55 ? ex.slice(0, 55) + '…' : ex}
              </button>
            ))}
          </div>
        </div>

        {/* Live sources strip */}
        <div className="relative z-10 mt-16 w-full max-w-4xl">
          <p className="mb-4 text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-text-muted">
            One question · five live engines
          </p>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {SOURCES.map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-2 rounded-xl border border-border-subtle bg-bg-secondary/70 px-4 py-2 text-xs font-medium text-text-secondary backdrop-blur"
              >
                <Icon size={14} className="text-accent-hover" aria-hidden="true" />
                {label}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="px-4">
        <div className="card mx-auto grid max-w-5xl grid-cols-2 divide-border-subtle p-2 md:grid-cols-4 md:divide-x">
          {STATS.map(({ value, label }) => (
            <div key={label} className="px-4 py-5 text-center">
              <div className="gradient-text font-display text-3xl font-bold">{value}</div>
              <div className="mt-1 text-xs uppercase tracking-wider text-text-muted">{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Pipeline */}
      <section className="px-4 py-24">
        <div className="mx-auto max-w-5xl text-center">
          <h2 className="eyebrow mb-2">The Clariq Pipeline</h2>
          <p className="mb-12 text-3xl font-bold text-text-primary">From question to actionable recommendation</p>
          <ol className="grid grid-cols-2 gap-3 text-left sm:grid-cols-3 lg:grid-cols-4">
            {PIPELINE_STEPS.map((step, i) => (
              <li
                key={step}
                className="card card-interactive flex items-center gap-3 px-4 py-3"
              >
                <span className="font-display flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-accent/15 text-xs font-bold text-accent-hover">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <span className="text-sm font-medium text-text-secondary">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Intelligence Modes */}
      <section className="border-y border-border-subtle bg-bg-secondary/50 px-4 py-24">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="eyebrow mb-2">Intelligence Modes</h2>
            <p className="text-3xl font-bold text-text-primary">Multiple lenses, one evidence engine</p>
          </div>
          <div className="stagger-children grid gap-5 md:grid-cols-2 lg:grid-cols-4">
            {MODES.map(({ icon: Icon, title, description, color }) => (
              <div key={title} className="card card-interactive group relative overflow-hidden p-6">
                <div
                  className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full opacity-0 blur-2xl transition-opacity duration-500 group-hover:opacity-100"
                  style={{ background: `${color}55` }}
                  aria-hidden="true"
                />
                <div
                  className="relative mb-5 flex h-12 w-12 items-center justify-center rounded-2xl"
                  style={{ background: `${color}1f`, boxShadow: `0 0 0 1px ${color}40 inset` }}
                >
                  <Icon size={22} style={{ color }} aria-hidden="true" />
                </div>
                <h3 className="relative mb-2 text-lg font-semibold text-text-primary">{title}</h3>
                <p className="relative text-sm leading-relaxed text-text-secondary">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Differentiators */}
      <section className="px-4 py-24">
        <div className="mx-auto max-w-5xl">
          <div className="mb-12 text-center">
            <h2 className="eyebrow mb-2">Why Clariq</h2>
            <p className="text-3xl font-bold text-text-primary">Not a chatbot. Not a search engine.</p>
          </div>
          <div className="stagger-children grid gap-5 md:grid-cols-3">
            {DIFFERENTIATORS.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="card flex flex-col gap-3 p-6">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent/25 to-violet/15">
                  <Icon size={19} className="text-accent-hover" aria-hidden="true" />
                </div>
                <h3 className="font-semibold text-text-primary">{title}</h3>
                <p className="text-sm leading-relaxed text-text-secondary">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border-subtle px-4 py-8 text-center text-sm text-text-muted">
        <span className="font-display font-semibold tracking-[0.14em] text-text-secondary">
          CLAR<span className="text-accent-hover">IQ</span>
        </span>{' '}
        · Evidence-powered decision intelligence · Built for SerpApi Hackathon 2026
      </footer>
    </div>
  );
}
