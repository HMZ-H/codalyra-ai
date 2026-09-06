import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { customRules as rulesApi } from '../api/client';
import { HiPlus, HiArrowLeft, HiTrash, HiPencil, HiCheck, HiX } from 'react-icons/hi';
import toast from 'react-hot-toast';

const SEVERITY_OPTIONS = ['critical', 'warning', 'info'];

const EMPTY_RULE = {
  name: '', description: '', pattern: '', severity: 'warning',
  category: 'custom-rule', message: '', suggestion: '', file_pattern: '',
};

export default function CustomRules() {
  const { projectId } = useParams();
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [form, setForm] = useState({ ...EMPTY_RULE });

  const fetchRules = async () => {
    try {
      const res = await rulesApi.list(projectId);
      setRules(res.data);
    } catch {
      toast.error('Failed to load rules');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRules(); }, [projectId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = { ...form };
      if (!data.file_pattern) delete data.file_pattern;
      if (!data.suggestion) delete data.suggestion;
      if (!data.description) delete data.description;

      if (editingRule) {
        await rulesApi.update(projectId, editingRule.id, data);
        toast.success('Rule updated');
      } else {
        await rulesApi.create(projectId, data);
        toast.success('Rule created');
      }
      setForm({ ...EMPTY_RULE });
      setShowForm(false);
      setEditingRule(null);
      fetchRules();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save rule');
    }
  };

  const handleEdit = (rule) => {
    setEditingRule(rule);
    setForm({
      name: rule.name,
      description: rule.description || '',
      pattern: rule.pattern,
      severity: rule.severity,
      category: rule.category,
      message: rule.message,
      suggestion: rule.suggestion || '',
      file_pattern: rule.file_pattern || '',
    });
    setShowForm(true);
  };

  const handleDelete = async (ruleId, name) => {
    if (!confirm(`Delete rule "${name}"?`)) return;
    try {
      await rulesApi.delete(projectId, ruleId);
      toast.success('Rule deleted');
      fetchRules();
    } catch {
      toast.error('Failed to delete rule');
    }
  };

  const handleToggle = async (rule) => {
    try {
      await rulesApi.update(projectId, rule.id, { is_enabled: !rule.is_enabled });
      fetchRules();
    } catch {
      toast.error('Failed to update rule');
    }
  };

  if (loading) return <div className="page"><div className="loading">Loading rules...</div></div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to={`/projects/${projectId}`} className="back-link"><HiArrowLeft /> Project</Link>
          <h1>Custom Rules</h1>
          <p className="text-muted">Define regex-based patterns to flag alongside built-in validators</p>
        </div>
        <button className="btn btn-primary" onClick={() => { setEditingRule(null); setForm({ ...EMPTY_RULE }); setShowForm(true); }}>
          <HiPlus /> Add Rule
        </button>
      </div>

      {showForm && (
        <div className="modal-overlay" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <h3>{editingRule ? 'Edit Rule' : 'New Custom Rule'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="no-console-error" required />
              </div>
              <div className="form-group">
                <label>Regex Pattern</label>
                <input value={form.pattern} onChange={(e) => setForm({ ...form, pattern: e.target.value })} placeholder="console\\.error\\(" required style={{ fontFamily: 'monospace' }} />
              </div>
              <div className="form-group">
                <label>Message</label>
                <input value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} placeholder="Avoid console.error in production code" required />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div className="form-group">
                  <label>Severity</label>
                  <select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
                    {SEVERITY_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Category</label>
                  <input value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} placeholder="custom-rule" />
                </div>
              </div>
              <div className="form-group">
                <label>Suggestion (optional)</label>
                <input value={form.suggestion} onChange={(e) => setForm({ ...form, suggestion: e.target.value })} placeholder="Use a logging library instead" />
              </div>
              <div className="form-group">
                <label>File pattern (optional regex)</label>
                <input value={form.file_pattern} onChange={(e) => setForm({ ...form, file_pattern: e.target.value })} placeholder="\\.py$" style={{ fontFamily: 'monospace' }} />
                <small className="text-muted">Only match files matching this pattern</small>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">{editingRule ? 'Update' : 'Create'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {rules.length === 0 ? (
        <div className="empty-state">
          <h3>No custom rules yet</h3>
          <p>Add regex-based rules to enforce team conventions in code reviews</p>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <HiPlus /> Add Rule
          </button>
        </div>
      ) : (
        <div style={{ maxWidth: 800 }}>
          {rules.map((rule) => (
            <div key={rule.id} className="card" style={{ marginBottom: '0.75rem', opacity: rule.is_enabled ? 1 : 0.6 }}>
              <div className="card-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span className="card-title" style={{ fontSize: '1rem' }}>{rule.name}</span>
                  <span className={`badge badge-${rule.severity === 'critical' ? 'red' : rule.severity === 'warning' ? 'yellow' : 'blue'}`}>
                    {rule.severity}
                  </span>
                  <span className="text-muted text-sm">{rule.category}</span>
                </div>
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                  <button className="btn-icon" onClick={() => handleToggle(rule)} title={rule.is_enabled ? 'Disable' : 'Enable'}>
                    {rule.is_enabled ? <HiCheck style={{ color: '#22c55e' }} /> : <HiX style={{ color: '#888' }} />}
                  </button>
                  <button className="btn-icon" onClick={() => handleEdit(rule)} title="Edit"><HiPencil /></button>
                  <button className="btn-icon btn-danger-ghost" onClick={() => handleDelete(rule.id, rule.name)} title="Delete"><HiTrash /></button>
                </div>
              </div>
              <p className="card-desc">{rule.message}</p>
              <code className="text-sm" style={{ color: 'var(--accent)', display: 'block', marginTop: '0.25rem' }}>{rule.pattern}</code>
              {rule.file_pattern && <span className="text-muted text-sm" style={{ marginTop: '0.25rem', display: 'block' }}>Files: {rule.file_pattern}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
