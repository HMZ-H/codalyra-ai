import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiOutlineLogout, HiOutlineViewGrid, HiServer, HiCode, HiSun, HiMoon, HiCog, HiChartBar, HiUserGroup } from 'react-icons/hi';
import useTheme from '../hooks/useTheme';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { isDark, toggle } = useTheme();

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
              <Link to="/analytics" className="nav-link">
                <HiChartBar /> Analytics
              </Link>
              <Link to="/teams" className="nav-link">
                <HiUserGroup /> Teams
              </Link>
              <Link to="/workers" className="nav-link">
                <HiServer /> Workers
              </Link>
              <Link to="/settings" className="nav-link">
                <HiCog /> Settings
              </Link>
              <div className="nav-user">
                {user.avatar_url && <img src={user.avatar_url} alt="" className="nav-avatar" />}
                {user.username}
              </div>
              <button onClick={toggle} className="theme-toggle" title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
                {isDark ? <HiSun /> : <HiMoon />}
              </button>
              <button onClick={handleLogout} className="nav-link btn-link">
                <HiOutlineLogout /> Logout
              </button>
            </>
          ) : (
            <>
              <button onClick={toggle} className="theme-toggle" title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}>
                {isDark ? <HiSun /> : <HiMoon />}
              </button>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link nav-link-primary">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
