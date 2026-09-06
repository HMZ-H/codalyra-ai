import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { auth } from '../api/client';
import toast from 'react-hot-toast';

export default function GitHubCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, loading, loginWithGithub, refreshUser } = useAuth();
  const [error, setError] = useState(null);
  const [processing, setProcessing] = useState(true);

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code) {
      setError('No authorization code received');
      setProcessing(false);
      return;
    }

    if (state === 'connect') {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('You must be logged in to connect GitHub. Please log in and try again.');
        setProcessing(false);
        return;
      }

      auth.connectGithub(code)
        .then(() => {
          toast.success('GitHub account connected!');
          if (refreshUser) refreshUser();
          navigate('/settings', { replace: true });
        })
        .catch((err) => {
          const msg = err.response?.data?.detail || 'Failed to connect GitHub account';
          setError(msg);
          toast.error(msg);
          setProcessing(false);
        });
      return;
    }

    loginWithGithub(code)
      .then(() => {
        toast.success('Signed in with GitHub!');
        navigate('/dashboard');
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'GitHub login failed');
        toast.error('GitHub login failed');
        setProcessing(false);
      });
  }, []);

  if (error) {
    return (
      <div className="page" style={{ textAlign: 'center', paddingTop: '4rem' }}>
        <h2>GitHub Connection Failed</h2>
        <p className="text-muted">{error}</p>
        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginTop: '1rem' }}>
          <button className="btn btn-secondary" onClick={() => navigate('/settings')}>
            Back to Settings
          </button>
          <button className="btn btn-primary" onClick={() => navigate('/login')}>
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page" style={{ textAlign: 'center', paddingTop: '4rem' }}>
      <div className="loading">{processing ? 'Connecting to GitHub...' : 'Redirecting...'}</div>
    </div>
  );
}
