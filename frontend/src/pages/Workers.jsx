import { useState, useEffect } from 'react';
import { health } from '../api/client';
import {
  HiServer, HiRefresh, HiCheck, HiX, HiCog, HiLightningBolt, HiChip,
  HiClipboardCheck, HiDocumentReport, HiCode,
} from 'react-icons/hi';
import toast from 'react-hot-toast';

const WORKERS = [
  {
    name: 'execution_worker',
    label: 'Execution Worker',
    icon: <HiLightningBolt />,
    desc: 'Clones repos, runs agent commands, records trajectories',
    queue: 'default',
    tasks: ['execute_agent'],
  },
  {
    name: 'evaluation_worker',
    label: 'Evaluation Worker',
    icon: <HiClipboardCheck />,
    desc: 'Runs test suites, compares output, scores runs',
    queue: 'default',
    tasks: ['evaluate_run'],
  },
  {
    name: 'review_worker',
    label: 'Review Worker',
    icon: <HiCode />,
    desc: 'AI-powered code review on agent patches',
    queue: 'default',
    tasks: ['review_code'],
  },
  {
    name: 'report_worker',
    label: 'Report Worker',
    icon: <HiDocumentReport />,
    desc: 'Generates evaluation reports and summaries',
    queue: 'default',
    tasks: ['generate_report'],
  },
  {
    name: 'github_worker',
    label: 'GitHub Worker',
    icon: <HiChip />,
    desc: 'Fetches repos, syncs branches, manages webhooks',
    queue: 'default',
    tasks: ['setup_repos'],
  },
];

export default function Workers() {
  const [apiOnline, setApiOnline] = useState(null);
  const [dbOnline, setDbOnline] = useState(null);
  const [loading, setLoading] = useState(true);

  const checkHealth = async () => {
    setLoading(true);
    try {
      await health.check();
      setApiOnline(true);
    } catch {
      setApiOnline(false);
    }
    try {
      await health.db();
      setDbOnline(true);
    } catch {
      setDbOnline(false);
    }
    setLoading(false);
  };

  useEffect(() => { checkHealth(); }, []);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1><HiServer /> Workers & Services</h1>
          <p className="text-muted">Celery task workers powering the execution pipeline</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-sm btn-secondary" onClick={checkHealth} disabled={loading}>
            <HiRefresh className={loading ? 'icon-running' : ''} /> Refresh
          </button>
        </div>
      </div>

      <div className="pipeline-banner">
        <div className="pipeline-title">Execution Pipeline</div>
        <div className="pipeline-flow">
          <div className="pipeline-node pipeline-node-accent">
            <HiCog />
            <span>Task Created</span>
          </div>
          <div className="pipeline-arrow" />
          <div className="pipeline-node pipeline-node-blue">
            <HiLightningBolt />
            <span>Agent Executes</span>
          </div>
          <div className="pipeline-arrow" />
          <div className="pipeline-node pipeline-node-yellow">
            <HiClipboardCheck />
            <span>Evaluation</span>
          </div>
          <div className="pipeline-arrow" />
          <div className="pipeline-node pipeline-node-green">
            <HiDocumentReport />
            <span>Report</span>
          </div>
        </div>
      </div>

      <section className="section">
        <div className="section-header">
          <h2><HiCog /> System Health</h2>
        </div>
        <div className="health-grid">
          <div className={`health-card ${apiOnline ? 'health-ok' : 'health-err'}`}>
            <div className="health-indicator">{apiOnline ? <HiCheck /> : <HiX />}</div>
            <div>
              <div className="health-label">API Server</div>
              <div className="health-status">{loading ? 'Checking...' : apiOnline ? 'Online' : 'Offline'}</div>
            </div>
          </div>
          <div className={`health-card ${dbOnline ? 'health-ok' : 'health-err'}`}>
            <div className="health-indicator">{dbOnline ? <HiCheck /> : <HiX />}</div>
            <div>
              <div className="health-label">Database</div>
              <div className="health-status">{loading ? 'Checking...' : dbOnline ? 'Connected' : 'Disconnected'}</div>
            </div>
          </div>
          <div className="health-card health-neutral">
            <div className="health-indicator"><HiServer /></div>
            <div>
              <div className="health-label">Redis / Broker</div>
              <div className="health-status">Celery Queue</div>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <h2><HiLightningBolt /> Worker Pool</h2>
        </div>
        <div className="worker-grid">
          {WORKERS.map((w) => (
            <div key={w.name} className="worker-card">
              <div className="worker-card-header">
                <div className="worker-icon">{w.icon}</div>
                <div>
                  <div className="worker-name">{w.label}</div>
                  <span className="badge badge-blue">{w.queue}</span>
                </div>
              </div>
              <p className="worker-desc">{w.desc}</p>
              <div className="worker-tasks">
                <span className="worker-tasks-label">Registered Tasks</span>
                {w.tasks.map((t) => (
                  <code key={t} className="worker-task-name">{t}</code>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-header">
          <h2><HiChip /> Agent Types</h2>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Agent</th><th>Type</th><th>Description</th><th>Workers Used</th></tr>
            </thead>
            <tbody>
              <tr>
                <td className="font-medium">Code Agent</td>
                <td><span className="badge badge-blue">LLM</span></td>
                <td className="text-muted text-sm">Generates code patches and fixes from task descriptions</td>
                <td className="text-sm">Execution, Review</td>
              </tr>
              <tr>
                <td className="font-medium">Test Agent</td>
                <td><span className="badge badge-green">Validator</span></td>
                <td className="text-muted text-sm">Runs test suites and validates correctness</td>
                <td className="text-sm">Evaluation</td>
              </tr>
              <tr>
                <td className="font-medium">Review Agent</td>
                <td><span className="badge badge-yellow">Reviewer</span></td>
                <td className="text-muted text-sm">AI-powered code review with security and quality checks</td>
                <td className="text-sm">Review, Report</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
