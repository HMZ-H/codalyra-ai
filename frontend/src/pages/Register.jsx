import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form);
      toast.success('Account created!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split">
      <div className="auth-left">
        <div className="auth-left-inner">
          <div className="auth-hero-brand">⚡ Codalyra</div>
          <h1 className="auth-hero-title">Agentic evaluation for the AI era</h1>
          <p className="auth-hero-desc">
            Benchmark AI coding agents with real tasks. Execute, evaluate, and compare — all in one platform.
          </p>
          <div className="auth-features">
            <div className="auth-feature">
              <div className="auth-feature-icon">⟐</div>
              <div>
                <div className="auth-feature-title">Execute Agents</div>
                <div className="auth-feature-desc">Run any AI agent against real coding tasks with git repos</div>
              </div>
            </div>
            <div className="auth-feature">
              <div className="auth-feature-icon">◈</div>
              <div>
                <div className="auth-feature-title">Auto Evaluate</div>
                <div className="auth-feature-desc">Test suites, output matching, and AI-powered code review</div>
              </div>
            </div>
            <div className="auth-feature">
              <div className="auth-feature-icon">△</div>
              <div>
                <div className="auth-feature-title">Track Trajectories</div>
                <div className="auth-feature-desc">Step-by-step execution traces for every agent run</div>
              </div>
            </div>
          </div>
          <div className="auth-hero-terminal">
            <div className="terminal-bar">
              <span className="terminal-dot terminal-dot-red" />
              <span className="terminal-dot terminal-dot-yellow" />
              <span className="terminal-dot terminal-dot-green" />
              <span className="terminal-bar-title">agent run</span>
            </div>
            <div className="terminal-body">
              <div className="terminal-line"><span className="terminal-prompt">$</span> codalyra run --agent gpt-4 --task add-unit-tests</div>
              <div className="terminal-line terminal-muted">Cloning repository...</div>
              <div className="terminal-line terminal-muted">Executing agent on task...</div>
              <div className="terminal-line terminal-success">✓ Run completed in 8.2s</div>
              <div className="terminal-line terminal-muted">Running evaluation...</div>
              <div className="terminal-line terminal-success">✓ Tests passed: 5/5 — Score: 100%</div>
            </div>
          </div>
        </div>
      </div>
      <div className="auth-right">
        <div className="auth-card">
          <h2>Create Account</h2>
          <p className="auth-subtitle">Start evaluating AI agents</p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Full Name</label>
              <input value={form.full_name} onChange={update('full_name')} placeholder="John Doe" />
            </div>
            <div className="form-group">
              <label>Username</label>
              <input value={form.username} onChange={update('username')} placeholder="johndoe" required />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" value={form.email} onChange={update('email')} placeholder="you@example.com" required />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input type="password" value={form.password} onChange={update('password')} placeholder="Min 8 characters" required minLength={8} />
            </div>
            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? 'Creating...' : 'Create Account'}
            </button>
          </form>
          <div className="auth-divider">
            <span>or</span>
          </div>
          <button
            className="btn btn-github btn-full"
            onClick={() => {
              const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
              const redirectUri = import.meta.env.VITE_GITHUB_REDIRECT_URI || 'http://localhost:5173/auth/github/callback';
              window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=read:user+user:email+repo`;
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: '0.5rem' }}>
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            Continue with GitHub
          </button>
          <p className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
