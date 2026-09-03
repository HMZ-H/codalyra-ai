import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiOutlineLogout, HiOutlineViewGrid, HiServer, HiCode } from 'react-icons/hi';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="brand-icon">⚡</span>
          Codalyra
        </Link>
        <div className="navbar-links">
          {user ? (
            <>
              <Link to="/dashboard" className="nav-link">
                <HiOutlineViewGrid /> Dashboard
              </Link>
              <Link to="/github" className="nav-link">
                <HiCode /> GitHub
              </Link>
              <Link to="/workers" className="nav-link">
                <HiServer /> Workers
              </Link>
              <div className="nav-user">
                {user.avatar_url && <img src={user.avatar_url} alt="" className="nav-avatar" />}
                {user.username}
              </div>
              <button onClick={handleLogout} className="nav-link btn-link">
                <HiOutlineLogout /> Logout
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link nav-link-primary">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
