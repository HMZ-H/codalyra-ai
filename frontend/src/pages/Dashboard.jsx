import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { projects as projectsApi, health } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { HiPlus, HiFolder, HiCheck, HiX } from 'react-icons/hi';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const { user } = useAuth();
  const [projectList, setProjectList] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [apiHealth, setApiHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProjects = async () => {
    try {
      const res = await projectsApi.list();
      setProjectList(res.data);
    } catch {
      toast.error('Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
    health.check()
      .then(() => setApiHealth(true))
      .catch(() => setApiHealth(false));
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await projectsApi.create(newProject);
      toast.success('Project created');
      setNewProject({ name: '', description: '' });
      setShowCreate(false);
      fetchProjects();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create project');
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete project "${name}"?`)) return;
    try {
      await projectsApi.delete(id);
      toast.success('Project deleted');
      fetchProjects();
    } catch {
      toast.error('Failed to delete project');
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="text-muted">Welcome, {user?.full_name || user?.username}</p>
        </div>
        <div className="header-actions">
          <span className={`status-badge ${apiHealth ? 'status-ok' : 'status-err'}`}>
            {apiHealth ? <><HiCheck /> API Online</> : <><HiX /> API Offline</>}
          </span>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <HiPlus /> New Project
          </button>
        </div>
      </div>

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>New Project</h3>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Name</label>
                <input
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="My Project"
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="What is this project about?"
                  rows={3}
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading projects...</div>
      ) : projectList.length === 0 ? (
        <div className="empty-state">
          <HiFolder className="empty-icon" />
          <h3>No projects yet</h3>
          <p>Create your first project to start evaluating AI agents</p>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <HiPlus /> Create Project
          </button>
        </div>
      ) : (
        <div className="card-grid">
          {projectList.map((project) => (
            <div key={project.id} className="card">
              <div className="card-header">
                <Link to={`/projects/${project.id}`} className="card-title">
                  <HiFolder className="card-icon" />
                  {project.name}
                </Link>
                <button
                  className="btn-icon btn-danger-ghost"
                  onClick={() => handleDelete(project.id, project.name)}
                  title="Delete"
                >
                  <HiX />
                </button>
              </div>
              <p className="card-desc">{project.description || 'No description'}</p>
              <div className="card-footer">
                <span className="text-muted text-sm">
                  {new Date(project.created_at).toLocaleDateString()}
                </span>
                <Link to={`/projects/${project.id}`} className="btn btn-sm btn-secondary">
                  Open
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
