import { createContext, useContext, useState, useEffect } from 'react';
import { auth } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      auth.me()
        .then((res) => setUser(res.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await auth.login({ email, password });
    localStorage.setItem('token', res.data.access_token);
    const me = await auth.me();
    setUser(me.data);
    return me.data;
  };

  const register = async (data) => {
    await auth.register(data);
    return login(data.email, data.password);
  };

  const loginWithGithub = async (code) => {
    const res = await auth.githubCallback(code);
    localStorage.setItem('token', res.data.access_token);
    const me = await auth.me();
    setUser(me.data);
    return me.data;
  };

  const refreshUser = async () => {
    const me = await auth.me();
    setUser(me.data);
    return me.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, loginWithGithub, refreshUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
