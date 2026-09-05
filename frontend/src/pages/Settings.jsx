import { useState, useEffect } from 'react';
import { settings as settingsApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { HiKey, HiTrash, HiCheck, HiArrowLeft } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

const PROVIDERS = [
  { key: 'gemini', label: 'Google Gemini', placeholder: 'AIza...', fieldHas: 'has_gemini_key', fieldPreview: 'gemini_key_preview', apiField: 'gemini_api_key' },
  { key: 'openai', label: 'OpenAI', placeholder: 'sk-...', fieldHas: 'has_openai_key', fieldPreview: 'openai_key_preview', apiField: 'openai_api_key' },
  { key: 'anthropic', label: 'Anthropic', placeholder: 'sk-ant-...', fieldHas: 'has_anthropic_key', fieldPreview: 'anthropic_key_preview', apiField: 'anthropic_api_key' },
];

export default function Settings() {
  const { user } = useAuth();
  const [keyStatus, setKeyStatus] = useState(null);
  const [keys, setKeys] = useState({ gemini: '', openai: '', anthropic: '' });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(null);

  useEffect(() => {
    settingsApi.getApiKeyStatus()
      .then((res) => setKeyStatus(res.data))
      .catch(() => toast.error('Failed to load settings'))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (provider) => {
    const p = PROVIDERS.find((pr) => pr.key === provider);
    const val = keys[provider]?.trim();
    if (!val) return;
    setSaving(provider);
    try {
      await settingsApi.updateApiKey({ [p.apiField]: val });
      const res = await settingsApi.getApiKeyStatus();
      setKeyStatus(res.data);
      setKeys((prev) => ({ ...prev, [provider]: '' }));
      toast.success(`${p.label} key saved`);
    } catch {
      toast.error(`Failed to save ${p.label} key`);
    } finally {
      setSaving(null);
    }
  };

  const handleDelete = async (provider) => {
    const p = PROVIDERS.find((pr) => pr.key === provider);
    try {
      await settingsApi.deleteProviderKey(provider);
      const res = await settingsApi.getApiKeyStatus();
      setKeyStatus(res.data);
      toast.success(`${p.label} key removed`);
    } catch {
      toast.error(`Failed to remove ${p.label} key`);
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

      {/* API Keys */}
      <h2 style={{ marginBottom: 16 }}><HiKey style={{ verticalAlign: 'middle', marginRight: 8, color: 'var(--accent)' }} />API Keys</h2>
      <p className="text-muted" style={{ marginBottom: 16, maxWidth: 600 }}>
        Configure API keys for different LLM providers. You can assign specific providers to individual review agents in each project's Agent Config.
      </p>

      {PROVIDERS.map((p) => (
        <div key={p.key} className="card" style={{ maxWidth: 600, marginBottom: 16 }}>
          <div className="card-header">
            <h3 style={{ fontSize: '1rem' }}>{p.label}</h3>
            {keyStatus?.[p.fieldHas] && (
              <span className="badge badge-green" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <HiCheck /> Active
              </span>
            )}
          </div>

          {keyStatus?.[p.fieldHas] && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '8px 0' }}>
              <code style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                {keyStatus[p.fieldPreview]}
              </code>
              <button className="btn-icon btn-danger-ghost" onClick={() => handleDelete(p.key)} title="Remove">
                <HiTrash />
              </button>
            </div>
          )}

          <div className="form-group" style={{ marginTop: 8 }}>
            <input
              type="password"
              value={keys[p.key]}
              onChange={(e) => setKeys((prev) => ({ ...prev, [p.key]: e.target.value }))}
              placeholder={p.placeholder}
            />
          </div>
          <button
            className="btn btn-sm btn-primary"
            onClick={() => handleSave(p.key)}
            disabled={!keys[p.key]?.trim() || saving === p.key}
          >
            {saving === p.key ? 'Saving...' : keyStatus?.[p.fieldHas] ? 'Update Key' : 'Save Key'}
          </button>
        </div>
      ))}

      <p className="text-muted" style={{ maxWidth: 600, fontSize: '0.8rem' }}>
        Keys are encrypted at rest and never exposed in the UI.
      </p>
    </div>
  );
}
