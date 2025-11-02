// _app.tsx
// Enforce fresh login on every frontend start: clear any stored tokens on initial load
// and redirect to /login unless already on the login page.
// This runs only once per full app load (won't log you out after you've logged in during the same session).

import type { AppProps } from 'next/app';
import { useRouter } from 'next/router';
import React from 'react';

const App = ({ Component, pageProps }: AppProps) => {
  const router = useRouter();
  const [initialized, setInitialized] = React.useState(false);

  React.useEffect(() => {
    // Clear both localStorage and sessionStorage tokens to force re-login on app start
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth.token');
        localStorage.removeItem('auth.user');
        sessionStorage.removeItem('auth.token');
        sessionStorage.removeItem('auth.user');
      }
    } catch {}
    // Redirect to login unless we're already on it
    if (router.pathname !== '/login') {
      router.replace('/login');
    }
    setInitialized(true);
    // only run once on first mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // To avoid flicker, allow rendering login immediately; for other pages wait for init.
  const isLogin = router.pathname === '/login';
  if (!initialized && !isLogin) return null;

  return <Component {...pageProps} />;
};

export default App;
