import { HiChip, HiLightningBolt, HiCheck, HiClock } from 'react-icons/hi';

function AgentCard({ agent }) {
  const completionRate = agent.total_runs > 0
    ? Math.round((agent.completed_runs / agent.total_runs) * 100)
    : 0;

  return (
    <div className="agent-perf-card">
      <div className="agent-perf-header">
        <HiChip className="agent-perf-icon" />
        <span className="agent-perf-name">{agent.agent}</span>
      </div>
      <div className="agent-perf-stats">
        <div className="agent-perf-stat">
          <HiLightningBolt />
          <span className="agent-perf-value">{agent.total_findings}</span>
          <span className="agent-perf-label">findings</span>
        </div>
        <div className="agent-perf-stat">
          <HiCheck />
          <span className="agent-perf-value">{completionRate}%</span>
          <span className="agent-perf-label">success</span>
        </div>
        <div className="agent-perf-stat">
          <HiClock />
          <span className="agent-perf-value">{agent.avg_duration_seconds ? `${agent.avg_duration_seconds}s` : '--'}</span>
          <span className="agent-perf-label">avg time</span>
        </div>
      </div>
      {agent.avg_score != null && (
        <div className="agent-perf-score">
          <div className="agent-perf-score-bar">
            <div
              className="agent-perf-score-fill"
              style={{ width: `${(agent.avg_score / 10) * 100}%` }}
            />
          </div>
          <span className="agent-perf-score-val">{agent.avg_score}/10</span>
        </div>
      )}
      <div className="agent-perf-footer">
        {agent.total_runs} runs, {agent.completed_runs} completed
      </div>
    </div>
  );
}

export default function AgentPerformance({ data }) {
  if (!data || data.length === 0) {
    return <div className="chart-empty">No agent data available yet</div>;
  }

  return (
    <div className="agent-perf-grid">
      {data.map((a) => <AgentCard key={a.agent} agent={a} />)}
    </div>
  );
}
