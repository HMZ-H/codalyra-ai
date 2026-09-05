import { vi } from 'vitest';

vi.mock('axios', () => {
  const interceptors = {
    request: { use: vi.fn() },
    response: { use: vi.fn() },
  };
  const instance = {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} }),
    put: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({ data: {} }),
    interceptors,
  };
  return {
    default: { create: vi.fn(() => instance) },
  };
});

describe('API Client modules', () => {
  let client, auth, projects, reviews, settings, agentConfigs, health;

  beforeEach(async () => {
    vi.resetModules();
    const mod = await import('../api/client');
    client = mod.default;
    auth = mod.auth;
    projects = mod.projects;
    reviews = mod.reviews;
    settings = mod.settings;
    agentConfigs = mod.agentConfigs;
    health = mod.health;
  });

  describe('auth', () => {
    it('calls register endpoint', async () => {
      const data = { email: 'a@b.com', password: '123' };
      await auth.register(data);
      expect(client.post).toHaveBeenCalledWith('/auth/register', data);
    });

    it('calls login endpoint', async () => {
      const data = { email: 'a@b.com', password: '123' };
      await auth.login(data);
      expect(client.post).toHaveBeenCalledWith('/auth/login', data);
    });

    it('calls me endpoint', async () => {
      await auth.me();
      expect(client.get).toHaveBeenCalledWith('/auth/me');
    });
  });

  describe('projects', () => {
    it('lists projects', async () => {
      await projects.list();
      expect(client.get).toHaveBeenCalledWith('/projects/');
    });

    it('gets a project by id', async () => {
      await projects.get('abc');
      expect(client.get).toHaveBeenCalledWith('/projects/abc');
    });

    it('creates a project', async () => {
      await projects.create({ name: 'Test' });
      expect(client.post).toHaveBeenCalledWith('/projects/', { name: 'Test' });
    });

    it('deletes a project', async () => {
      await projects.delete('abc');
      expect(client.delete).toHaveBeenCalledWith('/projects/abc');
    });
  });

  describe('reviews', () => {
    it('creates a review', async () => {
      await reviews.create({ diff: 'test' });
      expect(client.post).toHaveBeenCalledWith('/reviews/', { diff: 'test' });
    });

    it('gets review report', async () => {
      await reviews.report('r1');
      expect(client.get).toHaveBeenCalledWith('/reviews/r1/report');
    });
  });

  describe('settings', () => {
    it('gets api key status', async () => {
      await settings.getApiKeyStatus();
      expect(client.get).toHaveBeenCalledWith('/settings/api-keys');
    });

    it('updates api key with object', async () => {
      await settings.updateApiKey({ openai_api_key: 'sk-test' });
      expect(client.put).toHaveBeenCalledWith('/settings/api-keys', { openai_api_key: 'sk-test' });
    });

    it('updates api key with string (legacy)', async () => {
      await settings.updateApiKey('AIzaTest');
      expect(client.put).toHaveBeenCalledWith('/settings/api-keys', { gemini_api_key: 'AIzaTest' });
    });

    it('deletes provider key', async () => {
      await settings.deleteProviderKey('openai');
      expect(client.delete).toHaveBeenCalledWith('/settings/api-keys/openai');
    });
  });

  describe('agentConfigs', () => {
    it('lists configs', async () => {
      await agentConfigs.list('p1');
      expect(client.get).toHaveBeenCalledWith('/projects/p1/agents');
    });

    it('updates agent config', async () => {
      await agentConfigs.update('p1', 'security', { temperature: 0.5 });
      expect(client.put).toHaveBeenCalledWith('/projects/p1/agents/security', { temperature: 0.5 });
    });

    it('resets agent config', async () => {
      await agentConfigs.reset('p1', 'logic');
      expect(client.delete).toHaveBeenCalledWith('/projects/p1/agents/logic');
    });

    it('gets providers', async () => {
      await agentConfigs.providers('p1');
      expect(client.get).toHaveBeenCalledWith('/projects/p1/agents/providers');
    });
  });

  describe('health', () => {
    it('checks health', async () => {
      await health.check();
      expect(client.get).toHaveBeenCalledWith('/health');
    });

    it('checks db health', async () => {
      await health.db();
      expect(client.get).toHaveBeenCalledWith('/health/db');
    });
  });
});
