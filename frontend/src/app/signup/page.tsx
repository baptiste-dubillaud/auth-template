'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuthToken } from '@/hooks/useAuthToken';
import { resolveBackendUrl } from '@/lib/apiClient';
import styles from "./page.module.css";

export default function SignupPage() {

    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        fullName: '',
        username: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { setToken } = useAuthToken();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        // Validate passwords match
        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        // Validate password strength
        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(resolveBackendUrl('/auth/standard/register'), {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: formData.email,
                    password: formData.password,
                    full_name: formData.fullName,
                    username: formData.username
                }),
            });

            if (response.ok) {
                const data = await response.json();
                setToken(data.access_token);
                window.location.href = '/dashboard';
            } else {
                const errorData = await response.json();
                setError(errorData.detail || 'Registration failed');
            }
        } catch (err) {
            setError('Network error. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleOAuthSignup = async (provider: string) => {
        setError('');

        try {
            const response = await fetch(resolveBackendUrl(`/auth/${provider}/login`), {
                method: 'GET',
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error('Failed to initiate OAuth signup');
            }

            const data = await response.json();

            if (data?.auth_url) {
                window.location.href = data.auth_url;
            } else {
                throw new Error('Missing auth URL');
            }
        } catch (oauthError) {
            console.error(oauthError);
            setError('Unable to start OAuth signup. Please try again.');
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.signupCard}>
                <h1 className={styles.title}>Create Account</h1>
                <p className={styles.subtitle}>Sign up to get started</p>

                {error && <div className={styles.error}>{error}</div>}

                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <label htmlFor="fullName">Full Name</label>
                        <input
                            id="fullName"
                            name="fullName"
                            type="text"
                            value={formData.fullName}
                            onChange={handleChange}
                            placeholder="Enter your full name"
                            required
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="username">Username (Optional)</label>
                        <input
                            id="username"
                            name="username"
                            type="text"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Choose a username"
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="email">Email</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            value={formData.email}
                            onChange={handleChange}
                            placeholder="Enter your email"
                            required
                        />
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Create a password"
                            required
                        />
                        <small className={styles.passwordHint}>
                            Must be at least 8 characters long
                        </small>
                    </div>

                    <div className={styles.inputGroup}>
                        <label htmlFor="confirmPassword">Confirm Password</label>
                        <input
                            id="confirmPassword"
                            name="confirmPassword"
                            type="password"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            placeholder="Confirm your password"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={loading}
                    >
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </button>
                </form>

                <div className={styles.divider}>
                    <span>Or sign up with</span>
                </div>

                <div className={styles.oauthButtons}>
                    <button 
                        onClick={() => handleOAuthSignup('google')}
                        className={`${styles.oauthButton} ${styles.google}`}
                    >
                        <span>Google</span>
                    </button>
                    
                    <button 
                        onClick={() => handleOAuthSignup('microsoft')}
                        className={`${styles.oauthButton} ${styles.microsoft}`}
                    >
                        <span>Microsoft</span>
                    </button>
                    
                    <button 
                        onClick={() => handleOAuthSignup('facebook')}
                        className={`${styles.oauthButton} ${styles.facebook}`}
                    >
                        <span>Facebook</span>
                    </button>
                    
                    <button 
                        onClick={() => handleOAuthSignup('strava')}
                        className={`${styles.oauthButton} ${styles.strava}`}
                    >
                        <span>Strava</span>
                    </button>
                </div>

                <p className={styles.loginLink}>
                    Already have an account?{' '}
                    <Link href="/login">Sign in</Link>
                </p>
            </div>
        </div>
    );
}
