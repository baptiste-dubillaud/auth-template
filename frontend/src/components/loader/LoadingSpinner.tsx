import React from 'react';

interface LoadingSpinnerProps {
    size?: 'small' | 'medium' | 'large';
    message?: string;
    fullScreen?: boolean;
}

export default function LoadingSpinner({ 
    size = 'medium', 
    message = 'Loading...',
    fullScreen = false 
}: LoadingSpinnerProps) {
    const sizeMap = {
        small: '20px',
        medium: '40px',
        large: '60px'
    };

    const spinnerSize = sizeMap[size];

    const containerStyle: React.CSSProperties = {
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        gap: '15px',
        ...(fullScreen && {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            zIndex: 9999
        })
    };

    const spinnerStyle: React.CSSProperties = {
        width: spinnerSize,
        height: spinnerSize,
        border: '3px solid #f3f3f3',
        borderTop: '3px solid #007bff',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite'
    };

    return (
        <div style={containerStyle}>
            <style jsx>{`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>
            <div style={spinnerStyle} />
            {message && (
                <p style={{ 
                    margin: 0, 
                    fontSize: size === 'small' ? '14px' : '16px',
                    color: '#666'
                }}>
                    {message}
                </p>
            )}
        </div>
    );
}
