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
  updateApiKey: (gemini_api_key) => client.put('/settings/api-keys', { gemini_api_key }),
  deleteApiKey: () => client.delete('/settings/api-keys'),
};

export const health = {
  check: () => client.get('/health'),
  db: () => client.get('/health/db'),
};

export default client;
