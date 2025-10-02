'use client';

import React, { useState, useEffect } from 'react';
import { useAuthToken } from '@/hooks/useAuthToken';
import { resolveBackendUrl } from '@/lib/apiClient';

interface User {
    id: string;
    email: string;
    full_name?: string;
    username?: string;
    avatar_url?: string;
    is_verified: boolean;
    created_at: string;
}

interface AuthLayoutProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
    redirectTo?: string;
    requireAuth?: boolean;
}

export default function AuthLayout({ 
    children, 
    fallback,
    redirectTo = '/login',
    requireAuth = true 
}: AuthLayoutProps) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [lastCheckedToken, setLastCheckedToken] = useState<string | null>(null);
    const { token, clearToken, isAuthenticated } = useAuthToken();

    useEffect(() => {
        console.log('AuthLayout useEffect triggered', { token, isAuthenticated, requireAuth, user: !!user, lastCheckedToken });
        
        const checkAuth = async () => {
            try {
                // If authentication is not required, just render children
                if (!requireAuth) {
                    console.log('Auth not required, setting loading to false');
                    setLoading(false);
                    return;
                }

                // If no token or not authenticated, redirect
                if (!token || !isAuthenticated) {
                    console.log('No token or not authenticated, redirecting to:', redirectTo);
                    window.location.href = redirectTo;
                    return;
                }

                // If we already checked this token and have user data, skip the API call
                if (lastCheckedToken === token && user) {
                    console.log('Token already checked and user exists, skipping API call');
                    setLoading(false);
                    return;
                }

                console.log('Fetching user data from /me endpoint');
                // Fetch user data
                const response = await fetch(resolveBackendUrl('/auth/standard/me'), {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const userData = await response.json();
                    console.log('User data fetched successfully:', userData);
                    setUser(userData);
                    setLastCheckedToken(token);
                } else {
                    console.log('Invalid token response, clearing token and redirecting');
                    // Invalid token, clear it and redirect
                    clearToken();
                    window.location.href = redirectTo;
                    return;
                }
            } catch (err) {
                console.error('Auth check failed:', err);
                setError('Authentication failed');
                if (requireAuth) {
                    clearToken();
                    window.location.href = redirectTo;
                }
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, [token, isAuthenticated, requireAuth, redirectTo]); // Removed clearToken from dependencies

    // Show loading state
    if (loading) {
        return fallback || (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                fontSize: '18px'
            }}>
                Loading...
            </div>
        );
    }

    // Show error state
    if (error && requireAuth) {
        return (
            <div style={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center', 
                height: '100vh',
                flexDirection: 'column',
                gap: '20px'
            }}>
                <p style={{ color: 'red', fontSize: '18px' }}>{error}</p>
                <button 
                    onClick={() => window.location.href = redirectTo}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Go to Login
                </button>
            </div>
        );
    }

    // If authentication is required but user is not authenticated, don't render children
    if (requireAuth && !isAuthenticated) {
        return null;
    }

    // Render children with auth context
    return (
        <AuthContext.Provider value={{ user, isAuthenticated, token, clearToken }}>
            {children}
        </AuthContext.Provider>
    );
}

// Context for sharing auth state
interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    token: string | null;
    clearToken: () => void;
}

const AuthContext = React.createContext<AuthContextType | null>(null);

// Hook to use auth context
export function useAuth() {
    const context = React.useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthLayout');
    }
    return context;
}
