'use client';

import React from 'react';
import ProtectedRoute, { useAuth } from '@/components/auth/ProtectedRoute';
import styles from "./page.module.css";

function DashboardContent() {
    const { user, clearToken } = useAuth();

    const handleLogout = () => {
        clearToken();
        window.location.href = '/login';
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>Dashboard</h1>
                <button onClick={handleLogout} className={styles.logoutButton}>
                    Logout
                </button>
            </div>
            
            <div className={styles.userCard}>
                <div className={styles.userInfo}>
                    {user?.avatar_url && (
                        <img 
                            src={user.avatar_url} 
                            alt="Profile" 
                            className={styles.avatar}
                        />
                    )}
                    <div>
                        <h2>{user?.full_name || user?.username || 'User'}</h2>
                        <p className={styles.email}>{user?.email}</p>
                        <span className={`${styles.status} ${user?.is_verified ? styles.verified : styles.unverified}`}>
                            {user?.is_verified ? 'Verified' : 'Unverified'}
                        </span>
                    </div>
                </div>
                
                <div className={styles.userDetails}>
                    <h3>Account Details</h3>
                    <div className={styles.detailItem}>
                        <strong>User ID:</strong> {user?.id}
                    </div>
                    <div className={styles.detailItem}>
                        <strong>Member since:</strong> {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </div>
                    {user?.username && (
                        <div className={styles.detailItem}>
                            <strong>Username:</strong> {user.username}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function DashboardPage() {
    return (
        <ProtectedRoute loadingMessage="Loading your dashboard...">
            <DashboardContent />
        </ProtectedRoute>
    );
}
