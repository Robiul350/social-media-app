import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import Navbar from "./navbar";
import api from "../api/axios";
import { getProfileSnapshot, subscribeProfile } from "../api/profileStore";
import useFocusTrap from "../hooks/useFocusTrap";
import Icon from "./Icon";
import NotificationSettingsDialog from "./NotificationSettingsDialog";
import UserAvatar from "./UserAvatar";

const primaryNavigation = [
    { to: "/", label: "Home", icon: "home", end: true },
    { to: "/search", label: "Explore", icon: "search" },
    { to: "/connections/friends", label: "Friends", icon: "friends" },
    { to: "/messages", label: "Messages", icon: "messages" },
    { to: "/notifications", label: "Notifications", icon: "notifications" },
];

const moreNavigation = [
    { to: "/friend-requests", label: "Friend requests", icon: "friends" },
    { to: "/bookmarks", label: "Saved posts", icon: "bookmarks" },
    { to: "/profile", label: "My profile", icon: "profile" },
];

const mobileNavigationLabels = {
    "/": "Home",
    "/search": "People",
    "/connections/friends": "Friends",
    "/messages": "Chat",
    "/notifications": "Alerts",
};

const mobileNavigation = primaryNavigation
    .filter((item) => Object.hasOwn(mobileNavigationLabels, item.to))
    .map((item) => ({ ...item, mobileLabel: mobileNavigationLabels[item.to] }));

function NavigationLink({ item, mobile = false, drawer = false, onNavigate }) {
    const location = useLocation();
    const profileActive = item.icon === "profile" && location.pathname.startsWith("/users/");
    const className = mobile ? "mobile-nav-link" : drawer ? "drawer-nav-link" : "app-nav-link";

    return (
        <NavLink
            to={item.to}
            end={item.end}
            className={({ isActive }) => `${className}${isActive || profileActive ? " is-active" : ""}`}
            aria-label={mobile || drawer ? item.label : undefined}
            onClick={onNavigate}
        >
            <Icon name={item.icon} />
            <span>{mobile ? item.mobileLabel || item.label : item.label}</span>
        </NavLink>
    );
}

function personName(person) {
    if (!person) return "Member";
    return [person.first_name, person.last_name].filter(Boolean).join(" ") || person.username || "Member";
}

function personAvatar(person) {
    return person?.profile_picture || person?.profile?.profile_picture || "";
}

function AppShell() {
    const location = useLocation();
    const profileState = useSyncExternalStore(subscribeProfile, getProfileSnapshot, getProfileSnapshot);
    const [settingsOpen, setSettingsOpen] = useState(false);
    const [seeMoreOpen, setSeeMoreOpen] = useState(false);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [suggestedUsers, setSuggestedUsers] = useState([]);
    const [friends, setFriends] = useState([]);
    const [requests, setRequests] = useState([]);
    const [railError, setRailError] = useState("");
    const [followingId, setFollowingId] = useState(null);
    const [busyRequestId, setBusyRequestId] = useState(null);
    const [mobileMoreOpen, setMobileMoreOpen] = useState(false);
    const mobileMoreRef = useRef(null);
    const mobileMoreButtonRef = useRef(null);
    const drawerCloseRef = useRef(null);
    const drawerRef = useRef(null);

    useFocusTrap(drawerOpen, drawerRef, drawerCloseRef);

    const mobileMoreActive = ["/friend-requests", "/bookmarks", "/profile"].includes(location.pathname)
        || location.pathname.startsWith("/users/");

    useEffect(() => {
        if (location.pathname !== "/") return undefined;
        let active = true;
        Promise.allSettled([
            api.get("users/search/?suggested=true"),
            api.get("social/friends/"),
            api.get("social/friend-requests/?direction=incoming"),
        ]).then(([suggestionsResult, friendsResult, requestsResult]) => {
            if (!active) return;
            if (suggestionsResult.status === "fulfilled") {
                setSuggestedUsers(Array.isArray(suggestionsResult.value.data) ? suggestionsResult.value.data : []);
            }
            if (friendsResult.status === "fulfilled") {
                setFriends(Array.isArray(friendsResult.value.data) ? friendsResult.value.data : []);
            }
            if (requestsResult.status === "fulfilled") {
                setRequests(Array.isArray(requestsResult.value.data) ? requestsResult.value.data : []);
            }
            const failed = [suggestionsResult, friendsResult, requestsResult]
                .some((result) => result.status === "rejected");
            setRailError(failed ? "Some community updates are unavailable right now." : "");
        });
        return () => {
            active = false;
        };
    }, [location.pathname]);

    useEffect(() => {
        if (!mobileMoreOpen) return undefined;
        const handlePointerDown = (event) => {
            if (!mobileMoreRef.current?.contains(event.target)) setMobileMoreOpen(false);
        };
        const handleKeyDown = (event) => {
            if (event.key === "Escape") {
                setMobileMoreOpen(false);
                mobileMoreButtonRef.current?.focus();
            }
        };
        document.addEventListener("pointerdown", handlePointerDown);
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.removeEventListener("pointerdown", handlePointerDown);
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [mobileMoreOpen]);

    useEffect(() => {
        if (!drawerOpen) return undefined;
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        drawerCloseRef.current?.focus();
        const handleKeyDown = (event) => {
            if (event.key === "Escape") setDrawerOpen(false);
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.body.style.overflow = previousOverflow;
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [drawerOpen]);

    const followSuggestedUser = async (user) => {
        setFollowingId(user.id);
        setRailError("");
        try {
            await api.post(`social/users/${user.id}/follow/`);
            setSuggestedUsers((current) => current.filter((item) => item.id !== user.id));
        } catch {
            setRailError(`Unable to follow @${user.username}. Please try again.`);
        } finally {
            setFollowingId(null);
        }
    };

    const respondToRequest = async (request, action) => {
        setBusyRequestId(request.id);
        setRailError("");
        try {
            await api.post(`social/friend-requests/${request.id}/${action}/`);
            setRequests((current) => current.filter((item) => item.id !== request.id));
            if (action === "accept") {
                setFriends((current) => {
                    if (current.some((person) => person.id === request.sender?.id)) return current;
                    return [...current, request.sender].filter(Boolean);
                });
            }
            window.dispatchEvent(new Event("socialconnect:refresh-counts"));
        } catch {
            setRailError(`Unable to ${action} the request right now.`);
        } finally {
            setBusyRequestId(null);
        }
    };

    const openDrawer = useCallback(() => setDrawerOpen(true), []);
    const closeDrawer = useCallback(() => setDrawerOpen(false), []);
    const closeSettings = useCallback(() => setSettingsOpen(false), []);
    const openSettings = () => {
        setDrawerOpen(false);
        setSettingsOpen(true);
    };

    const profile = profileState.data;
    const displayName = personName({
        first_name: profile?.first_name,
        last_name: profile?.last_name,
        username: profile?.username || localStorage.getItem("username"),
    });
    const username = profile?.username || localStorage.getItem("username") || "member";

    const profileSummary = (variant = "") => (
        <div className={`sidebar-profile${variant ? ` ${variant}` : ""}`}>
            <UserAvatar
                className="sidebar-profile-avatar"
                src={profile?.profile?.profile_picture}
                name={displayName}
            />
            <div className="sidebar-profile-meta">
                <strong>{displayName}</strong>
                <small>@{username}</small>
            </div>
            <Link to="/profile" className="sidebar-profile-link" aria-label="Open your profile">↗</Link>
        </div>
    );

    return (
        <div className="app-root">
            <Navbar onOpenDrawer={openDrawer} />
            <div className="app-shell">
                <aside className="app-sidebar" aria-label="Primary navigation">
                    {profileSummary()}

                    <nav className="app-sidebar-nav">
                        <p className="sidebar-section-label">MENU</p>
                        {primaryNavigation.map((item) => (
                            <NavigationLink key={item.to} item={item} />
                        ))}
                    </nav>

                    <button
                        type="button"
                        className="sidebar-see-more"
                        onClick={() => setSeeMoreOpen((open) => !open)}
                        aria-expanded={seeMoreOpen}
                    >
                        <span>See more</span>
                        <Icon name="chevron" />
                    </button>

                    {seeMoreOpen && (
                        <nav className="app-sidebar-nav sidebar-more-nav">
                            {moreNavigation.map((item) => (
                                <NavigationLink key={item.to} item={item} />
                            ))}
                            <button type="button" className="app-nav-link" onClick={openSettings}>
                                <Icon name="settings" />
                                <span>Settings</span>
                            </button>
                        </nav>
                    )}
                </aside>

                <main className="app-main">
                    <Outlet />
                </main>

                <aside className="app-right-rail" aria-label="Community updates">
                    {location.pathname === "/" ? (
                        <>
                            <section className="rail-card">
                                <div className="rail-section-heading">
                                    <div>
                                        <span className="rail-eyebrow">PEOPLE YOU MAY KNOW</span>
                                        <h2>Grow your circle</h2>
                                    </div>
                                    <Link to="/search" className="rail-text-link">See all</Link>
                                </div>
                                {railError && <p className="rail-error" role="status">{railError}</p>}
                                {suggestedUsers.length ? (
                                    <div className="rail-suggested-users">
                                        {suggestedUsers.slice(0, 4).map((user) => {
                                            const name = personName(user);
                                            return (
                                                <div className="rail-suggested-user" key={user.id}>
                                                    <UserAvatar
                                                        className="rail-suggested-avatar"
                                                        src={personAvatar(user)}
                                                        name={name}
                                                    />
                                                    <Link to={`/users/${user.id}`} className="rail-suggested-person">
                                                        <span>
                                                            <strong>{name}</strong>
                                                            <small>@{user.username}</small>
                                                        </span>
                                                    </Link>
                                                    <button
                                                        type="button"
                                                        className="rail-follow-button"
                                                        onClick={() => followSuggestedUser(user)}
                                                        disabled={followingId === user.id}
                                                    >
                                                        {followingId === user.id ? "..." : "Follow"}
                                                    </button>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ) : !railError ? (
                                    <p className="rail-empty">You’re all caught up. Find more people to follow.</p>
                                ) : null}
                            </section>

                            {requests.length > 0 && (
                                <section className="rail-card">
                                    <div className="rail-section-heading">
                                        <div>
                                            <span className="rail-eyebrow">FRIEND REQUESTS</span>
                                            <h2>Waiting for you</h2>
                                        </div>
                                        <Link to="/friend-requests" className="rail-text-link">See all</Link>
                                    </div>
                                    <div className="rail-requests">
                                        {requests.slice(0, 3).map((request) => {
                                            const person = request.sender;
                                            const name = personName(person);
                                            const busy = busyRequestId === request.id;
                                            return (
                                                <div className="rail-request" key={request.id}>
                                                    <UserAvatar
                                                        className="rail-mini-avatar"
                                                        src={personAvatar(person)}
                                                        name={name}
                                                    />
                                                    <div className="rail-request-copy">
                                                        <Link to={`/users/${person?.id}`}><strong>{name}</strong></Link>
                                                        <small>@{person?.username || "member"}</small>
                                                    </div>
                                                    <div className="rail-request-actions">
                                                        <button
                                                            type="button"
                                                            className="rail-accept-button"
                                                            onClick={() => respondToRequest(request, "accept")}
                                                            disabled={busy}
                                                        >
                                                            Accept
                                                        </button>
                                                        <button
                                                            type="button"
                                                            className="rail-ignore-button"
                                                            onClick={() => respondToRequest(request, "reject")}
                                                            disabled={busy}
                                                        >
                                                            Ignore
                                                        </button>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </section>
                            )}

                            {friends.length > 0 && (
                                <section className="rail-card">
                                    <div className="rail-section-heading">
                                        <div>
                                            <span className="rail-eyebrow">YOUR FRIENDS</span>
                                            <h2>Stay close</h2>
                                        </div>
                                        <Link to="/connections/friends" className="rail-text-link">See all</Link>
                                    </div>
                                    <div className="rail-friends">
                                        {friends.slice(0, 4).map((friend) => {
                                            const name = personName(friend);
                                            return (
                                                <Link className="rail-friend" to={`/users/${friend.id}`} key={friend.id}>
                                                    <UserAvatar
                                                        className="rail-mini-avatar"
                                                        src={personAvatar(friend)}
                                                        name={name}
                                                        interactive={false}
                                                    />
                                                    <span>
                                                        <strong>{name}</strong>
                                                        <small>@{friend.username}</small>
                                                    </span>
                                                </Link>
                                            );
                                        })}
                                    </div>
                                </section>
                            )}
                        </>
                    ) : (
                        <section className="rail-card">
                            <span className="rail-eyebrow">DISCOVER</span>
                            <h2>Meet your community</h2>
                            <p>Find real people on SocialConnect and follow the conversations that matter to you.</p>
                            <Link to="/search" className="rail-action">Find people</Link>
                        </section>
                    )}

                    <section className="rail-card rail-card-soft">
                        <span className="rail-eyebrow">YOUR SPACE</span>
                        <h2>Pick up where you left off</h2>
                        <div className="rail-link-list">
                            <Link to="/bookmarks"><Icon name="bookmarks" /> Saved posts</Link>
                            <Link to="/notifications"><Icon name="notifications" /> Notifications</Link>
                            <Link to="/profile"><Icon name="profile" /> My profile</Link>
                        </div>
                    </section>
                    <p className="rail-footer">SocialConnect · A place to connect</p>
                </aside>
            </div>

            {drawerOpen && (
                <div className="mobile-drawer-backdrop" onMouseDown={(event) => {
                    if (event.target === event.currentTarget) closeDrawer();
                }}>
                    <aside ref={drawerRef} className="mobile-drawer" role="dialog" aria-modal="true" aria-label="Navigation menu">
                        <header className="drawer-header">
                            <Link to="/" className="brand" onClick={closeDrawer}>
                                <span className="brand-mark" aria-hidden="true">S</span>
                                <span className="brand-name">Social<span>Connect</span></span>
                            </Link>
                            <button
                                ref={drawerCloseRef}
                                type="button"
                                className="drawer-close"
                                onClick={closeDrawer}
                                aria-label="Close navigation menu"
                            >
                                ×
                            </button>
                        </header>
                        {profileSummary("drawer-profile")}
                        <nav className="drawer-nav" aria-label="Mobile primary navigation">
                            {[...primaryNavigation, ...moreNavigation].map((item) => (
                                <NavigationLink key={item.to} item={item} drawer onNavigate={closeDrawer} />
                            ))}
                        </nav>
                        <button type="button" className="drawer-nav-link" onClick={openSettings}>
                            <Icon name="settings" />
                            <span>Settings</span>
                        </button>
                    </aside>
                </div>
            )}

            <nav className="mobile-bottom-nav" aria-label="Mobile navigation">
                {mobileNavigation.map((item) => (
                    <NavigationLink key={item.to} item={item} mobile onNavigate={() => setMobileMoreOpen(false)} />
                ))}
                <div className="mobile-more-wrap" ref={mobileMoreRef}>
                    <button
                        ref={mobileMoreButtonRef}
                        type="button"
                        className={`mobile-nav-link mobile-more-trigger${mobileMoreOpen || mobileMoreActive ? " is-active" : ""}`}
                        aria-label="More navigation"
                        aria-haspopup="true"
                        aria-expanded={mobileMoreOpen}
                        aria-controls="mobile-more-menu"
                        onClick={() => setMobileMoreOpen((open) => !open)}
                    >
                        <Icon name="more" />
                        <span>More</span>
                    </button>
                    {mobileMoreOpen && (
                        <div className="mobile-more-menu" id="mobile-more-menu">
                            {moreNavigation.map((item) => (
                                <NavigationLink key={item.to} item={item} mobile onNavigate={() => setMobileMoreOpen(false)} />
                            ))}
                            <button type="button" className="mobile-nav-link" onClick={() => {
                                setMobileMoreOpen(false);
                                setSettingsOpen(true);
                            }}>
                                <Icon name="settings" />
                                <span>Settings</span>
                            </button>
                        </div>
                    )}
                </div>
            </nav>

            {settingsOpen && <NotificationSettingsDialog onClose={closeSettings} />}
        </div>
    );
}

export default AppShell;
