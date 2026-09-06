import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { analytics, projects as projectsApi } from '../api/client';
import { HiSearch, HiFilter, HiChevronLeft, HiChevronRight, HiArrowLeft } from 'react-icons/hi';
import toast from 'react-hot-toast';

const STATUS_OPTIONS = ['all', 'pending', 'processing', 'completed', 'failed'];

function ScoreBadge({ score }) {
  if (score == null) return <span className="badge badge-gray">--</span>;
  const cls = score >= 7 ? 'badge-green' : score >= 4 ? 'badge-yellow' : 'badge-red';
  return <span className={`badge ${cls}`}>{score.toFixed(1)}</span>;
}

function StatusBadge({ status }) {
  const cls = {
    completed: 'badge-green',
    processing: 'badge-blue',
    pending: 'badge-gray',
    failed: 'badge-red',
  }[status] || 'badge-gray';
  return <span className={`badge ${cls}`}>{status}</span>;
}

export default function ReviewHistory() {
  const [data, setData] = useState({ reviews: [], total: 0, page: 1, per_page: 20, total_pages: 1 });
  const [projectList, setProjectList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    project_id: '',
    status: 'all',
    min_score: '',
    max_score: '',
    search: '',
    page: 1,
  });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    projectsApi.list().then((res) => setProjectList(res.data)).catch(() => {});
  }, []);

  const fetchReviews = useCallback(async () => {
    setLoading(true);
    try {
      const params = { page: filters.page, per_page: 20 };
      if (filters.project_id) params.project_id = filters.project_id;
      if (filters.status !== 'all') params.status = filters.status;
      if (filters.min_score) params.min_score = parseFloat(filters.min_score);
      if (filters.max_score) params.max_score = parseFloat(filters.max_score);
      if (filters.search.trim()) params.search = filters.search.trim();
      const res = await analytics.reviews(params);
      setData(res.data);
    } catch {
      toast.error('Failed to load review history');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { fetchReviews(); }, [fetchReviews]);

  const updateFilter = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }));
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/analytics" className="back-link"><HiArrowLeft /> Analytics</Link>
          <h1>Review History</h1>
          <p className="text-muted">{data.total} total reviews</p>
        </div>
      </div>

      <div className="history-toolbar">
        <div className="search-box">
          <HiSearch className="search-icon" />
          <input
            type="text"
            placeholder="Search by PR title..."
            value={filters.search}
            onChange={(e) => updateFilter('search', e.target.value)}
          />
        </div>
        <button className={`btn btn-secondary ${showFilters ? 'active' : ''}`} onClick={() => setShowFilters(!showFilters)}>
          <HiFilter /> Filters
        </button>
      </div>

      {showFilters && (
        <div className="filter-panel">
          <div className="filter-group">
            <label>Project</label>
            <select value={filters.project_id} onChange={(e) => updateFilter('project_id', e.target.value)}>
              <option value="">All Projects</option>
              {projectList.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Status</label>
            <select value={filters.status} onChange={(e) => updateFilter('status', e.target.value)}>
              {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s === 'all' ? 'All' : s}</option>)}
            </select>
          </div>
          <div className="filter-group">
            <label>Min Score</label>
            <input type="number" min="0" max="10" step="0.1" value={filters.min_score} onChange={(e) => updateFilter('min_score', e.target.value)} placeholder="0" />
          </div>
          <div className="filter-group">
            <label>Max Score</label>
            <input type="number" min="0" max="10" step="0.1" value={filters.max_score} onChange={(e) => updateFilter('max_score', e.target.value)} placeholder="10" />
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading reviews...</div>
      ) : data.reviews.length === 0 ? (
        <div className="empty-state">
          <h3>No reviews found</h3>
          <p>Try adjusting your filters or submit a new review.</p>
        </div>
      ) : (
        <>
          <div className="review-table-wrap">
            <table className="review-table">
              <thead>
                <tr>
                  <th>PR Title</th>
                  <th>Status</th>
                  <th>Score</th>
                  <th>Findings</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.reviews.map((r) => (
                  <tr key={r.id}>
                    <td className="td-title">{r.pr_title || 'Untitled'}</td>
                    <td><StatusBadge status={r.status} /></td>
                    <td><ScoreBadge score={r.overall_score} /></td>
                    <td>{r.findings_count}</td>
                    <td className="text-muted">{new Date(r.created_at).toLocaleDateString()}</td>
                    <td>
                      <Link to={`/reviews/${r.id}`} className="btn btn-sm btn-secondary">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {data.total_pages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-sm btn-secondary"
                disabled={data.page <= 1}
                onClick={() => setFilters((p) => ({ ...p, page: p.page - 1 }))}
              >
                <HiChevronLeft /> Prev
              </button>
              <span className="pagination-info">
                Page {data.page} of {data.total_pages}
              </span>
              <button
                className="btn btn-sm btn-secondary"
                disabled={data.page >= data.total_pages}
                onClick={() => setFilters((p) => ({ ...p, page: p.page + 1 }))}
              >
                Next <HiChevronRight />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
