'use client';

import React from 'react';

interface AppLayoutProps {
    children: React.ReactNode;
    showHeader?: boolean;
    showFooter?: boolean;
    title?: string;
}

export default function AppLayout({ 
    children, 
    showHeader = true, 
    showFooter = true,
    title 
}: AppLayoutProps) {
    React.useEffect(() => {
        if (title) {
            document.title = title;
        }
    }, [title]);

    return (
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            {showHeader && <Header />}
            <main style={{ flex: 1 }}>
                {children}
            </main>
            {showFooter && <Footer />}
        </div>
    );
}

function Header() {
    return (
        <header style={{
            padding: '1rem 2rem',
            borderBottom: '1px solid #e5e5e5',
            backgroundColor: 'white'
        }}>
            <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                    Auth Template
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    {/* Navigation items can be added here */}
                </div>
            </nav>
        </header>
    );
}

function Footer() {
    return (
        <footer style={{
            padding: '2rem',
            borderTop: '1px solid #e5e5e5',
            backgroundColor: '#f8f9fa',
            textAlign: 'center',
            color: '#666'
        }}>
            <p>&copy; 2025 Auth Template. All rights reserved.</p>
        </footer>
    );
}
