// login.tsx - Simple user login page (front-end only demo)
// @ts-nocheck
import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { signIn } from '../utils/auth';

const cardStyle: React.CSSProperties = {
  background: '#fff',
  border: '1px solid #e5e7eb',
  borderRadius: 12,
  padding: 20,
  boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '10px 12px',
  borderRadius: 8,
  border: '1px solid #e5e7eb',
  outline: 'none'
};

const LoginPage: React.FC = () => {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
  try {
  await signIn(email, password, remember);
  // redirect to dashboard and replace history so back doesn't return to login
  router.replace('/');
    } catch (err: any) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f7f7f9', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        <div style={cardStyle}>
          <div style={{ marginBottom: 12, textAlign: 'center' }}>
            <h2 style={{ margin: 0 }}>Sign in</h2>
            <p style={{ color: '#6b7280', margin: '6px 0 0' }}>Use your account to access the dashboard.</p>
          </div>

          {error && (
            <div style={{ background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', padding: 10, borderRadius: 8, marginBottom: 12 }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: 10 }}>
              <label style={{ display: 'block', fontSize: 12, color: '#6b7280', marginBottom: 6 }}>Email</label>
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={inputStyle}
                autoComplete="email"
                required
              />
            </div>
            <div style={{ marginBottom: 10 }}>
              <label style={{ display: 'block', fontSize: 12, color: '#6b7280', marginBottom: 6 }}>Password</label>
              <input
                type="password"
                placeholder=""
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={inputStyle}
                autoComplete="current-password"
                required
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, userSelect: 'none' }}>
                <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
                <span style={{ color: '#111827' }}>Remember me</span>
              </label>
              <a href="#" style={{ color: '#2563eb', textDecoration: 'none' }} onClick={(e) => e.preventDefault()}>Forgot password?</a>
            </div>

            <button type="submit" disabled={loading} style={{
              width: '100%', marginTop: 14, background: '#111827', color: '#fff', padding: '10px 14px',
              borderRadius: 8, border: '1px solid #0b1220', cursor: 'pointer', fontWeight: 600
            }}>
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

        </div>
      </div>
    </div>
  );
};

export default LoginPage;
