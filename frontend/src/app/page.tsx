'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import styles from "./page.module.css";

export default function Home() {
	useEffect(() => {
		// Check if user is already logged in
		const token = localStorage.getItem('token');
		if (token) {
			window.location.href = '/dashboard';
		}
	}, []);

	return (
		<div className={styles.container}>
			<main className={styles.main}>
				<div className={styles.hero}>
					<h1 className={styles.title}>Welcome to Auth Template</h1>
					<p className={styles.description}>
						A complete authentication system with FastAPI and Next.js
					</p>
					<div className={styles.authButtons}>
						<Link href="/login" className={styles.loginButton}>
							Sign In
						</Link>
						<Link href="/signup" className={styles.signupButton}>
							Sign Up
						</Link>
					</div>
				</div>
				
				<div className={styles.features}>
					<h2>Backend</h2>
					<ul className={styles.featureList}>
						<li>🔒 Email/Password, Google, Microsoft, Facebook, Strava Authentication</li>
						<li>🗄️ PostgreSQL Database</li>
						<li>🚀 FastAPI Backend</li>
						<li>🔐 JWT Token Authentication</li>
					</ul>
					<h2>Frontend</h2>
					<ul className={styles.featureList}>
						<li>⚡ Next.js Frontend</li>
						<li>🎨 Tailwind CSS</li>
						<li>🌐 Default translation implementation</li>
					</ul>
				</div>
			</main>
		</div>
	);
}
