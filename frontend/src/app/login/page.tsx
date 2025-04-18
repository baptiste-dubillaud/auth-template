import styles from "@/app/login/page.module.css";

export default LoginPage => {
    return (
        <div className={styles.container}>
            <div className={styles.login}>
                <h1>Login</h1>
                <form action="/api/login" method="POST">
                    <input type="text" name="username" placeholder="Username" required />
                    <input type="password" name="password" placeholder="Password" required />
                    <button type="submit">Login</button>
                </form>
            </div>
            <div className={styles.register}>
                <h1>Register</h1>
            </div>
        </div>
    )
}