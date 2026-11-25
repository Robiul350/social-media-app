import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";
import UserAvatar from "../components/UserAvatar";

const tabs = [
    { value: "incoming", label: "Received" },
    { value: "outgoing", label: "Sent" },
];

function FriendRequests() {
    const [direction, setDirection] = useState("incoming");
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [busyRequests, setBusyRequests] = useState({});
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [receivedCount, setReceivedCount] = useState(0);
    const tabRefs = useRef([]);

    useEffect(() => {
        const controller = new AbortController();
        api.get(`social/friend-requests/?direction=${direction}`, {
            signal: controller.signal,
        })
            .then((response) => {
                const items = Array.isArray(response.data) ? response.data : [];
                setRequests(items);
                if (direction === "incoming") setReceivedCount(items.length);
                setError("");
            })
            .catch((requestError) => {
                if (requestError.code !== "ERR_CANCELED") {
                    setError("Unable to load friend requests. Please try again.");
                }
            })
            .finally(() => {
                if (!controller.signal.aborted) setLoading(false);
            });
        return () => controller.abort();
    }, [direction]);

    const selectTab = (value) => {
        if (value === direction) return;
        setLoading(true);
        setError("");
        setDirection(value);
        setNotice("");
    };

    const handleTabKeyDown = (event) => {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        const currentIndex = tabs.findIndex((tab) => tab.value === direction);
        const step = event.key === "ArrowRight" ? 1 : -1;
        const nextIndex = (currentIndex + step + tabs.length) % tabs.length;
        selectTab(tabs[nextIndex].value);
        tabRefs.current[nextIndex]?.focus();
    };

    const handleAction = async (friendRequest, action) => {
        if (busyRequests[friendRequest.id]) return;
        setBusyRequests((current) => ({ ...current, [friendRequest.id]: action }));
        setError("");
        setNotice("");
        try {
            const requestUrl = `social/friend-requests/${friendRequest.id}/`;
            if (action === "accept" || action === "reject") {
                await api.post(`${requestUrl}${action}/`);
            } else {
                await api.delete(requestUrl);
            }

            setRequests((current) =>
                current.filter((item) => item.id !== friendRequest.id)
            );
            if (direction === "incoming") {
                setReceivedCount((count) => Math.max(0, count - 1));
            }
            setNotice(
                action === "accept"
                    ? "Friend request accepted."
                    : action === "reject"
                        ? "Friend request rejected."
                        : "Friend request cancelled.",
            );
        } catch (actionError) {
            setError(
                actionError.response?.data?.detail ||
                "Unable to update this friend request. Please try again.",
            );
        } finally {
            setBusyRequests((current) => {
                const next = { ...current };
                delete next[friendRequest.id];
                return next;
            });
        }
    };

    const listStatus = loading
        ? "Loading friend requests..."
        : `${requests.length} ${direction === "incoming" ? "received" : "sent"} friend request${requests.length === 1 ? "" : "s"}`;

    return (
        <main className="friend-requests-page">
            <header className="page-heading">
                <div>
                    <p className="page-eyebrow">YOUR CONNECTIONS</p>
                    <h1>Friend requests</h1>
                    <p>Manage the people you want to connect with.</p>
                </div>
                <div className="friend-request-page-actions">
                    <Link className="button-secondary" to="/connections/friends">View connections</Link>
                    <Link className="button-secondary" to="/search">Discover people</Link>
                </div>
            </header>

            <div
                className="friend-request-tabs"
                role="tablist"
                aria-label="Friend request type"
                onKeyDown={handleTabKeyDown}
            >
                {tabs.map((tab, index) => {
                    const isActive = direction === tab.value;
                    const count = tab.value === "incoming" ? receivedCount : 0;
                    return (
                        <button
                            key={tab.value}
                            ref={(node) => { tabRefs.current[index] = node; }}
                            id={`friend-request-tab-${tab.value}`}
                            type="button"
                            role="tab"
                            aria-selected={isActive}
                            aria-controls="friend-request-panel"
                            aria-label={count ? `${tab.label}, ${count} pending` : tab.label}
                            tabIndex={isActive ? 0 : -1}
                            className={isActive ? "friend-request-tab is-active" : "friend-request-tab"}
                            onClick={() => selectTab(tab.value)}
                        >
                            {tab.label}
                            {count > 0 && <span className="unread-count" aria-hidden="true">{count}</span>}
                        </button>
                    );
                })}
            </div>

            {error && <p className="form-error" role="alert">{error}</p>}
            {notice && <p className="form-success" role="status">{notice}</p>}

            <section
                id="friend-request-panel"
                role="tabpanel"
                aria-labelledby={`friend-request-tab-${direction}`}
                className="friend-request-list"
                tabIndex={0}
            >
                <p className="sr-only" role="status">{listStatus}</p>
                {loading ? (
                    <p>Loading friend requests...</p>
                ) : requests.length ? (
                    requests.map((friendRequest) => {
                        const person = (direction === "incoming"
                            ? friendRequest.sender
                            : friendRequest.receiver) || {};
                        const fullName = [person.first_name, person.last_name]
                            .filter(Boolean)
                            .join(" ");
                        const displayName = fullName || person.username || "A member";
                        const busyAction = busyRequests[friendRequest.id];
                        const identity = (
                            <>
                                <UserAvatar
                                    className="friend-request-avatar"
                                    src={person.profile_picture}
                                    name={displayName}
                                    interactive={false}
                                />
                                <span className="friend-request-person-copy">
                                    <strong>{displayName}</strong>
                                    <span>{person.username ? `@${person.username}` : "Profile unavailable"}</span>
                                </span>
                            </>
                        );

                        return (
                            <article className="friend-request-card" key={friendRequest.id}>
                                {person.id ? (
                                    <Link
                                        className="friend-request-person"
                                        to={`/users/${person.id}`}
                                        aria-label={`View ${displayName}'s profile`}
                                    >
                                        {identity}
                                    </Link>
                                ) : (
                                    <span className="friend-request-person">{identity}</span>
                                )}

                                {direction === "incoming" ? (
                                    <div className="friend-request-actions">
                                        <button
                                            className="button-primary"
                                            type="button"
                                            onClick={() => handleAction(friendRequest, "accept")}
                                            disabled={Boolean(busyAction)}
                                            aria-label={`Accept friend request from ${displayName}`}
                                        >
                                            {busyAction === "accept" ? "Accepting..." : "Accept"}
                                        </button>
                                        <button
                                            className="button-secondary"
                                            type="button"
                                            onClick={() => handleAction(friendRequest, "reject")}
                                            disabled={Boolean(busyAction)}
                                            aria-label={`Reject friend request from ${displayName}`}
                                        >
                                            {busyAction === "reject" ? "Rejecting..." : "Reject"}
                                        </button>
                                    </div>
                                ) : (
                                    <button
                                        className="button-secondary"
                                        type="button"
                                        onClick={() => handleAction(friendRequest, "cancel")}
                                        disabled={Boolean(busyAction)}
                                        aria-label={`Cancel friend request to ${displayName}`}
                                    >
                                        {busyAction ? "Cancelling..." : "Cancel request"}
                                    </button>
                                )}
                            </article>
                        );
                    })
                ) : (
                    <div className="empty-state">
                        <span className="empty-state-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0M18 8v6m-3-3h6" /></svg>
                        </span>
                        <h2>{direction === "incoming" ? "No requests received" : "No pending requests sent"}</h2>
                        <p>
                            {direction === "incoming"
                                ? "New friend requests will appear here."
                                : "When you send a friend request, it will appear here."}
                        </p>
                    </div>
                )}
            </section>
        </main>
    );
}

export default FriendRequests;
