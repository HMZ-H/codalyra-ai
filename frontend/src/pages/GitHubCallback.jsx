import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function GitHubCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { loginWithGithub } = useAuth();
  const [error, setError] = useState(null);

  useEffect(() => {
    const code = searchParams.get('code');
    if (!code) {
      setError('No authorization code received');
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
      });
  }, []);

  if (error) {
    return (
      <div className="page" style={{ textAlign: 'center', paddingTop: '4rem' }}>
        <h2>Login Failed</h2>
        <p className="text-muted">{error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/login')} style={{ marginTop: '1rem' }}>
          Back to Login
        </button>
      </div>
    );
  }

  return (
    <div className="page" style={{ textAlign: 'center', paddingTop: '4rem' }}>
      <div className="loading">Signing in with GitHub...</div>
    </div>
  );
}
