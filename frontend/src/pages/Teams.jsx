import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { teams as teamsApi } from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  HiPlus, HiUserGroup, HiArrowLeft, HiX, HiTrash,
  HiPencil, HiMail, HiShieldCheck,
} from 'react-icons/hi';
import toast from 'react-hot-toast';

const ROLE_LABELS = {
  admin: { label: 'Admin', color: '#ef4444' },
  reviewer: { label: 'Reviewer', color: '#f59e0b' },
  viewer: { label: 'Viewer', color: '#3b82f6' },
};

export default function Teams() {
  const { user } = useAuth();
  const [teamList, setTeamList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newTeam, setNewTeam] = useState({ name: '', slug: '', description: '' });
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [members, setMembers] = useState([]);
  const [showAddMember, setShowAddMember] = useState(false);
  const [newMember, setNewMember] = useState({ email: '', role: 'viewer' });

  const fetchTeams = async () => {
    try {
      const res = await teamsApi.list();
      setTeamList(res.data);
    } catch {
      toast.error('Failed to load teams');
    } finally {
      setLoading(false);
    }
  };

  const fetchMembers = async (teamId) => {
    try {
      const res = await teamsApi.listMembers(teamId);
      setMembers(res.data);
    } catch {
      toast.error('Failed to load members');
    }
  };

  useEffect(() => { fetchTeams(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await teamsApi.create(newTeam);
      toast.success('Team created');
      setNewTeam({ name: '', slug: '', description: '' });
      setShowCreate(false);
      fetchTeams();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create team');
    }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`Delete team "${name}"? This cannot be undone.`)) return;
    try {
      await teamsApi.delete(id);
      toast.success('Team deleted');
      setSelectedTeam(null);
      fetchTeams();
    } catch {
      toast.error('Failed to delete team');
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    try {
      await teamsApi.addMember(selectedTeam.id, newMember);
      toast.success('Member added');
      setNewMember({ email: '', role: 'viewer' });
      setShowAddMember(false);
      fetchMembers(selectedTeam.id);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to add member');
    }
  };

  const handleRemoveMember = async (memberId) => {
    try {
      await teamsApi.removeMember(selectedTeam.id, memberId);
      toast.success('Member removed');
      fetchMembers(selectedTeam.id);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  const handleRoleChange = async (memberId, newRole) => {
    try {
      await teamsApi.updateMember(selectedTeam.id, memberId, { role: newRole });
      toast.success('Role updated');
      fetchMembers(selectedTeam.id);
    } catch {
      toast.error('Failed to update role');
    }
  };

  const openTeam = (team) => {
    setSelectedTeam(team);
    fetchMembers(team.id);
  };

  if (loading) return <div className="page"><div className="loading">Loading teams...</div></div>;

  if (selectedTeam) {
    const isOwner = selectedTeam.owner_id === user?.id;
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <button className="back-link" onClick={() => setSelectedTeam(null)}>
              <HiArrowLeft /> All Teams
            </button>
            <h1>{selectedTeam.name}</h1>
            {selectedTeam.description && (
              <p className="text-muted">{selectedTeam.description}</p>
            )}
          </div>
          <div className="header-actions">
            {isOwner && (
              <>
                <button className="btn btn-primary" onClick={() => setShowAddMember(true)}>
                  <HiPlus /> Add Member
                </button>
                <button className="btn btn-secondary btn-danger-ghost" onClick={() => handleDelete(selectedTeam.id, selectedTeam.name)}>
                  <HiTrash /> Delete Team
                </button>
              </>
            )}
          </div>
        </div>

        {showAddMember && (
          <div className="modal-overlay" onClick={() => setShowAddMember(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()}>
              <h3>Add Team Member</h3>
              <form onSubmit={handleAddMember}>
                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    value={newMember.email}
                    onChange={(e) => setNewMember({ ...newMember, email: e.target.value })}
                    placeholder="user@example.com"
                    required
                    autoFocus
                  />
                </div>
                <div className="form-group">
                  <label>Role</label>
                  <select
                    value={newMember.role}
                    onChange={(e) => setNewMember({ ...newMember, role: e.target.value })}
                  >
                    <option value="viewer">Viewer</option>
                    <option value="reviewer">Reviewer</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div className="modal-actions">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowAddMember(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Add</button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="card" style={{ maxWidth: 700 }}>
          <h3 style={{ marginBottom: '1rem' }}><HiUserGroup style={{ verticalAlign: 'middle', marginRight: 8 }} />Members ({members.length})</h3>
          {members.map((m) => {
            const roleInfo = ROLE_LABELS[m.role] || ROLE_LABELS.viewer;
            return (
              <div key={m.id} className="team-member-row">
                <div className="team-member-info">
                  <span className="team-member-name">{m.full_name || m.username}</span>
                  <span className="text-muted text-sm">{m.email}</span>
                </div>
                <div className="team-member-actions">
                  {isOwner && m.user_id !== user?.id ? (
                    <select
                      value={m.role}
                      onChange={(e) => handleRoleChange(m.id, e.target.value)}
                      className="role-select"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="reviewer">Reviewer</option>
                      <option value="admin">Admin</option>
                    </select>
                  ) : (
                    <span className="role-badge" style={{ color: roleInfo.color }}>{roleInfo.label}</span>
                  )}
                  {isOwner && m.user_id !== user?.id && (
                    <button className="btn-icon btn-danger-ghost" onClick={() => handleRemoveMember(m.id)} title="Remove">
                      <HiX />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/dashboard" className="back-link"><HiArrowLeft /> Dashboard</Link>
          <h1>Teams</h1>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          <HiPlus /> New Team
        </button>
      </div>

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Create Team</h3>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Name</label>
                <input
                  value={newTeam.name}
                  onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                  placeholder="My Team"
                  required
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Slug</label>
                <input
                  value={newTeam.slug}
                  onChange={(e) => setNewTeam({ ...newTeam, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })}
                  placeholder="my-team"
                  required
                />
                <small className="text-muted">URL-friendly identifier (lowercase, hyphens only)</small>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newTeam.description}
                  onChange={(e) => setNewTeam({ ...newTeam, description: e.target.value })}
                  placeholder="What is this team about?"
                  rows={2}
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

      {teamList.length === 0 ? (
        <div className="empty-state">
          <HiUserGroup className="empty-icon" />
          <h3>No teams yet</h3>
          <p>Create a team to collaborate with others on code reviews</p>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <HiPlus /> Create Team
          </button>
        </div>
      ) : (
        <div className="card-grid">
          {teamList.map((team) => (
            <div key={team.id} className="card" style={{ cursor: 'pointer' }} onClick={() => openTeam(team)}>
              <div className="card-header">
                <span className="card-title">
                  <HiUserGroup className="card-icon" />
                  {team.name}
                </span>
              </div>
              <p className="card-desc">{team.description || 'No description'}</p>
              <div className="card-footer">
                <span className="text-muted text-sm">{team.member_count} members</span>
                <span className="badge badge-green">{team.slug}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
