import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { getProfileSnapshot, loadProfile, resetProfile, subscribeProfile } from "../api/profileStore";
import ConfirmDialog from "./ConfirmDialog";
import Icon from "./Icon";
import NotificationSettingsDialog from "./NotificationSettingsDialog";
import UserAvatar from "./UserAvatar";

function Navbar({ onOpenDrawer }) {
    const navigate = useNavigate();
    const location = useLocation();
    const [search, setSearch] = useState("");
    const [isLoggedIn, setIsLoggedIn] = useState(() => Boolean(localStorage.getItem("access")));
    const [logoutConfirmation, setLogoutConfirmation] = useState(false);
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [profileMenuOpen, setProfileMenuOpen] = useState(false);
    const [unreadMessages, setUnreadMessages] = useState(0);
    const [unreadNotifications, setUnreadNotifications] = useState(0);
    const [countsError, setCountsError] = useState(false);
    const profileState = useSyncExternalStore(subscribeProfile, getProfileSnapshot, getProfileSnapshot);
    const profileMenuRef = useRef(null);
    const profileButtonRef = useRef(null);
    const [theme, setTheme] = useState(() => {
        const stored = localStorage.getItem("socialconnect-theme");
        if (stored === "dark" || stored === "light") return stored;
        return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    });

    useEffect(() => {
        loadProfile();
        const refreshProfile = () => loadProfile({ force: true });
        const syncAuth = () => {
            setIsLoggedIn(Boolean(localStorage.getItem("access")));
            loadProfile({ force: true });
            setProfileMenuOpen(false);
        };
        window.addEventListener("socialconnect:profile-change", refreshProfile);
        window.addEventListener("socialconnect:auth-change", syncAuth);
        window.addEventListener("storage", syncAuth);
        return () => {
            window.removeEventListener("socialconnect:profile-change", refreshProfile);
            window.removeEventListener("socialconnect:auth-change", syncAuth);
            window.removeEventListener("storage", syncAuth);
        };
    }, []);

    useEffect(() => {
        if (!isLoggedIn) return undefined;
        let active = true;
        const loadCounts = async () => {
            try {
                const [messagesResponse, notificationsResponse] = await Promise.all([
                    api.get("chat/unread-count/"),
                    api.get("notifications/unread-count/"),
                ]);
                if (!active) return;
                setUnreadMessages(Number(messagesResponse.data.unread_count) || 0);
                setUnreadNotifications(Number(notificationsResponse.data.unread_count) || 0);
                setCountsError(false);
            } catch {
                if (active) setCountsError(true);
            }
        };
        loadCounts();
        const interval = window.setInterval(loadCounts, 60000);
        window.addEventListener("socialconnect:refresh-counts", loadCounts);
        return () => {
            active = false;
            window.clearInterval(interval);
            window.removeEventListener("socialconnect:refresh-counts", loadCounts);
        };
    }, [isLoggedIn]);

    useEffect(() => {
        document.documentElement.dataset.theme = theme;
        localStorage.setItem("socialconnect-theme", theme);
        document.querySelector('meta[name="theme-color"]')?.setAttribute(
            "content",
            theme === "dark" ? "#18191A" : "#F8FAFC",
        );
    }, [theme]);

    useEffect(() => {
        if (!profileMenuOpen) return undefined;
        const handlePointerDown = (event) => {
            if (!profileMenuRef.current?.contains(event.target)) setProfileMenuOpen(false);
        };
        const handleKeyDown = (event) => {
            if (event.key === "Escape") {
                setProfileMenuOpen(false);
                profileButtonRef.current?.focus();
            }
        };
        document.addEventListener("pointerdown", handlePointerDown);
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.removeEventListener("pointerdown", handlePointerDown);
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [profileMenuOpen]);

    const logout = async () => {
        const refresh = localStorage.getItem("refresh");
        let notice;
        if (refresh) {
            try {
                await api.post("users/logout/", { refresh });
            } catch {
                notice = "You were signed out on this device, but the server could not confirm token revocation.";
            }
        }
        ["access", "refresh", "user_id", "username"].forEach((key) =>
            localStorage.removeItem(key)
        );
        resetProfile();
        window.dispatchEvent(new Event("socialconnect:auth-change"));
        setLogoutConfirmation(false);
        setProfileMenuOpen(false);
        navigate("/login", { replace: true, state: notice ? { notice } : undefined });
    };

    const submitSearch = (event) => {
        event.preventDefault();
        const query = search.trim();
        navigate(query ? `/search?query=${encodeURIComponent(query)}` : "/search");
        setSearch("");
    };

    const closeSettings = useCallback(() => setSettingsOpen(false), []);
    const topbarLinkClass = (isActive) =>
        `topbar-icon-link topbar-nav-link${isActive ? " is-active" : ""}`;

    const avatarSrc = profileState.data?.profile?.profile_picture || "";
    const username = localStorage.getItem("username") || "My account";

    return (
        <header className="top-navbar">
            <div className="nav-left">
                {isLoggedIn && onOpenDrawer && (
                    <button
                        type="button"
                        className="app-menu-button"
                        onClick={onOpenDrawer}
                        aria-label="Open navigation menu"
                    >
                        <Icon name="menu" />
                    </button>
                )}
                <Link to={isLoggedIn ? "/" : "/login"} className="brand">
                    <span className="brand-mark" aria-hidden="true">S</span>
                    <span className="brand-name">Social<span>Connect</span></span>
                </Link>
            </div>

            {isLoggedIn && (
                <nav className="topbar-nav" aria-label="Primary">
                    <NavLink end to="/" className={({ isActive }) => topbarLinkClass(isActive)} aria-label="Home" title="Home">
                        <Icon name="home" />
                        <span className="topbar-label">Home</span>
                    </NavLink>
                    <NavLink to="/search" className={({ isActive }) => topbarLinkClass(isActive)} aria-label="Explore people" title="Explore">
                        <Icon name="explore" />
                        <span className="topbar-label">Explore</span>
                    </NavLink>
                    <NavLink to="/connections/friends" className={({ isActive }) => topbarLinkClass(isActive)} aria-label="Friends" title="Friends">
                        <Icon name="friends" />
                        <span className="topbar-label">Friends</span>
                    </NavLink>
                    <NavLink to="/messages" className={({ isActive }) => topbarLinkClass(isActive)} aria-label="Messages" title="Messages">
                        <Icon name="messages" />
                        <span className="topbar-label">Messages</span>
                        {unreadMessages > 0 && <span className="topbar-count">{unreadMessages > 99 ? "99+" : unreadMessages}</span>}
                    </NavLink>
                    <NavLink to="/notifications" className={({ isActive }) => topbarLinkClass(isActive)} aria-label="Notifications" title="Notifications">
                        <Icon name="notifications" />
                        <span className="topbar-label">Notifications</span>
                        {unreadNotifications > 0 && <span className="topbar-count">{unreadNotifications > 99 ? "99+" : unreadNotifications}</span>}
                    </NavLink>
                    {countsError && <span className="sr-only" role="status">Unread counts are temporarily unavailable.</span>}
                </nav>
            )}

            {isLoggedIn && (
                <div className="nav-search">
                    <form onSubmit={submitSearch} role="search">
                        <Icon name="explore" />
                        <input
                            type="search"
                            value={search}
                            onChange={(event) => setSearch(event.target.value)}
                            placeholder="Search people..."
                            aria-label="Search people"
                        />
                    </form>
                </div>
            )}

            <div className="nav-right">
                <button
                    type="button"
                    className="theme-toggle"
                    onClick={() => setTheme((current) => current === "dark" ? "light" : "dark")}
                    aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
                    title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
                >
                    <Icon name={theme === "dark" ? "sun" : "moon"} />
                </button>
                {isLoggedIn ? (
                    <>
                        <button
                            type="button"
                            className="topbar-icon-link topbar-settings"
                            onClick={() => setSettingsOpen(true)}
                            aria-label="Notification settings"
                            title="Settings"
                        >
                            <Icon name="settings" />
                            <span className="topbar-label">Settings</span>
                        </button>
                        <div className="profile-menu-wrap" ref={profileMenuRef}>
                            <button
                                ref={profileButtonRef}
                                type="button"
                                className="nav-user"
                                onClick={() => setProfileMenuOpen((open) => !open)}
                                aria-label="Account menu"
                                aria-haspopup="menu"
                                aria-expanded={profileMenuOpen}
                            >
                                <UserAvatar
                                    className="nav-avatar"
                                    src={profileState.error ? "" : avatarSrc}
                                    name={username}
                                    interactive={false}
                                />
                                <span className="nav-username">{username}</span>
                                <Icon name="chevron" />
                            </button>
                            {profileMenuOpen && (
                                <div className="profile-menu" role="menu" onClick={() => setProfileMenuOpen(false)}>
                                    <div className="profile-menu-header">
                                        <strong>{username}</strong>
                                        <small>Signed in</small>
                                    </div>
                                    <Link role="menuitem" to="/profile" className="profile-menu-item">
                                        <Icon name="friends" /> My profile
                                    </Link>
                                    <Link role="menuitem" to="/connections/friends" className="profile-menu-item">
                                        <Icon name="friends" /> Friends
                                    </Link>
                                    <Link role="menuitem" to="/bookmarks" className="profile-menu-item">
                                        <Icon name="explore" /> Saved posts
                                    </Link>
                                    <button
                                        role="menuitem"
                                        type="button"
                                        className="profile-menu-item"
                                        onClick={() => {
                                            setProfileMenuOpen(false);
                                            setSettingsOpen(true);
                                        }}
                                    >
                                        <Icon name="settings" /> Settings
                                    </button>
                                    <span className="profile-menu-divider" role="separator" />
                                    <button
                                        role="menuitem"
                                        type="button"
                                        className="profile-menu-item is-danger"
                                        onClick={() => {
                                            setProfileMenuOpen(false);
                                            setLogoutConfirmation(true);
                                        }}
                                    >
                                        Log out
                                    </button>
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    <>
                        <Link to="/login" state={{ from: location.state?.from }}>Log in</Link>
                        <Link to="/register" className="signup-btn">Create account</Link>
                    </>
                )}
            </div>

            {settingsOpen && <NotificationSettingsDialog onClose={closeSettings} />}
            <ConfirmDialog
                open={logoutConfirmation}
                title="Log out of SocialConnect?"
                message="You can log back in at any time with your account."
                confirmLabel="Log out"
                onCancel={() => setLogoutConfirmation(false)}
                onConfirm={logout}
            />
        </header>
    );
}

export default Navbar;
