import { Link } from "react-router-dom";

function AuthWelcomePanel() {
    return (
        <section className="auth-welcome-panel" aria-label="About SocialConnect">
            <Link to="/login" className="auth-brand" aria-label="SocialConnect">
                <span className="auth-brand-mark" aria-hidden="true">S</span>
                <span>SocialConnect</span>
            </Link>
            <div className="auth-welcome-copy">
                <p className="auth-eyebrow">YOUR COMMUNITY, IN ONE PLACE</p>
                <h2>Good conversations start here.</h2>
                <p>Catch up with friends, share everyday moments, and keep the people you care about close.</p>
                <ul>
                    <li>See updates from your community</li>
                    <li>Share photos, videos, and thoughts</li>
                    <li>Stay in touch through messages</li>
                </ul>
            </div>
            <p className="auth-welcome-footer">A place to connect, share, and belong.</p>
        </section>
    );
}

export default AuthWelcomePanel;
