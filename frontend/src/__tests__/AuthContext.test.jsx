import { render, screen, waitFor, act } from '@testing-library/react';
import { vi } from 'vitest';
import { AuthProvider, useAuth } from '../context/AuthContext';

const mockPost = vi.fn();
const mockGet = vi.fn();

vi.mock('../api/client', () => ({
  auth: {
    login: (...args) => mockPost(...args),
    register: (...args) => mockPost(...args),
    me: () => mockGet(),
    githubCallback: (...args) => mockPost(...args),
  },
}));

function TestComponent() {
  const { user, loading, login, logout } = useAuth();
  if (loading) return <div>Loading...</div>;
  return (
    <div>
      <span data-testid="user">{user ? user.username : 'none'}</span>
      <button onClick={() => login('a@b.com', 'pass')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

function renderWithAuth() {
  return render(
    <AuthProvider>
      <TestComponent />
    </AuthProvider>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('starts with no user when no token', async () => {
    renderWithAuth();
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('none');
    });
  });

  it('loads user from token on mount', async () => {
    localStorage.setItem('token', 'test-token');
    mockGet.mockResolvedValueOnce({ data: { username: 'loaded-user' } });

    renderWithAuth();
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('loaded-user');
    });
  });

  it('clears token on failed auth check', async () => {
    localStorage.setItem('token', 'bad-token');
    mockGet.mockRejectedValueOnce(new Error('401'));

    renderWithAuth();
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('none');
      expect(localStorage.getItem('token')).toBeNull();
    });
  });

  it('login stores token and sets user', async () => {
    mockPost.mockResolvedValueOnce({ data: { access_token: 'new-token' } });
    mockGet.mockResolvedValueOnce({ data: { username: 'new-user' } });

    renderWithAuth();
    await waitFor(() => screen.getByTestId('user'));

    await act(async () => {
      screen.getByText('Login').click();
    });

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('new-token');
      expect(screen.getByTestId('user')).toHaveTextContent('new-user');
    });
  });

  it('logout removes token and user', async () => {
    localStorage.setItem('token', 'test-token');
    mockGet.mockResolvedValueOnce({ data: { username: 'current' } });

    renderWithAuth();
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('current');
    });

    act(() => {
      screen.getByText('Logout').click();
    });

    expect(screen.getByTestId('user')).toHaveTextContent('none');
    expect(localStorage.getItem('token')).toBeNull();
  });
});
