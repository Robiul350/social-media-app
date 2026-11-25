import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";

function Register() {
    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        username: "",
        email: "",
        password: "",
        password2: "",
    });

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setError("");

        if (formData.password.length < 8) {
            setError("Use at least 8 characters for your password.");
            return;
        }

        if (formData.password !== formData.password2) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);

        try {
            await api.post("users/register/", formData);
            navigate("/login", {
                replace: true,
                state: { notice: "Your account is ready. Log in to continue." },
            });
        } catch (err) {
            const data = err.response?.data;
            const firstMessage = data && typeof data === "object"
                ? Object.values(data).flat().find((value) => typeof value === "string")
                : "";
            setError(firstMessage || err.message || "Unable to create your account. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="auth-page register-page">
            <div className="auth-info">
                <h1>Social<span>Connect</span></h1>
                <h2>Join our growing community!</h2>
                <p>
                    Create your account and start sharing your
                    experiences with people around the world.
                </p>
            </div>

            <div className="auth-card">
                <div className="auth-heading">
                    <div className="auth-logo">SC</div>
                    <h2>Create Account</h2>
                    <p>Sign up and become part of our community.</p>
                </div>

                <form onSubmit={handleRegister}>
                    {error && <div className="form-error">{error}</div>}

                    <label>Username</label>
                    <input
                        name="username"
                        placeholder="Choose a username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                    />

                    <label>Email Address</label>
                    <input
                        name="email"
                        type="email"
                        placeholder="Enter your email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />

                    <label>Password</label>
                    <input
                        name="password"
                        type="password"
                        placeholder="Create a password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />

                    <label>Confirm Password</label>
                    <input
                        name="password2"
                        type="password"
                        placeholder="Confirm your password"
                        value={formData.password2}
                        onChange={handleChange}
                        required
                    />

                    <button type="submit" disabled={loading}>
                        {loading ? "Creating Account..." : "Create Account"}
                    </button>
                </form>

                <div className="auth-footer">
                    Already have an account?
                    <Link to="/login"> Login</Link>
                </div>
            </div>
        </main>
    );
}

export default Register;