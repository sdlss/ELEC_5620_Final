// auth.ts - minimal front-end only auth helpers (demo)

export type AuthUser = { email: string };

const TOKEN_KEY = 'auth.token';
const USER_KEY = 'auth.user';

const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function signIn(
  email: string,
  password: string,
  remember = true
): Promise<{ token: string; user: AuthUser }> {
  const e = (email || '').trim();
  const p = (password || '').trim();
  if (!e || !p) throw new Error('Email and password are required');

  // Call backend to verify against database
  const res = await fetch(`${baseURL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: e, password: p })
  });
  if (!res.ok) {
    let msg = 'Login failed';
    try { const j = await res.json(); msg = j?.detail || msg; } catch {}
    throw new Error(msg);
  }
  const data = await res.json();
  const token = data?.token as string;
  const user = (data?.user as AuthUser) || { email: e };
  if (!token) throw new Error('Invalid server response');

  try {
    if (remember) {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      sessionStorage.setItem(TOKEN_KEY, token);
      sessionStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  } catch {}
  return { token, user };
}

export function signOut() {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
  } catch {}
}

export function getToken(): string | null {
  try {
    return (
      localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
    );
  } catch {
    return null;
  }
}

export function getCurrentUser(): AuthUser | null {
  try {
    const raw =
      localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}
