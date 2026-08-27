import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { tasks as tasksApi, runs as runsApi, evaluations as evalsApi, trajectories as trajApi } from '../api/client';
import {
  HiArrowLeft, HiPlay, HiPlus, HiClipboardCheck, HiChevronDown, HiChevronRight,
  HiClock, HiCheckCircle, HiXCircle, HiExclamation, HiRefresh, HiChip,
  HiLightningBolt, HiDocumentReport, HiCog,
} from 'react-icons/hi';
import toast from 'react-hot-toast';

const statusIcon = {
  pending: <HiClock className="status-icon icon-pending" />,
  running: <HiRefresh className="status-icon icon-running" />,
  completed: <HiCheckCircle className="status-icon icon-completed" />,
  evaluated: <HiCheckCircle className="status-icon icon-evaluated" />,
  failed: <HiXCircle className="status-icon icon-failed" />,
  timeout: <HiExclamation className="status-icon icon-timeout" />,
};

const statusBadge = {
  pending: 'badge-gray',
  running: 'badge-blue',
  completed: 'badge-green',
  evaluated: 'badge-green',
  failed: 'badge-red',
  timeout: 'badge-yellow',
};

function CreateRunModal({ taskId, onClose, onCreated }) {
  const [agentName, setAgentName] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await runsApi.create({ task_id: taskId, agent_name: agentName });
      toast.success('Run created');
      onCreated();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create run');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>New Run</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Agent Name</label>
            <input
              value={agentName}
              onChange={(e) => setAgentName(e.target.value)}
              placeholder="e.g. gpt-4, claude-sonnet, codex"
              required
              autoFocus
            />
            <div className="form-hint">The AI agent that will attempt to solve this task</div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary"><HiChip /> Create Run</button>
          </div>
        </form>
      </div>
    </div>
  );
}

function TrajectoryViewer({ runId }) {
  const [steps, setSteps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    trajApi.getByRun(runId)
      .then((res) => setSteps(res.data))
      .catch(() => toast.error('Failed to load trajectory'))
      .finally(() => setLoading(false));
  }, [runId]);

  if (loading) return <div className="text-muted text-sm">Loading trajectory...</div>;
  if (steps.length === 0) return <div className="text-muted text-sm">No trajectory steps recorded.</div>;

  return (
    <div className="trajectory-timeline">
      {steps.map((step, i) => (
        <div key={step.id} className="trajectory-step">
          <div className="step-marker">
            <div className="step-number">{step.sequence_number}</div>
            {i < steps.length - 1 && <div className="step-line" />}
          </div>
          <div className="step-content">
            <div className="step-header">
              <span className="badge badge-blue">{step.action_type}</span>
              {step.duration_ms && <span className="text-muted text-sm">{step.duration_ms}ms</span>}
            </div>
            {step.action_input && (
              <div className="step-block">
                <div className="step-block-label">Input</div>
                <pre className="step-code">{step.action_input}</pre>
              </div>
            )}
            {step.action_output && (
              <div className="step-block">
                <div className="step-block-label">Output</div>
                <pre className="step-code">{step.action_output}</pre>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function EvaluationCard({ runId }) {
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    evalsApi.getByRun(runId)
      .then((res) => setEvaluation(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [runId]);

  if (loading) return <div className="text-muted text-sm">Loading evaluation...</div>;
  if (!evaluation) return <div className="text-muted text-sm">Not evaluated yet.</div>;

  return (
    <div className="eval-card">
      <div className="eval-grid">
        <div className="eval-stat">
          <div className="eval-stat-value">{evaluation.score != null ? `${Math.round(evaluation.score * 100)}%` : '—'}</div>
          <div className="eval-stat-label">Score</div>
        </div>
        <div className="eval-stat">
          <div className="eval-stat-value">{evaluation.tests_passed}/{evaluation.tests_total}</div>
          <div className="eval-stat-label">Tests Passed</div>
        </div>
        <div className="eval-stat">
          <div className={`eval-stat-value ${evaluation.is_correct ? 'text-pass' : 'text-fail'}`}>
            {evaluation.is_correct ? 'PASS' : 'FAIL'}
          </div>
          <div className="eval-stat-label">Result</div>
        </div>
        <div className="eval-stat">
          <div className="eval-stat-value">{evaluation.evaluation_method}</div>
          <div className="eval-stat-label">Method</div>
        </div>
      </div>
      {evaluation.feedback && (
        <div className="eval-feedback">
          <div className="step-block-label">Feedback</div>
          <pre className="step-code">{evaluation.feedback}</pre>
        </div>
      )}
    </div>
  );
}

function RunRow({ run, onRefresh }) {
  const [expanded, setExpanded] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [evaluating, setEvaluating] = useState(false);

  const handleExecute = async (e) => {
    e.stopPropagation();
    setExecuting(true);
    try {
      await runsApi.execute(run.id);
      toast.success('Job queued — worker will pick it up');
      onRefresh();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to execute');
    } finally {
      setExecuting(false);
    }
  };

  const handleEvaluate = async (e) => {
    e.stopPropagation();
    setEvaluating(true);
    try {
      await runsApi.evaluate(run.id);
      toast.success('Evaluation job queued');
      onRefresh();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to evaluate');
    } finally {
      setEvaluating(false);
    }
  };

  const pipelineStage = run.status === 'evaluated' ? 3
    : run.status === 'completed' ? 2
    : run.status === 'running' ? 1
    : run.status === 'failed' || run.status === 'timeout' ? -1
    : 0;

  return (
    <div className="run-card">
      <div className="run-header" onClick={() => setExpanded(!expanded)}>
        <div className="run-header-left">
          {expanded ? <HiChevronDown /> : <HiChevronRight />}
          {statusIcon[run.status] || statusIcon.pending}
          <div className="run-agent-info">
            <span className="font-medium">{run.agent_name}</span>
            <span className="run-agent-sub">Agent</span>
          </div>
          <span className={`badge ${statusBadge[run.status] || 'badge-gray'}`}>{run.status}</span>
        </div>
        <div className="run-header-right">
          {run.duration_seconds && (
            <span className="run-duration"><HiClock /> {run.duration_seconds.toFixed(1)}s</span>
          )}
          <span className="text-muted text-sm">
            {new Date(run.created_at).toLocaleString()}
          </span>
          {run.status === 'pending' && (
            <button className="btn btn-sm btn-primary" onClick={handleExecute} disabled={executing}>
              <HiPlay /> {executing ? 'Queuing...' : 'Execute'}
            </button>
          )}
          {run.status === 'completed' && (
            <button className="btn btn-sm btn-secondary" onClick={handleEvaluate} disabled={evaluating}>
              <HiClipboardCheck /> {evaluating ? 'Queuing...' : 'Evaluate'}
            </button>
          )}
        </div>
      </div>

      <div className="run-pipeline-bar">
        <div className={`run-pipeline-step ${pipelineStage >= 0 ? 'rps-active' : ''} ${pipelineStage === -1 ? 'rps-error' : ''}`}>
          <HiCog className="rps-icon" /> Queued
        </div>
        <div className={`run-pipeline-step ${pipelineStage >= 1 ? 'rps-active' : ''}`}>
          <HiLightningBolt className="rps-icon" /> Executing
        </div>
        <div className={`run-pipeline-step ${pipelineStage >= 2 ? 'rps-active' : ''}`}>
          <HiClipboardCheck className="rps-icon" /> Completed
        </div>
        <div className={`run-pipeline-step ${pipelineStage >= 3 ? 'rps-active' : ''}`}>
          <HiDocumentReport className="rps-icon" /> Evaluated
        </div>
      </div>

      {expanded && (
        <div className="run-detail">
          <div className="run-detail-meta">
            <div className="run-meta-item">
              <span className="run-meta-label">Agent</span>
              <span className="run-meta-value"><HiChip /> {run.agent_name}</span>
            </div>
            <div className="run-meta-item">
              <span className="run-meta-label">Exit Code</span>
              <span className="run-meta-value">{run.exit_code != null ? run.exit_code : '—'}</span>
            </div>
            <div className="run-meta-item">
              <span className="run-meta-label">Started</span>
              <span className="run-meta-value">{run.started_at ? new Date(run.started_at).toLocaleString() : '—'}</span>
            </div>
            <div className="run-meta-item">
              <span className="run-meta-label">Completed</span>
              <span className="run-meta-value">{run.completed_at ? new Date(run.completed_at).toLocaleString() : '—'}</span>
            </div>
          </div>

          {run.error_message && (
            <div className="run-error">
              <strong>Error:</strong> {run.error_message}
            </div>
          )}

          <div className="run-section">
            <h4><HiLightningBolt /> Trajectory</h4>
            <TrajectoryViewer runId={run.id} />
          </div>

          <div className="run-section">
            <h4><HiClipboardCheck /> Evaluation</h4>
            <EvaluationCard runId={run.id} />
          </div>
        </div>
      )}
    </div>
  );
}

export default function TaskDetail() {
  const { taskId } = useParams();
  const [task, setTask] = useState(null);
  const [runList, setRunList] = useState([]);
  const [showRunModal, setShowRunModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    try {
      const [t, r] = await Promise.all([
        tasksApi.get(taskId),
        runsApi.list(taskId),
      ]);
      setTask(t.data);
      setRunList(r.data);
    } catch {
      toast.error('Failed to load task');
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading) return <div className="loading">Loading...</div>;
  if (!task) return <div className="loading">Task not found</div>;

  const diffColor = { easy: 'badge-green', medium: 'badge-yellow', hard: 'badge-red' };
  const completedRuns = runList.filter((r) => r.status === 'completed' || r.status === 'evaluated').length;
  const failedRuns = runList.filter((r) => r.status === 'failed' || r.status === 'timeout').length;

  return (
    <div className="page">
      <Link to={`/projects/${task.project_id}`} className="back-link">
        <HiArrowLeft /> Back to Project
      </Link>

      <div className="page-header">
        <div>
          <h1>{task.title}</h1>
          <div className="task-meta">
            <span className={`badge ${diffColor[task.difficulty] || ''}`}>{task.difficulty}</span>
            <span className={`badge ${statusBadge[task.status] || 'badge-gray'}`}>{task.status}</span>
            <span className="text-muted text-sm"><HiClock /> {task.time_limit_seconds}s limit</span>
          </div>
        </div>
        <div className="header-actions">
          <button className="btn btn-sm btn-secondary" onClick={fetchAll}>
            <HiRefresh /> Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setShowRunModal(true)}>
            <HiPlus /> New Run
          </button>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-card stat-card-sm">
          <div className="stat-icon stat-icon-blue"><HiPlay /></div>
          <div className="stat-info">
            <div className="stat-value">{runList.length}</div>
            <div className="stat-label">Total Runs</div>
          </div>
        </div>
        <div className="stat-card stat-card-sm">
          <div className="stat-icon stat-icon-green"><HiCheckCircle /></div>
          <div className="stat-info">
            <div className="stat-value">{completedRuns}</div>
            <div className="stat-label">Passed</div>
          </div>
        </div>
        <div className="stat-card stat-card-sm">
          <div className="stat-icon stat-icon-red"><HiXCircle /></div>
          <div className="stat-info">
            <div className="stat-value">{failedRuns}</div>
            <div className="stat-label">Failed</div>
          </div>
        </div>
        <div className="stat-card stat-card-sm">
          <div className="stat-icon stat-icon-accent"><HiChip /></div>
          <div className="stat-info">
            <div className="stat-value">{new Set(runList.map((r) => r.agent_name)).size}</div>
            <div className="stat-label">Agents</div>
          </div>
        </div>
      </div>

      <div className="task-description-card">
        <h3>Description</h3>
        <p>{task.description}</p>
        <div className="task-fields-row">
          {task.test_command && (
            <div className="task-field">
              <span className="task-field-label">Test Command</span>
              <code className="task-field-code">{task.test_command}</code>
            </div>
          )}
          {task.expected_output && (
            <div className="task-field">
              <span className="task-field-label">Expected Output</span>
              <pre className="step-code">{task.expected_output}</pre>
            </div>
          )}
          {task.language && (
            <div className="task-field">
              <span className="task-field-label">Language</span>
              <span className="badge badge-blue">{task.language}</span>
            </div>
          )}
        </div>
      </div>

      <section className="section">
        <div className="section-header">
          <h2><HiPlay /> Agent Runs ({runList.length})</h2>
        </div>

        {runList.length === 0 ? (
          <div className="empty-state">
            <HiChip className="empty-icon" />
            <h3>No runs yet</h3>
            <p>Create a run to dispatch an AI agent to this task. The worker will pick it up from the queue.</p>
            <button className="btn btn-primary" onClick={() => setShowRunModal(true)}>
              <HiPlus /> Create Run
            </button>
          </div>
        ) : (
          <div className="runs-list">
            {runList.map((run) => (
              <RunRow key={run.id} run={run} onRefresh={fetchAll} />
            ))}
          </div>
        )}
      </section>

      {showRunModal && (
        <CreateRunModal
          taskId={taskId}
          onClose={() => setShowRunModal(false)}
          onCreated={fetchAll}
        />
      )}
    </div>
  );
}
