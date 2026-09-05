import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';
import Dashboard from '../pages/Dashboard';

const mockProjects = [
  { id: '1', name: 'Project Alpha', description: 'First project', created_at: '2025-01-01T00:00:00Z' },
  { id: '2', name: 'Project Beta', description: '', created_at: '2025-02-01T00:00:00Z' },
];

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: { username: 'testuser', full_name: 'Test User' } }),
}));

vi.mock('../api/client', () => ({
  projects: {
    list: vi.fn().mockResolvedValue({ data: [] }),
    create: vi.fn().mockResolvedValue({ data: {} }),
    delete: vi.fn().mockResolvedValue({}),
  },
  health: {
    check: vi.fn().mockResolvedValue({}),
    db: vi.fn().mockResolvedValue({}),
  },
}));

vi.mock('../components/ReviewSubmit', () => ({
  default: ({ isOpen }) => isOpen ? <div data-testid="review-modal">Review Modal</div> : null,
}));

vi.mock('react-hot-toast', () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));

function renderDashboard() {
  return render(
    <MemoryRouter>
      <Dashboard />
    </MemoryRouter>
  );
}

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows welcome message with user name', async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText(/welcome, test user/i)).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    renderDashboard();
    expect(screen.getByText('Loading projects...')).toBeInTheDocument();
  });

  it('shows empty state when no projects', async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText('No projects yet')).toBeInTheDocument();
    });
  });

  it('renders projects when loaded', async () => {
    const { projects } = await import('../api/client');
    projects.list.mockResolvedValueOnce({ data: mockProjects });

    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText('Project Alpha')).toBeInTheDocument();
      expect(screen.getByText('Project Beta')).toBeInTheDocument();
    });
  });

  it('shows project count in stats', async () => {
    const { projects } = await import('../api/client');
    projects.list.mockResolvedValueOnce({ data: mockProjects });

    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument();
    });
  });

  it('shows API health status', async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText('API Online')).toBeInTheDocument();
    });
  });

  it('opens create project modal', async () => {
    renderDashboard();
    await waitFor(() => screen.getByText(/new project/i));
    fireEvent.click(screen.getByRole('button', { name: /new project/i }));
    expect(screen.getByPlaceholderText('My Project')).toBeInTheDocument();
  });

  it('opens review modal on Review Code click', async () => {
    renderDashboard();
    await waitFor(() => screen.getByText(/review code/i));
    fireEvent.click(screen.getByRole('button', { name: /review code/i }));
    expect(screen.getByTestId('review-modal')).toBeInTheDocument();
  });

  it('shows "No description" for projects without description', async () => {
    const { projects } = await import('../api/client');
    projects.list.mockResolvedValueOnce({ data: mockProjects });

    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText('No description')).toBeInTheDocument();
    });
  });
});
