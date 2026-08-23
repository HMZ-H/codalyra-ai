import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { projects as projectsApi, repositories as reposApi, tasks as tasksApi } from '../api/client';
import { HiPlus, HiCode, HiClipboardList, HiArrowLeft, HiPencil, HiTrash, HiX } from 'react-icons/hi';
import toast from 'react-hot-toast';

function CreateRepoModal({ projectId, onClose, onCreated }) {
  const [form, setForm] = useState({ name: '', url: '', language: '', default_branch: 'main', project_id: projectId });
  const update = (f) => (e) => setForm({ ...form, [f]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await reposApi.create(form);
      toast.success('Repository added');
      onCreated();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add repository');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>Add Repository</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Name</label>
            <input value={form.name} onChange={update('name')} placeholder="my-repo" required autoFocus />
          </div>
          <div className="form-group">
            <label>URL</label>
            <input value={form.url} onChange={update('url')} placeholder="https://github.com/user/repo" required />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Language</label>
              <select value={form.language} onChange={update('language')}>
                <option value="">Select...</option>
                <option value="python">Python</option>
                <option value="go">Go</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="rust">Rust</option>
              </select>
            </div>
            <div className="form-group">
              <label>Default Branch</label>
              <input value={form.default_branch} onChange={update('default_branch')} />
            </div>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary">Add Repository</button>
          </div>
        </form>
      </div>
    </div>
  );
}

function CreateTaskModal({ projectId, repos, onClose, onCreated }) {
  const [form, setForm] = useState({
    title: '', description: '', difficulty: 'medium', status: 'draft',
    time_limit_seconds: 300, project_id: projectId, repository_id: '',
  });
  const update = (f) => (e) => setForm({ ...form, [f]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = { ...form };
    if (!data.repository_id) delete data.repository_id;
    try {
      await tasksApi.create(data);
      toast.success('Task created');
      onCreated();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create task');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
        <h3>New Task</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Title</label>
            <input value={form.title} onChange={update('title')} placeholder="Fix authentication bug" required autoFocus />
          </div>
          <div className="form-group">
            <label>Description</label>
            <textarea value={form.description} onChange={update('description')} placeholder="Describe what the agent needs to do..." rows={4} required />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Difficulty</label>
              <select value={form.difficulty} onChange={update('difficulty')}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div className="form-group">
              <label>Status</label>
              <select value={form.status} onChange={update('status')}>
                <option value="draft">Draft</option>
                <option value="active">Active</option>
                <option value="archived">Archived</option>
              </select>
            </div>
            <div className="form-group">
              <label>Time Limit (s)</label>
              <input type="number" value={form.time_limit_seconds} onChange={update('time_limit_seconds')} min={30} />
            </div>
          </div>
          <div className="form-group">
            <label>Repository (optional)</label>
            <select value={form.repository_id} onChange={update('repository_id')}>
              <option value="">None</option>
              {repos.map((r) => <option key={r.id} value={r.id}>{r.name}</option>)}
            </select>
          </div>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary">Create Task</button>
          </div>
        </form>
      </div>
    </div>
  );
}

const difficultyColor = { easy: 'badge-green', medium: 'badge-yellow', hard: 'badge-red' };
const statusColor = { draft: 'badge-gray', active: 'badge-green', archived: 'badge-gray' };

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [repos, setRepos] = useState([]);
  const [taskList, setTaskList] = useState([]);
  const [showRepoModal, setShowRepoModal] = useState(false);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({ name: '', description: '' });

  const fetchAll = async () => {
    try {
      const [p, r, t] = await Promise.all([
        projectsApi.get(id),
        reposApi.list(id),
        tasksApi.list(id),
      ]);
      setProject(p.data);
      setRepos(r.data);
      setTaskList(t.data);
      setEditForm({ name: p.data.name, description: p.data.description || '' });
    } catch {
      toast.error('Failed to load project');
      navigate('/dashboard');
    }
  };

  useEffect(() => { fetchAll(); }, [id]);

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await projectsApi.update(id, editForm);
      toast.success('Project updated');
      setEditing(false);
      fetchAll();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed');
    }
  };

  const deleteRepo = async (repoId, name) => {
    if (!confirm(`Delete repository "${name}"?`)) return;
    try {
      await reposApi.delete(repoId);
      toast.success('Repository deleted');
      fetchAll();
    } catch {
      toast.error('Failed to delete');
    }
  };

  const deleteTask = async (taskId, title) => {
    if (!confirm(`Delete task "${title}"?`)) return;
    try {
      await tasksApi.delete(taskId);
      toast.success('Task deleted');
      fetchAll();
    } catch {
      toast.error('Failed to delete');
    }
  };

  if (!project) return <div className="loading">Loading...</div>;

  return (
    <div className="page">
      <Link to="/dashboard" className="back-link"><HiArrowLeft /> Back to Dashboard</Link>

      <div className="page-header">
        <div>
          {editing ? (
            <form onSubmit={handleUpdate} className="inline-edit">
              <input
                value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                className="edit-title"
                autoFocus
              />
              <input
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                className="edit-desc"
                placeholder="Description"
              />
              <div className="edit-actions">
                <button type="submit" className="btn btn-sm btn-primary">Save</button>
                <button type="button" className="btn btn-sm btn-secondary" onClick={() => setEditing(false)}>Cancel</button>
              </div>
            </form>
          ) : (
            <>
              <h1>{project.name} <button className="btn-icon" onClick={() => setEditing(true)}><HiPencil /></button></h1>
              <p className="text-muted">{project.description || 'No description'}</p>
            </>
          )}
        </div>
      </div>

      {/* Repositories */}
      <section className="section">
        <div className="section-header">
          <h2><HiCode /> Repositories ({repos.length})</h2>
          <button className="btn btn-sm btn-primary" onClick={() => setShowRepoModal(true)}>
            <HiPlus /> Add
          </button>
        </div>
        {repos.length === 0 ? (
          <p className="text-muted text-center">No repositories yet</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Name</th><th>URL</th><th>Language</th><th>Branch</th><th></th></tr>
              </thead>
              <tbody>
                {repos.map((repo) => (
                  <tr key={repo.id}>
                    <td className="font-medium">{repo.name}</td>
                    <td className="text-muted text-sm">{repo.url}</td>
                    <td><span className="badge badge-blue">{repo.language || '-'}</span></td>
                    <td className="text-sm">{repo.default_branch}</td>
                    <td>
                      <button className="btn-icon btn-danger-ghost" onClick={() => deleteRepo(repo.id, repo.name)}>
                        <HiTrash />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Tasks */}
      <section className="section">
        <div className="section-header">
          <h2><HiClipboardList /> Tasks ({taskList.length})</h2>
          <button className="btn btn-sm btn-primary" onClick={() => setShowTaskModal(true)}>
            <HiPlus /> New Task
          </button>
        </div>
        {taskList.length === 0 ? (
          <p className="text-muted text-center">No tasks yet</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Title</th><th>Difficulty</th><th>Status</th><th>Time Limit</th><th>Created</th><th></th></tr>
              </thead>
              <tbody>
                {taskList.map((task) => (
                  <tr key={task.id}>
                    <td className="font-medium">{task.title}</td>
                    <td><span className={`badge ${difficultyColor[task.difficulty] || ''}`}>{task.difficulty}</span></td>
                    <td><span className={`badge ${statusColor[task.status] || ''}`}>{task.status}</span></td>
                    <td className="text-sm">{task.time_limit_seconds}s</td>
                    <td className="text-muted text-sm">{new Date(task.created_at).toLocaleDateString()}</td>
                    <td>
                      <button className="btn-icon btn-danger-ghost" onClick={() => deleteTask(task.id, task.title)}>
                        <HiTrash />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {showRepoModal && <CreateRepoModal projectId={id} onClose={() => setShowRepoModal(false)} onCreated={fetchAll} />}
      {showTaskModal && <CreateTaskModal projectId={id} repos={repos} onClose={() => setShowTaskModal(false)} onCreated={fetchAll} />}
    </div>
  );
}
