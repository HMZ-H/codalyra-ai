import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analytics, projects as projectsApi } from '../api/client';
import { HiTrendingUp, HiClipboardList, HiChartBar, HiChip, HiArrowRight } from 'react-icons/hi';
import ScoreTrendChart from '../components/ScoreTrendChart';
import CategoryBreakdown from '../components/CategoryBreakdown';
import AgentPerformance from '../components/AgentPerformance';
import toast from 'react-hot-toast';

export default function AnalyticsPage() {
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [agents, setAgents] = useState([]);
  const [projectList, setProjectList] = useState([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.list().then((res) => setProjectList(res.data)).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (selectedProject) params.project_id = selectedProject;

    Promise.all([
      analytics.overview(),
      analytics.scoreTrends({ ...params, days }),
      analytics.categories(params),
      analytics.agents(params),
    ])
      .then(([ov, tr, cat, ag]) => {
        setOverview(ov.data);
        setTrends(tr.data);
        setCategories(cat.data);
        setAgents(ag.data);
      })
      .catch(() => toast.error('Failed to load analytics'))
      .finally(() => setLoading(false));
  }, [selectedProject, days]);

  if (loading) return <div className="page"><div className="loading">Loading analytics...</div></div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Analytics</h1>
          <p className="text-muted">Track review quality and agent performance</p>
        </div>
        <div className="header-actions">
          <select
            className="filter-select"
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
          >
            <option value="">All Projects</option>
            {projectList.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <Link to="/analytics/history" className="btn btn-secondary">
            <HiClipboardList /> Review History
          </Link>
        </div>
      </div>

      {overview && (
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-icon stat-icon-accent"><HiClipboardList /></div>
            <div className="stat-info">
              <div className="stat-value">{overview.total_reviews}</div>
              <div className="stat-label">Total Reviews</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon stat-icon-blue"><HiTrendingUp /></div>
            <div className="stat-info">
              <div className="stat-value">{overview.avg_score != null ? overview.avg_score.toFixed(1) : '--'}</div>
              <div className="stat-label">Avg Score</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon stat-icon-yellow"><HiChartBar /></div>
            <div className="stat-info">
              <div className="stat-value">{overview.total_findings}</div>
              <div className="stat-label">Total Findings</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon stat-icon-green"><HiChip /></div>
            <div className="stat-info">
              <div className="stat-value">{overview.reviews_last_30_days}</div>
              <div className="stat-label">Last 30 Days</div>
            </div>
          </div>
        </div>
      )}

      <div className="analytics-grid">
        <div className="analytics-panel analytics-panel-wide">
          <div className="analytics-panel-header">
            <h3><HiTrendingUp /> Quality Score Trends</h3>
            <select className="filter-select-sm" value={days} onChange={(e) => setDays(Number(e.target.value))}>
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
              <option value={180}>6 months</option>
              <option value={365}>1 year</option>
            </select>
          </div>
          <ScoreTrendChart data={trends} />
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <h3><HiChartBar /> Finding Categories</h3>
          </div>
          <CategoryBreakdown data={categories} />
        </div>

        <div className="analytics-panel analytics-panel-wide">
          <div className="analytics-panel-header">
            <h3><HiChip /> Agent Performance</h3>
          </div>
          <AgentPerformance data={agents} />
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Link to="/analytics/history" className="btn btn-primary">
          <HiArrowRight /> View Full Review History
        </Link>
      </div>
    </div>
  );
}
