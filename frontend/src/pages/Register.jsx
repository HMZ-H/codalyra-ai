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
          <p className="auth-footer">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
