
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Login() {
    const navigate = useNavigate();
    const location = useLocation();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const notice = location.state?.notice;

    const handleLogin = async (e) => {
        e.preventDefault();

        setError("");
        setLoading(true);

        try {
            const response = await api.post("users/login/", {
                username: username,
                password: password,
            });

            const user = response.data.user;
            const tokens = response.data.tokens;

            if (!user?.id || !tokens?.access || !tokens?.refresh) {
                throw new Error("Invalid login response from server.");
            }

            localStorage.setItem("access", tokens.access);
            localStorage.setItem("refresh", tokens.refresh);
            localStorage.setItem("user_id", String(user.id));
            localStorage.setItem("username", user.username);
            window.dispatchEvent(new Event("socialconnect:auth-change"));

            const destination = location.state?.from;
            navigate(
                destination
                    ? `${destination.pathname || "/"}${destination.search || ""}${destination.hash || ""}`
                    : "/",
                { replace: true }
            );

        } catch (err) {
            const data = err.response?.data;
            const messages = data && typeof data === "object"
                ? Object.values(data).flat().filter((value) => typeof value === "string")
                : [];
            setError(messages[0] || "Unable to log in. Check your details and try again.");

        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="auth-page login-page">
            <div className="auth-card">

                <span className="auth-eyebrow">WELCOME TO SOCIALCONNECT</span>

                <h1>Welcome back</h1>

                <p className="auth-intro">Log in to catch up with your community.</p>

                {notice && <p className="form-success" role="status">{notice}</p>}
                {error && (
                    <p className="form-error" role="alert">{error}</p>
                )}

                <form onSubmit={handleLogin}>
                    <label htmlFor="login-username">Username</label>
                    <input
                        id="login-username"
                        type="text"
                        autoComplete="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <label htmlFor="login-password">Password</label>
                    <div className="password-field">
                        <input
                            id="login-password"
                            type={showPassword ? "text" : "password"}
                            autoComplete="current-password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                        <button
                            type="button"
                            className="password-toggle"
                            onClick={() => setShowPassword((visible) => !visible)}
                            aria-label={showPassword ? "Hide password" : "Show password"}
                        >
                            {showPassword ? "Hide" : "Show"}
                        </button>
                    </div>

                    <button
                        className="button-primary auth-submit"
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? "Signing in..." : "Log in"}
                    </button>

                </form>

                <p className="auth-footer">
                    New to SocialConnect?{" "}
                    <Link to="/register">Create an account</Link>
                </p>

            </div>
        </main>
    );
}

export default Login;
