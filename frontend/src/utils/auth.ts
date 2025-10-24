// auth.ts - minimal front-end only auth helpers (demo)

export type AuthUser = { email: string };

const TOKEN_KEY = 'auth.token';
const USER_KEY = 'auth.user';

export function signIn(
  email: string,
  password: string,
  remember = true
): Promise<{ token: string; user: AuthUser }> {
  return new Promise((resolve, reject) => {
    // Very basic client-side check; replace with real API later
    const e = (email || '').trim();
    const p = (password || '').trim();
    if (!e || !p) {
      reject(new Error('Email and password are required'));
      return;
    }
    // Fake token: base64(email:timestamp)
    const token = btoa(`${e}:${Date.now()}`);
    const user: AuthUser = { email: e };

    try {
      if (remember) {
        localStorage.setItem(TOKEN_KEY, token);
        localStorage.setItem(USER_KEY, JSON.stringify(user));
      } else {
        sessionStorage.setItem(TOKEN_KEY, token);
        sessionStorage.setItem(USER_KEY, JSON.stringify(user));
      }
    } catch {}

    resolve({ token, user });
  });
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
