'use client';
import styles from "./page.module.css";

import React, { useState } from 'react';
import Link from 'next/link';

import { useAuthToken } from '@/hooks/useAuthToken';
import { resolveBackendUrl } from '@/lib/apiClient';

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { setToken } = useAuthToken();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(resolveBackendUrl('/auth/standard/login'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token);
                window.location.href = '/dashboard';
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Login failed');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleOAuthLogin = async (provider: string) => {
        setError('');

        try {
            const response = await fetch(resolveBackendUrl(`/auth/${provider}/login`), {
                method: 'GET',
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error('Failed to initiate OAuth login');
            }

            const data = await response.json();

            if (data?.auth_url) {
                window.location.href = data.auth_url;
            } else {
                throw new Error('Missing auth URL');
            }
        } catch (oauthError) {
            console.error(oauthError);
            setError('Unable to start OAuth login. Please try again.');
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.loginCard}>
                <h1 className={styles.title}>Welcome Back</h1>
                <p className={styles.subtitle}>Sign in to your account</p>

                {error && <div className={styles.error}>{error}</div>}

                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                            required
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter your password"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={loading}
                    >
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>

                <div className={styles.divider}>
                    <span>Or continue with</span>
                </div>

                <div className={styles.oauthButtons}>
                    <button 
                        onClick={() => handleOAuthLogin('google')}
                        className={`${styles.oauthButton} ${styles.google}`}
                    >
                        <span>Google</span>
                    </button>
                    
                    <button 
                        onClick={() => handleOAuthLogin('microsoft')}
                        className={`${styles.oauthButton} ${styles.microsoft}`}
                    >
                        <span>Microsoft</span>
                    </button>
                    
                    <button 
                        onClick={() => handleOAuthLogin('facebook')}
                        className={`${styles.oauthButton} ${styles.facebook}`}
                    >
                        <span>Facebook</span>
                    </button>
                    
                    <button 
                        onClick={() => handleOAuthLogin('strava')}
                        className={`${styles.oauthButton} ${styles.strava}`}
                    >
                        <span>Strava</span>
                    </button>
                </div>

                <p className={styles.registerLink}>
                    Don't have an account?{' '}
                    <Link href="/signup">Sign up</Link>
                </p>
            </div>
        </div>
    );
}