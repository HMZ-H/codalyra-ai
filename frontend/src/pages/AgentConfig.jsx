import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { agentConfigs, projects as projectsApi } from '../api/client';
import { HiArrowLeft, HiCog, HiRefresh, HiCheck, HiX } from 'react-icons/hi';
import toast from 'react-hot-toast';

const AGENT_LABELS = {
  logic: { name: 'Logic Agent', desc: 'Detects logical bugs, off-by-one errors, race conditions' },
  performance: { name: 'Performance Agent', desc: 'Finds N+1 queries, memory leaks, algorithmic issues' },
  quality: { name: 'Quality Agent', desc: 'Reviews code maintainability, naming, DRY violations' },
  security: { name: 'Security Agent', desc: 'Audits for OWASP Top 10 vulnerabilities' },
};

export default function AgentConfig() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(null);
  const [editPrompt, setEditPrompt] = useState('');
  const [editTemp, setEditTemp] = useState(0.2);
  const [editProvider, setEditProvider] = useState('');
  const [editModel, setEditModel] = useState('');
  const [providers, setProviders] = useState(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [agentsRes, projRes, provRes] = await Promise.all([
        agentConfigs.list(projectId),
        projectsApi.get(projectId),
        agentConfigs.providers(projectId),
      ]);
      setAgents(agentsRes.data);
      setProject(projRes.data);
      setProviders(provRes.data);
    } catch {
      toast.error('Failed to load agent configs');
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (agent) => {
    setEditing(agent.agent_type);
    setEditPrompt(agent.custom_prompt || agent.default_prompt);
    setEditTemp(agent.temperature);
    setEditProvider(agent.provider || '');
    setEditModel(agent.model_name || '');
  };

  const cancelEdit = () => {
    setEditing(null);
    setEditPrompt('');
    setEditTemp(0.2);
    setEditProvider('');
    setEditModel('');
  };

  const saveConfig = async (agentType) => {
    setSaving(true);
    try {
      const agent = agents.find((a) => a.agent_type === agentType);
      const isDefault = editPrompt.trim() === agent.default_prompt.trim();
      await agentConfigs.update(projectId, agentType, {
        custom_prompt: isDefault ? null : editPrompt,
        temperature: editTemp,
        provider: editProvider || null,
        model_name: editModel || null,
      });
      toast.success(`${AGENT_LABELS[agentType].name} updated`);
      setEditing(null);
      loadData();
    } catch {
      toast.error('Failed to save config');
    } finally {
      setSaving(false);
    }
  };

  const resetConfig = async (agentType) => {
    try {
      await agentConfigs.reset(projectId, agentType);
      toast.success(`${AGENT_LABELS[agentType].name} reset to defaults`);
      loadData();
    } catch {
      toast.error('Failed to reset config');
    }
  };

  const toggleAgent = async (agentType, currentEnabled) => {
    try {
      await agentConfigs.update(projectId, agentType, { is_enabled: !currentEnabled });
      toast.success(`${AGENT_LABELS[agentType].name} ${!currentEnabled ? 'enabled' : 'disabled'}`);
      loadData();
    } catch {
      toast.error('Failed to toggle agent');
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">Loading agent configuration...</div></div>;
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <button className="back-link" onClick={() => navigate(`/projects/${projectId}`)}>
            <HiArrowLeft /> {project?.name || 'Project'}
          </button>
          <h1><HiCog style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} />Agent Configuration</h1>
          <p className="text-muted">Customize review agent behavior for this project</p>
        </div>
      </div>

      <div className="agent-config-list">
        {agents.map((agent) => {
          const label = AGENT_LABELS[agent.agent_type] || { name: agent.agent_type, desc: '' };
          const isEditing = editing === agent.agent_type;

          return (
            <div key={agent.agent_type} className={`card agent-config-card ${!agent.is_enabled ? 'agent-disabled' : ''}`}>
              <div className="card-header">
                <div className="agent-config-title">
                  <span className={`agent-status-dot ${agent.is_enabled ? 'active' : 'inactive'}`} />
                  <div>
                    <div className="card-title">{label.name}</div>
                    <div className="text-muted" style={{ fontSize: '0.8rem' }}>{label.desc}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {agent.provider && (
                    <span className="tag" style={{ fontSize: '0.7rem' }}>
                      {agent.provider}{agent.model_name ? ` / ${agent.model_name}` : ''}
                    </span>
                  )}
                  {agent.is_customized && (
                    <span className="tag tag-accent" style={{ fontSize: '0.7rem' }}>Customized</span>
                  )}
                  <button
                    className={`btn btn-sm ${agent.is_enabled ? 'btn-secondary' : 'btn-primary'}`}
                    onClick={() => toggleAgent(agent.agent_type, agent.is_enabled)}
                  >
                    {agent.is_enabled ? 'Disable' : 'Enable'}
                  </button>
                  {!isEditing && (
                    <button className="btn btn-sm btn-secondary" onClick={() => startEdit(agent)}>
                      <HiCog /> Configure
                    </button>
                  )}
                </div>
              </div>

              {isEditing && (
                <div className="agent-config-editor">
                  <div className="agent-config-row">
                    <div className="agent-config-field" style={{ flex: 1 }}>
                      <label>Provider</label>
                      <select
                        value={editProvider}
                        onChange={(e) => { setEditProvider(e.target.value); setEditModel(''); }}
                      >
                        <option value="">Default (Gemini)</option>
                        {providers && Object.keys(providers).map((p) => (
                          <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                        ))}
                      </select>
                    </div>
                    <div className="agent-config-field" style={{ flex: 1 }}>
                      <label>Model</label>
                      <select
                        value={editModel}
                        onChange={(e) => setEditModel(e.target.value)}
                      >
                        <option value="">Default</option>
                        {providers && providers[editProvider || 'gemini']?.models?.map((m) => (
                          <option key={m} value={m}>{m}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="agent-config-field">
                    <label>System Prompt</label>
                    <textarea
                      value={editPrompt}
                      onChange={(e) => setEditPrompt(e.target.value)}
                      rows={12}
                      className="agent-prompt-textarea"
                    />
                  </div>
                  <div className="agent-config-field">
                    <label>Temperature: {editTemp}</label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={editTemp}
                      onChange={(e) => setEditTemp(parseFloat(e.target.value))}
                      className="agent-temp-slider"
                    />
                    <div className="agent-temp-labels">
                      <span>Precise (0)</span>
                      <span>Creative (1)</span>
                    </div>
                  </div>
                  <div className="agent-config-actions">
                    <button className="btn btn-primary" onClick={() => saveConfig(agent.agent_type)} disabled={saving}>
                      <HiCheck /> {saving ? 'Saving...' : 'Save'}
                    </button>
                    {agent.is_customized && (
                      <button className="btn btn-secondary" onClick={() => resetConfig(agent.agent_type)}>
                        <HiRefresh /> Reset to Default
                      </button>
                    )}
                    <button className="btn btn-secondary" onClick={cancelEdit}>
                      <HiX /> Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
