import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { reviews, projects as projectsApi } from '../api/client';
import toast from 'react-hot-toast';

const SAMPLE_DIFF = `diff --git a/app/api/users.py b/app/api/users.py
--- a/app/api/users.py
+++ b/app/api/users.py
@@ -15,6 +15,12 @@ def get_user(user_id: int, db: Session = Depends(get_db)):
     return user

+@router.get("/search")
+def search_users(q: str, db: Session = Depends(get_db)):
+    query = f"SELECT * FROM users WHERE name LIKE '%{q}%'"
+    results = db.execute(query)
+    return results.fetchall()
+
 @router.post("/")
 def create_user(user: UserCreate, db: Session = Depends(get_db)):
     password = "default123"
`;

export default function ReviewSubmit({ isOpen, onClose }) {
  const navigate = useNavigate();
  const [projectList, setProjectList] = useState([]);
  const [projectId, setProjectId] = useState('');
  const [prTitle, setPrTitle] = useState('');
  const [diffContent, setDiffContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      projectsApi.list().then((res) => {
        setProjectList(res.data);
        if (res.data.length > 0 && !projectId) {
          setProjectId(res.data[0].id);
        }
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!projectId) {
      toast.error('Please select a project');
      return;
    }
    if (!diffContent.trim()) {
      toast.error('Please paste a diff');
      return;
    }

    setSubmitting(true);
    try {
      const res = await reviews.create({
        project_id: projectId,
        pr_title: prTitle || 'Code Review',
        diff_content: diffContent,
      });
      toast.success('Review started! Agents are analyzing your code...');
      onClose();
      navigate(`/reviews/${res.data.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start review');
    } finally {
      setSubmitting(false);
    }
  };

  const loadSample = () => {
    setDiffContent(SAMPLE_DIFF);
    setPrTitle('Add user search endpoint');
    toast.success('Sample diff loaded');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
        <h3>Start Code Review</h3>
        <p className="text-muted" style={{ marginBottom: '1rem' }}>
          Paste a unified diff and our multi-agent pipeline will analyze it for bugs, security issues, performance problems, and code quality.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group" style={{ flex: 1 }}>
              <label>Project</label>
              <select value={projectId} onChange={(e) => setProjectId(e.target.value)} required>
                <option value="">Select project...</option>
                {projectList.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ flex: 2 }}>
              <label>Title (optional)</label>
              <input
                value={prTitle}
                onChange={(e) => setPrTitle(e.target.value)}
                placeholder="e.g., Add user search endpoint"
              />
            </div>
          </div>

          <div className="form-group">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <label>Unified Diff</label>
              <button type="button" className="btn btn-sm btn-secondary" onClick={loadSample}>
                Load Sample Diff
              </button>
            </div>
            <textarea
              value={diffContent}
              onChange={(e) => setDiffContent(e.target.value)}
              placeholder="Paste your unified diff here (output of git diff)..."
              rows={14}
              className="diff-textarea"
              required
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? 'Starting Review...' : 'Start Review'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
