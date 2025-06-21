'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuthToken } from '@/hooks/useAuthToken';

interface User {
    id: string;
    email: string;
    full_name?: string;
    username?: string;
    avatar_url?: string;
    is_verified: boolean;
    created_at: string;
}

interface SimpleAuthLayoutProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
    redirectTo?: string;
    requireAuth?: boolean;
}

export default function SimpleAuthLayout({ 
    children, 
    fallback,
    redirectTo = '/login',
    requireAuth = true 
}: SimpleAuthLayoutProps) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { token, clearToken, isAuthenticated } = useAuthToken();
    const fetchedTokenRef = useRef<string | null>(null);

    useEffect(() => {
        let mounted = true;
        
        const checkAuth = async () => {
            console.log('SimpleAuthLayout: checkAuth called', { 
                token: !!token, 
                isAuthenticated, 
                requireAuth,
                fetchedToken: fetchedTokenRef.current,
                tokenChanged: fetchedTokenRef.current !== token
            });

            // If authentication is not required, just render children
            if (!requireAuth) {
                console.log('SimpleAuthLayout: Auth not required');
                if (mounted) setLoading(false);
                return;
            }

            // If no token or not authenticated, redirect
            if (!token || !isAuthenticated) {
                console.log('SimpleAuthLayout: No token, redirecting');
                window.location.href = redirectTo;
                return;
            }

            // If we already fetched data for this token, don't fetch again
            if (fetchedTokenRef.current === token && user) {
                console.log('SimpleAuthLayout: Token already processed');
                if (mounted) setLoading(false);
                return;
            }

            // Only fetch if token has changed
            if (fetchedTokenRef.current !== token) {
                console.log('SimpleAuthLayout: Fetching user data');
                fetchedTokenRef.current = token;

                try {
                    const response = await fetch('/api/auth/standard/me', {
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    });

                    if (!mounted) return; // Component unmounted

                    if (response.ok) {
                        const userData = await response.json();
                        console.log('SimpleAuthLayout: User data received');
                        setUser(userData);
                        setError('');
                    } else {
                        console.log('SimpleAuthLayout: Invalid response, clearing token');
                        clearToken();
                        window.location.href = redirectTo;
                        return;
                    }
                } catch (err) {
                    console.error('SimpleAuthLayout: Auth check failed:', err);
                    if (mounted) {
                        setError('Authentication failed');
                        if (requireAuth) {
                            clearToken();
                            window.location.href = redirectTo;
                        }
                    }
                }
            }

            if (mounted) setLoading(false);
        };

        checkAuth();

        return () => {
            mounted = false;
        };
    }, [token]); // Only depend on token

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
