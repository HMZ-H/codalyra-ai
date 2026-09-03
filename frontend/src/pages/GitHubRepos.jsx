import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { github, projects as projectsApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { HiArrowLeft, HiCode, HiLockClosed, HiGlobe, HiPlus, HiRefresh } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function GitHubRepos() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [repos, setRepos] = useState([]);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [selectedProject, setSelectedProject] = useState('');
  const [connecting, setConnecting] = useState(null);
  const [expandedRepo, setExpandedRepo] = useState(null);
  const [pulls, setPulls] = useState({});
  const [loadingPulls, setLoadingPulls] = useState(null);
  const [reviewingPr, setReviewingPr] = useState(null);

  const isConnected = !!user?.github_username;

  useEffect(() => {
    if (!isConnected) {
      setLoading(false);
      return;
    }
    Promise.all([
      github.listRepos(page),
      projectsApi.list(),
    ])
      .then(([reposRes, projRes]) => {
        setRepos(reposRes.data);
        setProjects(projRes.data);
        if (projRes.data.length > 0 && !selectedProject) {
          setSelectedProject(projRes.data[0].id);
        }
      })
      .catch(() => toast.error('Failed to load repos'))
      .finally(() => setLoading(false));
  }, [page, isConnected]);

  const connectRepo = async (repo) => {
    if (!selectedProject) {
      toast.error('Select a project first');
      return;
    }
    setConnecting(repo.name);
    try {
      await github.connectRepo({
        project_id: selectedProject,
        name: repo.name,
        url: repo.url,
        clone_url: repo.clone_url,
        default_branch: repo.default_branch,
        language: repo.language,
      });
      toast.success(`${repo.name} connected!`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to connect');
    } finally {
      setConnecting(null);
    }
  };

  const togglePulls = async (repo) => {
    const key = repo.full_name;
    if (expandedRepo === key) {
      setExpandedRepo(null);
      return;
    }
    setExpandedRepo(key);
    if (pulls[key]) return;

    setLoadingPulls(key);
    try {
      const [owner, name] = key.split('/');
      const res = await github.listPulls(owner, name);
      setPulls((prev) => ({ ...prev, [key]: res.data }));
    } catch {
      toast.error('Failed to load PRs');
    } finally {
      setLoadingPulls(null);
    }
  };

  const reviewPR = async (repoFullName, pr) => {
    if (!selectedProject) {
      toast.error('Select a project first');
      return;
    }
    setReviewingPr(`${repoFullName}#${pr.number}`);
    try {
      const [owner, repo] = repoFullName.split('/');
      const res = await github.reviewPull(owner, repo, pr.number, {
        project_id: selectedProject,
      });
      toast.success('Review started!');
      navigate(`/reviews/${res.data.review_id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start review');
    } finally {
      setReviewingPr(null);
    }
  };

  if (!isConnected) {
    return (
      <div className="page">
        <div className="empty-state">
          <HiCode className="empty-icon" />
          <h3>GitHub Not Connected</h3>
          <p>Log in with GitHub to connect your repositories and review PRs automatically.</p>
          <button className="btn btn-primary" onClick={() => navigate('/login')}>
            Connect GitHub
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <button className="back-link" onClick={() => navigate('/dashboard')}><HiArrowLeft /> Dashboard</button>
          <h1>GitHub Repositories</h1>
          <p className="text-muted">Connected as @{user.github_username}</p>
        </div>
        <div className="header-actions">
          <select value={selectedProject} onChange={(e) => setSelectedProject(e.target.value)} style={{ marginRight: '0.5rem' }}>
            <option value="">Select project...</option>
            {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <button className="btn btn-secondary" onClick={() => { setLoading(true); setPage(1); github.listRepos(1).then((r) => { setRepos(r.data); setLoading(false); }); }}>
            <HiRefresh /> Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading">Loading repositories...</div>
      ) : repos.length === 0 ? (
        <div className="empty-state">
          <h3>No repositories found</h3>
          <p>Make sure your GitHub account has repositories.</p>
        </div>
      ) : (
        <>
          <div className="card-grid" style={{ gridTemplateColumns: '1fr' }}>
            {repos.map((repo) => (
              <div key={repo.github_id} className="card">
                <div className="card-header">
                  <div className="card-title" style={{ cursor: 'pointer' }} onClick={() => togglePulls(repo)}>
                    {repo.private ? <HiLockClosed className="card-icon" /> : <HiGlobe className="card-icon" />}
                    {repo.full_name}
                    {repo.language && <span className="tag" style={{ marginLeft: '0.5rem', fontSize: '0.7rem' }}>{repo.language}</span>}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button className="btn btn-sm btn-secondary" onClick={() => togglePulls(repo)}>
                      PRs
                    </button>
                    <button
                      className="btn btn-sm btn-primary"
                      onClick={() => connectRepo(repo)}
                      disabled={connecting === repo.name}
                    >
                      {connecting === repo.name ? '...' : <><HiPlus /> Connect</>}
                    </button>
                  </div>
                </div>
                {repo.description && <p className="card-desc">{repo.description}</p>}

                {expandedRepo === repo.full_name && (
                  <div style={{ marginTop: '0.75rem', borderTop: '1px solid var(--border-color, #2a3040)', paddingTop: '0.75rem' }}>
                    {loadingPulls === repo.full_name ? (
                      <div className="text-muted" style={{ fontSize: '0.85rem' }}>Loading pull requests...</div>
                    ) : !pulls[repo.full_name]?.length ? (
                      <div className="text-muted" style={{ fontSize: '0.85rem' }}>No open pull requests</div>
                    ) : (
                      pulls[repo.full_name].map((pr) => (
                        <div key={pr.number} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.4rem 0', borderBottom: '1px solid var(--border-color, #1a2030)' }}>
                          <div>
                            <span style={{ color: '#2c8c7c', fontWeight: 500, marginRight: '0.5rem' }}>#{pr.number}</span>
                            <span style={{ fontSize: '0.88rem' }}>{pr.title}</span>
                            <span className="text-muted" style={{ fontSize: '0.75rem', marginLeft: '0.5rem' }}>{pr.head_branch} → {pr.base_branch}</span>
                          </div>
                          <button
                            className="btn btn-sm btn-accent"
                            onClick={() => reviewPR(repo.full_name, pr)}
                            disabled={reviewingPr === `${repo.full_name}#${pr.number}`}
                          >
                            {reviewingPr === `${repo.full_name}#${pr.number}` ? 'Starting...' : 'Review'}
                          </button>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '1.5rem' }}>
            {page > 1 && <button className="btn btn-secondary" onClick={() => setPage(page - 1)}>Previous</button>}
            <span className="text-muted" style={{ alignSelf: 'center' }}>Page {page}</span>
            {repos.length === 30 && <button className="btn btn-secondary" onClick={() => setPage(page + 1)}>Next</button>}
          </div>
        </>
      )}
    </div>
  );
}
