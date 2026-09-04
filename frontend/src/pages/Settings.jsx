import { useState, useEffect } from 'react';
import { settings as settingsApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { HiKey, HiTrash, HiCheck, HiArrowLeft } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function Settings() {
  const { user } = useAuth();
  const [keyStatus, setKeyStatus] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    settingsApi.getApiKeyStatus()
      .then((res) => setKeyStatus(res.data))
      .catch(() => toast.error('Failed to load settings'))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    if (!apiKey.trim()) return;
    setSaving(true);
    try {
      await settingsApi.updateApiKey(apiKey.trim());
      const res = await settingsApi.getApiKeyStatus();
      setKeyStatus(res.data);
      setApiKey('');
      toast.success('API key saved');
    } catch {
      toast.error('Failed to save API key');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    try {
      await settingsApi.deleteApiKey();
      setKeyStatus({ has_gemini_key: false, gemini_key_preview: null });
      toast.success('API key removed');
    } catch {
      toast.error('Failed to remove API key');
    }
  };

  const handleConnectGithub = () => {
    const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID;
    const redirectUri = encodeURIComponent(window.location.origin + '/auth/github/callback');
    window.location.href = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=read:user+user:email+repo&state=connect`;
  };

  if (loading) return <div className="page"><div className="loading">Loading settings...</div></div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/dashboard" className="back-link"><HiArrowLeft /> Dashboard</Link>
          <h1>Settings</h1>
        </div>
      </div>

      {/* GitHub Connection */}
      <div className="card" style={{ maxWidth: 600, marginBottom: 24 }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--accent)">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            GitHub Account
          </h3>
        </div>

        {user?.github_username ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
            {user.avatar_url && <img src={user.avatar_url} alt="" style={{ width: 32, height: 32, borderRadius: '50%' }} />}
            <div>
              <div className="font-medium">{user.github_username}</div>
              <div className="text-sm text-muted">GitHub account connected</div>
            </div>
            <span className="badge badge-green" style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 4 }}>
              <HiCheck /> Connected
            </span>
          </div>
        ) : (
          <>
            <p className="card-desc">
              Connect your GitHub account to review PRs directly, browse repos, and enable webhook-triggered reviews.
            </p>
            <button
              className="btn btn-github"
              onClick={handleConnectGithub}
              style={{ marginTop: 8 }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style={{ marginRight: 8 }}>
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              Connect GitHub Account
            </button>
          </>
        )}
      </div>

      {/* Gemini API Key */}
      <div className="card" style={{ maxWidth: 600 }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <HiKey style={{ color: 'var(--accent)' }} /> Gemini API Key
          </h3>
        </div>
        <p className="card-desc">
          Provide your own Google Gemini API key. When set, reviews use your key instead of the shared server key.
        </p>

        {keyStatus?.has_gemini_key ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <span className="badge badge-green" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <HiCheck /> Active
            </span>
            <code style={{ color: 'var(--text-muted)', fontSize: 13 }}>
              {keyStatus.gemini_key_preview}
            </code>
            <button className="btn-icon btn-danger-ghost" onClick={handleDelete} title="Remove API key">
              <HiTrash />
            </button>
          </div>
        ) : (
          <div className="badge badge-gray" style={{ marginBottom: 16 }}>
            No key set — using server default
          </div>
        )}

        <div className="form-group">
          <label>
            {keyStatus?.has_gemini_key ? 'Replace API Key' : 'Add API Key'}
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="AIza..."
          />
          <div className="form-hint">Your key is encrypted at rest and never exposed in the UI.</div>
        </div>

        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={!apiKey.trim() || saving}
        >
          {saving ? 'Saving...' : 'Save Key'}
        </button>
      </div>
    </div>
  );
}
