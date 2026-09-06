import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { reviews, feedback as feedbackApi } from '../api/client';
import client from '../api/client';
import useReviewSocket from '../hooks/useReviewSocket';
import {
  HiShieldCheck, HiLightningBolt, HiCode, HiBeaker,
  HiChevronDown, HiChevronRight, HiArrowLeft, HiFilter,
  HiTerminal, HiDocumentText, HiDownload, HiSparkles,
} from 'react-icons/hi';
import toast from 'react-hot-toast';

const SEVERITY_COLORS = {
  critical: { bg: 'var(--sev-critical-bg)', border: 'var(--sev-critical)', text: '#fca5a5', label: 'Critical' },
  warning: { bg: 'var(--sev-warning-bg)', border: 'var(--sev-warning)', text: '#fcd34d', label: 'Warning' },
  info: { bg: 'var(--sev-info-bg)', border: 'var(--sev-info)', text: '#93c5fd', label: 'Info' },
};

const AGENT_META = {
  logic: { icon: HiCode, label: 'Logic', color: '#8b5cf6' },
  security: { icon: HiShieldCheck, label: 'Security', color: '#ef4444' },
  performance: { icon: HiLightningBolt, label: 'Performance', color: '#f59e0b' },
  quality: { icon: HiBeaker, label: 'Quality', color: '#3b82f6' },
  synthesis: { icon: HiFilter, label: 'Synthesis', color: '#2c8c7c' },
  baseline: { icon: HiCode, label: 'Baseline', color: '#6b7280' },
};

function ScoreGauge({ score }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 80 ? '#22c55e' : score >= 60 ? '#f59e0b' : '#ef4444';

  return (
    <div className="review-score-gauge">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="var(--border)" strokeWidth="8" />
        <circle
          cx="70" cy="70" r={radius} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round" transform="rotate(-90 70 70)"
          style={{ transition: 'stroke-dashoffset 1s ease' }}
        />
      </svg>
      <div className="review-score-value" style={{ color }}>{Math.round(score)}</div>
      <div className="review-score-label">Quality Score</div>
    </div>
  );
}

function AgentCard({ agentType, run }) {
  const meta = AGENT_META[agentType] || AGENT_META.logic;
  const Icon = meta.icon;
  const isCompleted = run?.status === 'completed';
  const isRunning = run?.status === 'running';
  const isFailed = run?.status === 'failed';

  return (
    <div className={`review-agent-card ${isCompleted ? 'agent-done' : ''} ${isRunning ? 'agent-running' : ''} ${isFailed ? 'agent-failed' : ''}`}>
      <div className="agent-card-icon" style={{ color: meta.color }}>
        <Icon />
      </div>
      <div className="agent-card-label">{meta.label}</div>
      <div className="agent-card-status">
        {isRunning && <span className="spinner-sm" />}
        {isCompleted && <span className="agent-check">&#10003;</span>}
        {isFailed && <span className="agent-fail">&#10007;</span>}
        {!isRunning && !isCompleted && !isFailed && <span className="agent-pending">&#8230;</span>}
      </div>
      {run?.findings_count !== undefined && run.findings_count > 0 && (
        <div className="agent-card-findings">{run.findings_count} findings</div>
      )}
      {run?.findingsCount !== undefined && run.findingsCount > 0 && (
        <div className="agent-card-findings">{run.findingsCount} findings</div>
      )}
    </div>
  );
}

function AgentLogs({ logs }) {
  if (!logs || logs.length === 0) return null;

  return (
    <div className="review-section">
      <h2><HiTerminal style={{ verticalAlign: 'middle', marginRight: '0.4rem' }} />Agent Activity</h2>
      <div className="agent-logs">
        {logs.map((log, i) => (
          <div key={i} className="agent-log-entry">
            <span className="log-agent" style={{ color: AGENT_META[log.agent]?.color || '#888' }}>
              {AGENT_META[log.agent]?.label || log.agent}
            </span>
            <span className="log-action">{log.action}</span>
            {log.output && <span className="log-output">{log.output}</span>}
            {log.duration_ms > 0 && <span className="log-duration">{(log.duration_ms / 1000).toFixed(1)}s</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

function DiffViewer({ diffContent, findings }) {
  const [expanded, setExpanded] = useState(false);
  if (!diffContent) return null;

  const lines = diffContent.split('\n');
  const displayLines = expanded ? lines : lines.slice(0, 80);
  const findingsByLine = {};
  (findings || []).forEach((f) => {
    if (f.line) {
      if (!findingsByLine[f.line]) findingsByLine[f.line] = [];
      findingsByLine[f.line].push(f);
    }
  });

  return (
    <div className="review-section">
      <h2><HiDocumentText style={{ verticalAlign: 'middle', marginRight: '0.4rem' }} />Diff</h2>
      <div className="diff-viewer">
        {displayLines.map((line, i) => {
          let cls = 'diff-line';
          if (line.startsWith('+') && !line.startsWith('+++')) cls += ' diff-add';
          else if (line.startsWith('-') && !line.startsWith('---')) cls += ' diff-del';
          else if (line.startsWith('@@')) cls += ' diff-hunk';
          else if (line.startsWith('diff ')) cls += ' diff-header';

          const lineFindings = findingsByLine[i + 1] || [];

          return (
            <div key={i}>
              <div className={cls}>
                <span className="diff-line-num">{i + 1}</span>
                <span className="diff-line-content">{line || ' '}</span>
              </div>
              {lineFindings.map((f, fi) => (
                <div key={fi} className="diff-annotation" style={{ borderLeftColor: SEVERITY_COLORS[f.severity]?.border || '#666' }}>
                  <span className="diff-annotation-sev">{f.severity}</span>
                  <span>{f.message}</span>
                </div>
              ))}
            </div>
          );
        })}
        {!expanded && lines.length > 80 && (
          <button className="btn btn-sm btn-secondary" style={{ margin: '0.5rem' }} onClick={() => setExpanded(true)}>
            Show all {lines.length} lines
          </button>
        )}
      </div>
    </div>
  );
}

function FindingCard({ finding, feedbackStatus, onFeedback }) {
  const sev = SEVERITY_COLORS[finding.severity] || SEVERITY_COLORS.info;

  return (
    <div className="review-finding" style={{
      borderLeftColor: sev.border, background: sev.bg,
      opacity: feedbackStatus === 'dismiss' || feedbackStatus === 'false_positive' ? 0.5 : 1,
    }}>
      <div className="finding-header">
        <span className="finding-severity" style={{ background: sev.border, color: '#fff' }}>
          {sev.label}
        </span>
        <span className="finding-category">{finding.category}</span>
        {finding.agent && (
          <span className="finding-agent" style={{ color: AGENT_META[finding.agent]?.color || '#888' }}>
            {AGENT_META[finding.agent]?.label || finding.agent}
          </span>
        )}
        {feedbackStatus && (
          <span className={`feedback-badge feedback-${feedbackStatus}`}>
            {feedbackStatus === 'accept' ? '✓ Accepted' : feedbackStatus === 'dismiss' ? '✗ Dismissed' : '⚠ False Positive'}
          </span>
        )}
      </div>
      <div className="finding-location">
        {finding.file}{finding.line ? `:${finding.line}` : ''}
      </div>
      <div className="finding-message">{finding.message}</div>
      {finding.suggestion && (
        <div className="finding-suggestion">
          <strong>Fix:</strong> {finding.suggestion}
        </div>
      )}
      {onFeedback && !feedbackStatus && (
        <div className="finding-feedback-actions">
          <button className="btn btn-sm btn-feedback-accept" onClick={() => onFeedback(finding, 'accept')}>✓ Accept</button>
          <button className="btn btn-sm btn-feedback-dismiss" onClick={() => onFeedback(finding, 'dismiss')}>✗ Dismiss</button>
          <button className="btn btn-sm btn-feedback-fp" onClick={() => onFeedback(finding, 'false_positive')}>False Positive</button>
        </div>
      )}
    </div>
  );
}

export default function ReviewDetail() {
  const { reviewId } = useParams();
  const [review, setReview] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [expandedFiles, setExpandedFiles] = useState({});
  const [activeTab, setActiveTab] = useState('findings');
  const [fixes, setFixes] = useState(null);
  const [fixLoading, setFixLoading] = useState(false);
  const [feedbackMap, setFeedbackMap] = useState({});

  const { state: wsState, connected: wsConnected } = useReviewSocket(reviewId);

  const fetchData = useCallback(async () => {
    try {
      const [reviewRes, reportRes] = await Promise.all([
        reviews.get(reviewId),
        reviews.report(reviewId).catch(() => null),
      ]);
      setReview(reviewRes.data);
      if (reportRes?.data) setReport(reportRes.data);

      feedbackApi.getForReview(reviewId).then((res) => {
        const map = {};
        (res.data || []).forEach((fb) => { map[fb.finding_hash] = fb.action; });
        setFeedbackMap(map);
      }).catch(() => {});
    } catch {
      toast.error('Failed to load review');
    } finally {
      setLoading(false);
    }
  }, [reviewId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (wsState?.status === 'completed' && (!review || review.status !== 'completed')) {
      fetchData();
    }
  }, [wsState?.status]);

  useEffect(() => {
    if (!review || review.status === 'completed' || review.status === 'failed') return;
    if (wsConnected) return;
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [review?.status, wsConnected, fetchData]);

  if (loading) return <div className="page"><div className="loading">Loading review...</div></div>;
  if (!review) return <div className="page"><div className="empty-state">Review not found</div></div>;

  const liveStatus = wsState?.status || review.status;
  const liveScore = wsState?.overall_score ?? review.overall_score;
  const liveSummary = wsState?.summary || review.summary;
  const liveFindingsCount = wsState?.findings_count ?? review.findings_count;

  const agentRuns = {};
  if (wsState?.agent_runs) {
    Object.entries(wsState.agent_runs).forEach(([type, data]) => {
      agentRuns[type] = data;
    });
  } else if (report?.agent_results) {
    report.agent_results.forEach((ar) => {
      agentRuns[ar.agent_type] = {
        status: ar.status,
        findingsCount: ar.findings_count,
        score: ar.score,
        summary: ar.summary,
      };
    });
  }

  const findings = report?.findings || [];
  const filtered = filter === 'all' ? findings : findings.filter((f) => f.severity === filter);

  const fileGroups = {};
  filtered.forEach((f) => {
    const file = f.file || 'unknown';
    if (!fileGroups[file]) fileGroups[file] = [];
    fileGroups[file].push(f);
  });

  const toggleFile = (file) => {
    setExpandedFiles((prev) => ({ ...prev, [file]: !prev[file] }));
  };

  const comparison = report?.baseline_comparison;

  const handleFeedback = async (finding, action) => {
    try {
      await feedbackApi.submit(reviewId, { finding, action });
      const key = `${finding.file}:${finding.line}:${finding.category}:${finding.message}`;
      setFeedbackMap((prev) => ({ ...prev, [key]: action }));
      toast.success(action === 'accept' ? 'Finding accepted' : 'Finding dismissed');
    } catch {
      toast.error('Failed to save feedback');
    }
  };

  const getFeedbackKey = (f) => `${f.file}:${f.line}:${f.category}:${f.message}`;

  const handleAutoFix = async () => {
    setFixLoading(true);
    try {
      const res = await reviews.autoFix(reviewId);
      setFixes(res.data.fixes || []);
      if (res.data.fixes?.length === 0) {
        toast.error('No auto-fixes could be generated');
      } else {
        toast.success(`Generated ${res.data.fixes.length} fix suggestions`);
      }
    } catch {
      toast.error('Failed to generate auto-fixes');
    } finally {
      setFixLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const res = await client.get(`/exports/reviews/${reviewId}`, { responseType: 'blob' });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `review-${reviewId}.md`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Report downloaded');
    } catch {
      toast.error('Failed to export report');
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/dashboard" className="back-link"><HiArrowLeft /> Dashboard</Link>
          <h1>{review.pr_title || 'Code Review'}</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.3rem' }}>
            <span className={`status-badge status-${liveStatus}`}>{liveStatus}</span>
            {wsConnected && <span className="ws-indicator" title="Live updates active" />}
          </div>
        </div>
        <div className="header-actions">
          {liveStatus === 'completed' && (
            <>
              <button className="btn btn-accent" onClick={handleAutoFix} disabled={fixLoading}>
                <HiSparkles /> {fixLoading ? 'Generating...' : 'Auto-Fix'}
              </button>
              <button className="btn btn-secondary" onClick={handleExport}>
                <HiDownload /> Export Report
              </button>
            </>
          )}
        </div>
      </div>

      {/* Score + Summary */}
      <div className="review-summary-row">
        {liveScore !== null && liveScore !== undefined && (
          <ScoreGauge score={liveScore} />
        )}
        <div className="review-summary-text">
          {liveSummary && <p>{liveSummary}</p>}
          <div className="review-meta-chips">
            <span className="meta-chip">{liveFindingsCount} findings</span>
            {findings.filter((f) => f.severity === 'critical').length > 0 && (
              <span className="meta-chip meta-chip-critical">
                {findings.filter((f) => f.severity === 'critical').length} critical
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Agent Pipeline */}
      <div className="review-section">
        <h2>Agent Pipeline</h2>
        <div className="review-pipeline">
          <div className="pipeline-agents">
            {['logic', 'security', 'performance', 'quality'].map((a) => (
              <AgentCard key={a} agentType={a} run={agentRuns[a]} />
            ))}
          </div>
          <div className="pipeline-synthesis-arrow">
            <div className="pipeline-arrow-down" />
          </div>
          <div className="pipeline-synthesis">
            <AgentCard agentType="synthesis" run={agentRuns.synthesis} />
          </div>
        </div>
      </div>

      {/* Agent Logs (live from WebSocket) */}
      <AgentLogs logs={wsState?.recent_logs} />

      {/* Tabs: Findings | Diff | Baseline */}
      <div className="review-tabs">
        <button className={`review-tab ${activeTab === 'findings' ? 'active' : ''}`} onClick={() => setActiveTab('findings')}>
          Findings {findings.length > 0 && `(${findings.length})`}
        </button>
        <button className={`review-tab ${activeTab === 'diff' ? 'active' : ''}`} onClick={() => setActiveTab('diff')}>
          Diff
        </button>
        {fixes && fixes.length > 0 && (
          <button className={`review-tab ${activeTab === 'fixes' ? 'active' : ''}`} onClick={() => setActiveTab('fixes')}>
            Auto-Fixes ({fixes.length})
          </button>
        )}
        {comparison && (
          <button className={`review-tab ${activeTab === 'baseline' ? 'active' : ''}`} onClick={() => setActiveTab('baseline')}>
            Baseline Comparison
          </button>
        )}
      </div>

      {/* Findings tab */}
      {activeTab === 'findings' && findings.length > 0 && (
        <div className="review-section">
          <div className="findings-header">
            <div className="filter-buttons">
              {['all', 'critical', 'warning', 'info'].map((f) => (
                <button
                  key={f}
                  className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setFilter(f)}
                >
                  {f === 'all' ? `All (${findings.length})` : `${f} (${findings.filter((x) => x.severity === f).length})`}
                </button>
              ))}
            </div>
          </div>

          {Object.entries(fileGroups).map(([file, fileFindings]) => (
            <div key={file} className="finding-file-group">
              <button className="finding-file-header" onClick={() => toggleFile(file)}>
                {expandedFiles[file] !== false ? <HiChevronDown /> : <HiChevronRight />}
                <span className="finding-filename">{file}</span>
                <span className="finding-file-count">{fileFindings.length}</span>
              </button>
              {expandedFiles[file] !== false && (
                <div className="finding-file-list">
                  {fileFindings.map((f, i) => (
                    <FindingCard
                      key={i}
                      finding={f}
                      feedbackStatus={feedbackMap[getFeedbackKey(f)]}
                      onFeedback={liveStatus === 'completed' ? handleFeedback : null}
                    />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {activeTab === 'findings' && findings.length === 0 && liveStatus === 'completed' && (
        <div className="review-section">
          <div className="empty-state" style={{ padding: '2rem' }}>No findings detected.</div>
        </div>
      )}

      {/* Diff tab */}
      {activeTab === 'diff' && (
        <DiffViewer diffContent={review.diff_content} findings={findings} />
      )}

      {/* Auto-Fixes tab */}
      {activeTab === 'fixes' && fixes && fixes.length > 0 && (
        <div className="review-section">
          <h2><HiSparkles style={{ verticalAlign: 'middle', marginRight: '0.4rem' }} />Suggested Fixes</h2>
          {fixes.map((fix, i) => (
            <div key={i} className="auto-fix-card">
              <div className="fix-header">
                <span className="finding-severity" style={{
                  background: SEVERITY_COLORS[fix.severity]?.border || '#666',
                  color: '#fff',
                }}>{fix.severity}</span>
                <span className="finding-category">{fix.category}</span>
                <span className="finding-location">{fix.file}{fix.line ? `:${fix.line}` : ''}</span>
              </div>
              <p className="fix-explanation">{fix.explanation}</p>
              <div className="fix-diff">
                <div className="fix-code-block fix-original">
                  <div className="fix-code-label">Before</div>
                  <pre>{fix.original_code}</pre>
                </div>
                <div className="fix-code-block fix-corrected">
                  <div className="fix-code-label">After</div>
                  <pre>{fix.fixed_code}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Baseline tab */}
      {activeTab === 'baseline' && comparison && (
        <div className="review-section">
          <h2>Multi-Agent vs Single-Prompt Baseline</h2>
          <div className="comparison-grid">
            <div className="comparison-card comparison-agent">
              <h3>Multi-Agent Pipeline</h3>
              <div className="comparison-stat">{comparison.agent_findings_count} findings</div>
              <div className="comparison-stat">Score: {comparison.agent_score?.toFixed(0) ?? '--'}</div>
              <div className="comparison-stat">{comparison.categories_covered_agents?.length || 0} categories</div>
              <div className="comparison-unique">+{comparison.unique_to_agents} unique findings</div>
            </div>
            <div className="comparison-vs">VS</div>
            <div className="comparison-card comparison-baseline">
              <h3>Single Prompt</h3>
              <div className="comparison-stat">{comparison.baseline_findings_count} findings</div>
              <div className="comparison-stat">Score: {comparison.baseline_score?.toFixed(0) ?? '--'}</div>
              <div className="comparison-stat">{comparison.categories_covered_baseline?.length || 0} categories</div>
              <div className="comparison-unique">+{comparison.unique_to_baseline} unique findings</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
