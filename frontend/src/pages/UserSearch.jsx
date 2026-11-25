import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useSearchParams } from "react-router-dom";
import api from "../api/axios";
import UserAvatar from "../components/UserAvatar";

function UserSearch() {
    const location = useLocation();
    const [, setSearchParams] = useSearchParams();
    const urlQuery = new URLSearchParams(location.search).get("query") || "";
    const [query, setQuery] = useState(urlQuery);
    const [lastUrlQuery, setLastUrlQuery] = useState(urlQuery);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(Boolean(urlQuery.trim()));
    const [error, setError] = useState("");
    const [resultQuery, setResultQuery] = useState("");
    const [busyUsers, setBusyUsers] = useState([]);
    const [busyFriends, setBusyFriends] = useState([]);
    const lastFetchedQueryRef = useRef("");
    const normalizedQuery = query.trim();

    if (urlQuery !== lastUrlQuery) {
        setLastUrlQuery(urlQuery);
        setQuery(urlQuery);
        setUsers([]);
        setResultQuery("");
        setError("");
        setLoading(Boolean(urlQuery.trim()));
    }

    useEffect(() => {
        if (!normalizedQuery) {
            lastFetchedQueryRef.current = "";
            return undefined;
        }

        if (lastFetchedQueryRef.current === normalizedQuery) return undefined;

        const controller = new AbortController();

        const timeout = window.setTimeout(async () => {
            lastFetchedQueryRef.current = normalizedQuery;
            setLoading(true);
            setError("");
            setUsers([]);
            setResultQuery("");
            try {
                const response = await api.get(
                    `users/search/?search=${encodeURIComponent(normalizedQuery)}`,
                    { signal: controller.signal }
                );
                const data = response.data;
                setUsers(Array.isArray(data) ? data : data.results || []);
                setResultQuery(normalizedQuery);
            } catch (requestError) {
                if (requestError.code !== "ERR_CANCELED") {
                    lastFetchedQueryRef.current = "";
                    setError("Unable to search people right now. Please try again.");
                }
            } finally {
                if (!controller.signal.aborted) setLoading(false);
            }
        }, 300);

        return () => {
            window.clearTimeout(timeout);
            controller.abort();
        };
    }, [normalizedQuery]);

    const handleSubmit = (event) => {
        event.preventDefault();
        const search = query.trim();
        setSearchParams(search ? { query: search } : {});
    };

    const toggleFollow = async (user) => {
        if (busyUsers.includes(user.id)) return;
        setBusyUsers((current) => [...current, user.id]);
        setError("");
        try {
            if (user.is_following) {
                await api.delete(`social/users/${user.id}/follow/`);
            } else {
                await api.post(`social/users/${user.id}/follow/`);
            }
            setUsers((current) =>
                current.map((item) =>
                    item.id === user.id
                        ? { ...item, is_following: !user.is_following }
                        : item
                )
            );
        } catch {
            setError(`Unable to ${user.is_following ? "unfollow" : "follow"} @${user.username}. Please try again.`);
        } finally {
            setBusyUsers((current) => current.filter((id) => id !== user.id));
        }
    };

    const updateFriendship = async (user) => {
        if (busyFriends.includes(user.id)) return;
        const status = user.friendship_status || "none";
        const action = {
            none: "send",
            outgoing_pending: "cancel",
            incoming_pending: "accept",
            friends: "unfriend",
        }[status];
        if (!action) return;

        setBusyFriends((current) => [...current, user.id]);
        setError("");
        try {
            let requestId = user.friend_request_id;
            if (action === "send") {
                const response = await api.post(`social/users/${user.id}/friend-request/`);
                requestId = response.data.id;
            } else if (action === "cancel") {
                await api.delete(`social/friend-requests/${requestId}/`);
            } else if (action === "accept") {
                await api.post(`social/friend-requests/${requestId}/accept/`);
            } else {
                await api.delete(`social/friends/${user.id}/`);
            }

            const nextStatus = {
                send: "outgoing_pending",
                cancel: "none",
                accept: "friends",
                unfriend: "none",
            }[action];
            setUsers((current) =>
                current.map((item) =>
                    item.id === user.id
                        ? {
                            ...item,
                            friendship_status: nextStatus,
                            friend_request_id: nextStatus.endsWith("pending") ? requestId : null,
                        }
                        : item
                )
            );
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                `Unable to update your friendship with @${user.username}.`,
            );
        } finally {
            setBusyFriends((current) => current.filter((id) => id !== user.id));
        }
    };

    const statusText = loading
        ? "Searching..."
        : resultQuery
            ? `${users.length} ${users.length === 1 ? "person" : "people"} found`
            : "";

    return (
        <section className="search-page">
            <header className="page-heading">
                <div>
                    <p className="page-eyebrow">GROW YOUR COMMUNITY</p>
                    <h1>Discover people</h1>
                    <p>Find members by their name or username.</p>
                </div>
            </header>

            <form className="search-form" role="search" onSubmit={handleSubmit}>
                <label className="sr-only" htmlFor="people-search">Search people</label>
                <input
                    id="people-search"
                    type="search"
                    placeholder="Search by name or username"
                    value={query}
                    onChange={(event) => {
                        const nextQuery = event.target.value;
                        setQuery(nextQuery);
                        if (nextQuery.trim() !== normalizedQuery) {
                            setUsers([]);
                            setResultQuery("");
                            setError("");
                            setLoading(Boolean(nextQuery.trim()));
                        }
                    }}
                    autoComplete="off"
                />
                <button className="button-primary" type="submit">Search</button>
            </form>

            {error && <p className="form-error" role="alert">{error}</p>}
            <p className="sr-only" role="status">{statusText}</p>

            <div className="search-results">
                {loading ? (
                    <>
                        <div className="user-result-skeleton" />
                        <div className="user-result-skeleton" />
                        <div className="user-result-skeleton" />
                    </>
                ) : users.length ? (
                    users.map((user) => {
                        const profile = user.profile || {};
                        const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");
                        const displayName = fullName || user.username;
                        const avatar = profile.profile_picture;
                        const friendshipStatus = user.friendship_status || "none";
                        const friendshipLabels = {
                            none: `Add ${displayName} as a friend`,
                            outgoing_pending: `Cancel friend request to ${displayName}`,
                            incoming_pending: `Accept friend request from ${displayName}`,
                            friends: `Remove ${displayName} from your friends`,
                        };

                        return (
                            <article className="search-user-card" key={user.id}>
                                <div className="search-user-identity">
                                    <UserAvatar
                                        className="search-user-avatar"
                                        src={avatar}
                                        name={displayName}
                                    />
                                    <Link to={`/users/${user.id}`} className="search-user-copy">
                                        <strong>{displayName}</strong>
                                        <span>@{user.username}</span>
                                        {profile.bio && <small>{profile.bio}</small>}
                                    </Link>
                                </div>
                                <div className="search-user-actions">
                                    <button
                                        type="button"
                                        className={user.is_following ? "button-secondary follow-button is-following" : "button-primary follow-button"}
                                        onClick={() => toggleFollow(user)}
                                        disabled={busyUsers.includes(user.id)}
                                        aria-label={`${user.is_following ? "Unfollow" : "Follow"} @${user.username}`}
                                    >
                                        {busyUsers.includes(user.id)
                                            ? "Please wait..."
                                            : user.is_following ? "Following" : "Follow"}
                                    </button>
                                    <button
                                        type="button"
                                        className="button-secondary follow-button"
                                        onClick={() => updateFriendship(user)}
                                        disabled={busyFriends.includes(user.id)}
                                        aria-label={friendshipLabels[friendshipStatus] || `Manage friendship with ${displayName}`}
                                    >
                                        {busyFriends.includes(user.id)
                                            ? "Please wait..."
                                            : friendshipStatus === "friends"
                                                ? "Friends · Unfriend"
                                                : friendshipStatus === "incoming_pending"
                                                    ? "Accept request"
                                                    : friendshipStatus === "outgoing_pending"
                                                        ? "Request sent · Cancel"
                                                        : "Add friend"}
                                    </button>
                                </div>
                            </article>
                        );
                    })
                ) : query.trim() ? (
                    <div className="empty-state">
                        <h2>No people found</h2>
                        <p>Try a different name or username.</p>
                    </div>
                ) : (
                    <div className="empty-state">
                        <span className="empty-state-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></svg>
                        </span>
                        <h2>Search SocialConnect</h2>
                        <p>Type a name or username to find people in the community.</p>
                    </div>
                )}
            </div>
        </section>
    );
}

export default UserSearch;
