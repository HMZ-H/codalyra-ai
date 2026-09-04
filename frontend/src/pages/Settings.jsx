import { useState, useEffect } from 'react';
import { settings as settingsApi } from '../api/client';
import { HiKey, HiTrash, HiCheck, HiArrowLeft } from 'react-icons/hi';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function Settings() {
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

  if (loading) return <div className="page"><div className="loading">Loading settings...</div></div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/dashboard" className="back-link"><HiArrowLeft /> Dashboard</Link>
          <h1>Settings</h1>
        </div>
      </div>

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
