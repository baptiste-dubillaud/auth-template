import { useCallback, useMemo } from 'react';
import { useLocalStorage } from './useLocalStorage';

// Custom hook specifically for authentication token management
export function useAuthToken() {
  const [token, setTokenValue, removeToken] = useLocalStorage<string | null>('token', null);

  const setToken = useCallback((newToken: string) => {
    setTokenValue(newToken);
  }, [setTokenValue]);

  const clearToken = useCallback(() => {
    removeToken();
  }, [removeToken]);

  const isAuthenticated = useMemo(() => Boolean(token), [token]);

  return {
    token,
    setToken,
    clearToken,
    isAuthenticated
  };
}
