import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { reviews } from '../api/client';
import {
  HiShieldCheck, HiLightningBolt, HiCode, HiBeaker,
  HiChevronDown, HiChevronRight, HiArrowLeft, HiFilter,
} from 'react-icons/hi';
import toast from 'react-hot-toast';

const SEVERITY_COLORS = {
  critical: { bg: '#2d1215', border: '#dc2626', text: '#fca5a5', label: 'Critical' },
  warning: { bg: '#2d2305', border: '#d97706', text: '#fcd34d', label: 'Warning' },
  info: { bg: '#0c1929', border: '#2563eb', text: '#93c5fd', label: 'Info' },
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
      {run?.findingsCount !== undefined && (
        <div className="agent-card-findings">{run.findingsCount} findings</div>
      )}
    </div>
  );
}

function FindingCard({ finding }) {
  const sev = SEVERITY_COLORS[finding.severity] || SEVERITY_COLORS.info;

  return (
    <div className="review-finding" style={{ borderLeftColor: sev.border, background: sev.bg }}>
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

  const fetchData = useCallback(async () => {
    try {
      const [reviewRes, reportRes] = await Promise.all([
        reviews.get(reviewId),
        reviews.report(reviewId).catch(() => null),
      ]);
      setReview(reviewRes.data);
      if (reportRes?.data) setReport(reportRes.data);
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
    if (!review || review.status === 'completed' || review.status === 'failed') return;
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [review?.status, fetchData]);

  if (loading) return <div className="page"><div className="loading">Loading review...</div></div>;
  if (!review) return <div className="page"><div className="empty-state">Review not found</div></div>;

  const agentRuns = {};
  if (report?.agent_results) {
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

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/dashboard" className="back-link"><HiArrowLeft /> Dashboard</Link>
          <h1>{review.pr_title || 'Code Review'}</h1>
          <span className={`status-badge status-${review.status}`}>{review.status}</span>
        </div>
      </div>

      {/* Score + Summary */}
      <div className="review-summary-row">
        {review.overall_score !== null && review.overall_score !== undefined && (
          <ScoreGauge score={review.overall_score} />
        )}
        <div className="review-summary-text">
          {review.summary && <p>{review.summary}</p>}
          <div className="review-meta-chips">
            <span className="meta-chip">{review.findings_count} findings</span>
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

      {/* Baseline Comparison */}
      {comparison && (
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

      {/* Findings */}
      {findings.length > 0 && (
        <div className="review-section">
          <div className="findings-header">
            <h2>Findings</h2>
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

          {Object.entries(fileGroups).map(([file, fileFindigs]) => (
            <div key={file} className="finding-file-group">
              <button className="finding-file-header" onClick={() => toggleFile(file)}>
                {expandedFiles[file] !== false ? <HiChevronDown /> : <HiChevronRight />}
                <span className="finding-filename">{file}</span>
                <span className="finding-file-count">{fileFindigs.length}</span>
              </button>
              {expandedFiles[file] !== false && (
                <div className="finding-file-list">
                  {fileFindigs.map((f, i) => <FindingCard key={i} finding={f} />)}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
