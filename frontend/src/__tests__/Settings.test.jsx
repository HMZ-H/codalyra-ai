import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';
import Settings from '../pages/Settings';

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: { username: 'testuser', github_username: null } }),
}));

const mockGetStatus = vi.fn();
const mockUpdateKey = vi.fn();
const mockDeleteKey = vi.fn();

vi.mock('../api/client', () => ({
  settings: {
    getApiKeyStatus: (...args) => mockGetStatus(...args),
    updateApiKey: (...args) => mockUpdateKey(...args),
    deleteProviderKey: (...args) => mockDeleteKey(...args),
  },
}));

vi.mock('react-hot-toast', () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));

function renderSettings() {
  return render(
    <MemoryRouter>
      <Settings />
    </MemoryRouter>
  );
}

describe('Settings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockGetStatus.mockResolvedValue({
      data: {
        has_gemini_key: false,
        has_openai_key: false,
        has_anthropic_key: false,
      },
    });
  });

  it('shows loading state', () => {
    mockGetStatus.mockReturnValue(new Promise(() => {}));
    renderSettings();
    expect(screen.getByText('Loading settings...')).toBeInTheDocument();
  });

  it('renders all three provider sections', async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText('Google Gemini')).toBeInTheDocument();
      expect(screen.getByText('OpenAI')).toBeInTheDocument();
      expect(screen.getByText('Anthropic')).toBeInTheDocument();
    });
  });

  it('shows Save Key buttons when no keys configured', async () => {
    renderSettings();
    await waitFor(() => {
      const saveButtons = screen.getAllByText('Save Key');
      expect(saveButtons).toHaveLength(3);
    });
  });

  it('shows Active badge when key is configured', async () => {
    mockGetStatus.mockResolvedValueOnce({
      data: {
        has_gemini_key: true,
        gemini_key_preview: 'AIza...xxxx',
        has_openai_key: false,
        has_anthropic_key: false,
      },
    });
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText('Active')).toBeInTheDocument();
      expect(screen.getByText('Update Key')).toBeInTheDocument();
    });
  });

  it('shows Connect GitHub button when not connected', async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText('Connect GitHub Account')).toBeInTheDocument();
    });
  });

  it('saves API key on button click', async () => {
    mockUpdateKey.mockResolvedValueOnce({});
    mockGetStatus
      .mockResolvedValueOnce({
        data: { has_gemini_key: false, has_openai_key: false, has_anthropic_key: false },
      })
      .mockResolvedValueOnce({
        data: { has_gemini_key: true, gemini_key_preview: 'AIza...test', has_openai_key: false, has_anthropic_key: false },
      });

    renderSettings();
    await waitFor(() => screen.getByText('Google Gemini'));

    const inputs = screen.getAllByPlaceholderText(/AIza|sk-/);
    fireEvent.change(inputs[0], { target: { value: 'AIzaSyTest123456' } });

    const saveButtons = screen.getAllByText('Save Key');
    fireEvent.click(saveButtons[0]);

    await waitFor(() => {
      expect(mockUpdateKey).toHaveBeenCalledWith({ gemini_api_key: 'AIzaSyTest123456' });
    });
  });

  it('shows encryption notice', async () => {
    renderSettings();
    await waitFor(() => {
      expect(screen.getByText(/keys are encrypted at rest/i)).toBeInTheDocument();
    });
  });
});
