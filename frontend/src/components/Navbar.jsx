import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiOutlineLogout, HiOutlineViewGrid } from 'react-icons/hi';

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
              <span className="nav-user">{user.username}</span>
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
