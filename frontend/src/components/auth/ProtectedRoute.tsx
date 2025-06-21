'use client';

import React from 'react';
import SimpleAuthLayout, { useAuth } from './SimpleAuthLayout';
import LoadingSpinner from '../loader/LoadingSpinner';

interface ProtectedRouteProps {
    children: React.ReactNode;
    redirectTo?: string;
    loadingMessage?: string;
    fallback?: React.ReactNode;
}

export default function ProtectedRoute({ 
    children, 
    redirectTo = '/login',
    loadingMessage = 'Checking authentication...',
    fallback 
}: ProtectedRouteProps) {
    const defaultFallback = (
        <div style={{ height: '100vh' }}>
            <LoadingSpinner 
                size="large" 
                message={loadingMessage} 
                fullScreen 
            />
        </div>
    );

    return (
        <SimpleAuthLayout 
            requireAuth={true}
            redirectTo={redirectTo}
            fallback={fallback || defaultFallback}
        >
            {children}
        </SimpleAuthLayout>
    );
}

// Re-export useAuth for convenience
export { useAuth };
