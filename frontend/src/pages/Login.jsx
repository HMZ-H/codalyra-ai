import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed');
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
              <div className="terminal-line"><span className="terminal-prompt">$</span> codalyra run --agent claude-sonnet --task fix-auth-bug</div>
              <div className="terminal-line terminal-muted">Cloning repository...</div>
              <div className="terminal-line terminal-muted">Executing agent on task...</div>
              <div className="terminal-line terminal-success">✓ Run completed in 12.4s</div>
              <div className="terminal-line terminal-muted">Running evaluation...</div>
              <div className="terminal-line terminal-success">✓ Tests passed: 3/3 — Score: 100%</div>
            </div>
          </div>
        </div>
      </div>
      <div className="auth-right">
        <div className="auth-card">
          <h2>Sign In</h2>
          <p className="auth-subtitle">Welcome back to Codalyra</p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary btn-full" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
          <p className="auth-footer">
            Don't have an account? <Link to="/register">Register</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
