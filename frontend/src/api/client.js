import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const auth = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  me: () => client.get('/auth/me'),
  githubCallback: (code) => client.post('/auth/github/callback', { code }),
  connectGithub: (code) => client.post('/auth/github/connect', { code }),
};

export const projects = {
  list: () => client.get('/projects/'),
  get: (id) => client.get(`/projects/${id}`),
  create: (data) => client.post('/projects/', data),
  update: (id, data) => client.put(`/projects/${id}`, data),
  delete: (id) => client.delete(`/projects/${id}`),
};

export const repositories = {
  list: (projectId) => client.get(`/repositories/?project_id=${projectId}`),
  get: (id) => client.get(`/repositories/${id}`),
  create: (data) => client.post('/repositories/', data),
  update: (id, data) => client.put(`/repositories/${id}`, data),
  delete: (id) => client.delete(`/repositories/${id}`),
};

export const tasks = {
  list: (projectId) => client.get(`/tasks/?project_id=${projectId}`),
  get: (id) => client.get(`/tasks/${id}`),
  create: (data) => client.post('/tasks/', data),
  update: (id, data) => client.put(`/tasks/${id}`, data),
  delete: (id) => client.delete(`/tasks/${id}`),
};

export const runs = {
  list: (taskId) => client.get(`/runs/?task_id=${taskId}`),
  get: (id) => client.get(`/runs/${id}`),
  create: (data) => client.post('/runs/', data),
  execute: (id) => client.post(`/runs/${id}/execute`),
  evaluate: (id) => client.post(`/runs/${id}/evaluate`),
};

export const evaluations = {
  getByRun: (runId) => client.get(`/evaluations/run/${runId}`),
};

export const trajectories = {
  getByRun: (runId) => client.get(`/trajectories/run/${runId}`),
};

export const reviews = {
  create: (data) => client.post('/reviews/', data),
  list: (projectId) => client.get(`/reviews/?project_id=${projectId}`),
  get: (id) => client.get(`/reviews/${id}`),
  report: (id) => client.get(`/reviews/${id}/report`),
  autoFix: (id) => client.post(`/reviews/${id}/auto-fix`),
};

export const github = {
  listRepos: (page = 1) => client.get(`/github/repos?page=${page}`),
  connectRepo: (data) => client.post('/github/repos/connect', data),
  listPulls: (owner, repo, state = 'open') => client.get(`/github/repos/${owner}/${repo}/pulls?state=${state}`),
  getPullDiff: (owner, repo, prNumber) => client.get(`/github/repos/${owner}/${repo}/pulls/${prNumber}/diff`),
  reviewPull: (owner, repo, prNumber, data) => client.post(`/github/repos/${owner}/${repo}/pulls/${prNumber}/review`, data),
  postComments: (owner, repo, prNumber, data) => client.post(`/github/repos/${owner}/${repo}/pulls/${prNumber}/post-comments`, data),
};

export const settings = {
  getApiKeyStatus: () => client.get('/settings/api-keys'),
  updateApiKey: (data) => client.put('/settings/api-keys', typeof data === 'string' ? { gemini_api_key: data } : data),
  deleteApiKey: () => client.delete('/settings/api-keys'),
  deleteProviderKey: (provider) => client.delete(`/settings/api-keys/${provider}`),
};

export const analytics = {
  overview: () => client.get('/analytics/overview'),
  reviews: (params) => client.get('/analytics/reviews', { params }),
  scoreTrends: (params) => client.get('/analytics/score-trends', { params }),
  categories: (params) => client.get('/analytics/categories', { params }),
  agents: (params) => client.get('/analytics/agents', { params }),
};

export const agentConfigs = {
  list: (projectId) => client.get(`/projects/${projectId}/agents`),
  update: (projectId, agentType, data) => client.put(`/projects/${projectId}/agents/${agentType}`, data),
  reset: (projectId, agentType) => client.delete(`/projects/${projectId}/agents/${agentType}`),
  providers: (projectId) => client.get(`/projects/${projectId}/agents/providers`),
};

export const teams = {
  list: () => client.get('/teams/'),
  get: (id) => client.get(`/teams/${id}`),
  create: (data) => client.post('/teams/', data),
  update: (id, data) => client.put(`/teams/${id}`, data),
  delete: (id) => client.delete(`/teams/${id}`),
  listMembers: (id) => client.get(`/teams/${id}/members`),
  addMember: (id, data) => client.post(`/teams/${id}/members`, data),
  updateMember: (teamId, memberId, data) => client.put(`/teams/${teamId}/members/${memberId}`, data),
  removeMember: (teamId, memberId) => client.delete(`/teams/${teamId}/members/${memberId}`),
};

export const health = {
  check: () => client.get('/health'),
  db: () => client.get('/health/db'),
};

export default client;
