import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  Brain,
  Building2,
  ChevronRight,
  Cpu,
  GitCompare,
  Layers,
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
    color: '#6366f1',
  },
  {
    icon: Building2,
    title: 'Company Intelligence',
    description: 'Detect hiring signals, growth patterns, and risks across companies.',
    color: '#22c55e',
  },
  {
    icon: Cpu,
    title: 'Technology Intelligence',
    description: 'Evaluate whether a technology is worth learning based on real market evidence.',
    color: '#f59e0b',
  },
  {
    icon: GitCompare,
    title: 'Compare',
    description: 'Side-by-side entity comparison with traceable evidence scoring.',
    color: '#3b82f6',
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
      <section className="relative flex flex-1 flex-col items-center justify-center px-4 py-24">
        {/* Background glow */}
        <div
          className="pointer-events-none absolute left-1/2 top-1/4 -translate-x-1/2 -translate-y-1/2"
          style={{
            width: 600,
            height: 600,
            background: 'radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%)',
          }}
        />

        <div className="animate-fade-in-up relative z-10 mx-auto max-w-4xl text-center">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-bg-card px-4 py-1.5 text-sm text-text-secondary">
            <Sparkles size={14} className="text-accent" />
            Evidence-Powered Decision Intelligence
          </div>

          {/* Headline */}
          <h1 className="mb-4 text-5xl font-extrabold leading-tight tracking-tight md:text-7xl">
            Turn live information
            <br />
            into <span className="gradient-text">clear decisions</span>.
          </h1>

          <p className="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-text-secondary md:text-xl">
            CLARIQ searches live sources across jobs, news, trends, and maps — then normalizes,
            scores, and explains the evidence so you can decide with confidence.
          </p>

          {/* Search Bar */}
          <div className="relative mx-auto max-w-2xl">
            <div className="gradient-border flex items-center gap-3 rounded-2xl bg-bg-card p-2">
              <Search size={20} className="ml-3 shrink-0 text-text-muted" />
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                placeholder="Ask a decision question…"
                className="flex-1 border-none bg-transparent py-3 text-base text-text-primary outline-none placeholder:text-text-muted"
              />
              <button
                onClick={handleAnalyze}
                disabled={question.trim().length < 5}
                className="flex items-center gap-2 rounded-xl bg-accent px-6 py-3 text-sm font-semibold text-white transition-all hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed"
              >
                ANALYZE
                <ArrowRight size={16} />
              </button>
            </div>
          </div>

          {/* Examples */}
          <div className="mt-6 flex flex-wrap justify-center gap-2">
            {EXAMPLE_QUESTIONS.map((ex) => (
              <button
                key={ex}
                onClick={() => handleExample(ex)}
                className="flex items-center gap-1 rounded-lg border border-border bg-bg-card px-3 py-1.5 text-xs text-text-secondary transition-colors hover:border-accent hover:text-accent"
              >
                <ChevronRight size={12} />
                {ex.length > 55 ? ex.slice(0, 55) + '…' : ex}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline */}
      <section className="border-t border-border bg-bg-secondary px-4 py-20">
        <div className="mx-auto max-w-5xl text-center">
          <h2 className="mb-2 text-sm font-semibold uppercase tracking-widest text-accent">
            The Clariq Pipeline
          </h2>
          <p className="mb-12 text-2xl font-bold text-text-primary">
            From question to actionable recommendation
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2">
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step} className="flex items-center gap-2">
                <div className="rounded-lg border border-border bg-bg-card px-4 py-2 text-sm font-medium text-text-secondary transition-colors hover:border-accent hover:text-accent">
                  {step}
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ArrowRight size={14} className="text-text-muted" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Intelligence Modes */}
      <section className="px-4 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-widest text-accent">
              Intelligence Modes
            </h2>
            <p className="text-2xl font-bold text-text-primary">
              Multiple lenses, one evidence engine
            </p>
          </div>
          <div className="stagger-children grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {MODES.map(({ icon: Icon, title, description, color }) => (
              <div key={title} className="card group cursor-pointer p-6">
                <div
                  className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl"
                  style={{ background: `${color}20` }}
                >
                  <Icon size={24} style={{ color }} />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-text-primary">{title}</h3>
                <p className="text-sm leading-relaxed text-text-secondary">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Differentiators */}
      <section className="border-t border-border bg-bg-secondary px-4 py-20">
        <div className="mx-auto max-w-5xl">
          <div className="mb-12 text-center">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-widest text-accent">
              Why Clariq
            </h2>
            <p className="text-2xl font-bold text-text-primary">
              Not a chatbot. Not a search engine.
            </p>
          </div>
          <div className="stagger-children grid gap-8 md:grid-cols-3">
            {[
              {
                icon: Layers,
                title: 'Multi-Source Evidence',
                desc: 'Jobs, News, Web, Trends, Maps — cross-referenced and scored together.',
              },
              {
                icon: Shield,
                title: 'Full Traceability',
                desc: 'Every score traces back to specific evidence with source URLs.',
              },
              {
                icon: Brain,
                title: 'Conflict Detection',
                desc: 'Contradictions are surfaced, not hidden. Make decisions with open eyes.',
              },
              {
                icon: Zap,
                title: 'Live Data',
                desc: 'Powered by SerpApi. Results reflect the real world, right now.',
              },
              {
                icon: TrendingUp,
                title: 'Confidence Scoring',
                desc: 'Source diversity and agreement level produce an honest confidence score.',
              },
              {
                icon: Sparkles,
                title: 'Explainable AI',
                desc: 'Every recommendation has a "Why?" button backed by evidence chains.',
              },
            ].map(({ icon: Icon, title, desc }) => (
              <div key={title} className="flex gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent/10">
                  <Icon size={20} className="text-accent" />
                </div>
                <div>
                  <h3 className="mb-1 font-semibold text-text-primary">{title}</h3>
                  <p className="text-sm text-text-secondary">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border px-4 py-8 text-center text-sm text-text-muted">
        CLARIQ · Evidence-powered decision intelligence · Built for SerpApi Hackathon 2026
      </footer>
    </div>
  );
}
