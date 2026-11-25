import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { API_ORIGIN } from "../api/axios";

function notificationMessage(type) {
    switch (type) {
        case "like":
            return "liked your post";
        case "comment":
            return "commented on your post";
        case "reply":
            return "replied to your comment";
        case "follow":
            return "started following you";
        case "friend_request":
            return "sent you a friend request";
        case "message":
            return "sent you a message";
        case "mention":
            return "mentioned you in a post";
        case "story_reaction":
            return "reacted to your story";
        default:
            return "sent you a notification";
    }
}

function NotificationIcon({ type }) {
    const shared = {
        fill: "none",
        stroke: "currentColor",
        strokeLinecap: "round",
        strokeLinejoin: "round",
        strokeWidth: 1.8,
        viewBox: "0 0 24 24",
        "aria-hidden": true,
    };

    switch (type) {
        case "like":
            return <svg {...shared}><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8l1.1 1.1L12 21l7.8-7.5 1.1-1.1a5.5 5.5 0 0 0-.1-7.8Z" /></svg>;
        case "comment":
            return <svg {...shared}><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 21l2.1-5.4A8.5 8.5 0 1 1 21 11.5Z" /></svg>;
        case "reply":
            return <svg {...shared}><path d="M9 10 5 14l4 4M5 14h8a6 6 0 0 1 6 6M15 4l4 4-4 4M19 8h-6a6 6 0 0 0-6 6" /></svg>;
        case "follow":
            return <svg {...shared}><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0M19 8v6m-3-3h6" /></svg>;
        case "friend_request":
            return <svg {...shared}><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20a6.5 6.5 0 0 1 13 0M18 8v6m-3-3h6" /></svg>;
        case "message":
            return <svg {...shared}><path d="M21 11.5a8.5 8.5 0 0 1-12.6 7.4L3 21l2.1-5.4A8.5 8.5 0 1 1 21 11.5Z" /><path d="M8 12h.01M12 12h.01M16 12h.01" /></svg>;
        case "mention":
            return <svg {...shared}><circle cx="12" cy="12" r="4" /><path d="M16 12v1.5a2.5 2.5 0 0 0 5 0V12a9 9 0 1 0-3.6 7.2" /></svg>;
        case "story_reaction":
            return <svg {...shared}><circle cx="12" cy="12" r="3" /><path d="M12 3v2m0 14v2M3 12h2m14 0h2M5.6 5.6 7 7m10 10 1.4 1.4m0-12.8L17 7M7 17l-1.4 1.4" /></svg>;
        default:
            return <svg {...shared}><circle cx="12" cy="12" r="8" /><path d="M12 11v5m0-8h.01" /></svg>;
    }
}

function notificationIconClass(type) {
    if (type === "friend_request") return "notification-friend-request";
    if (type === "story_reaction") return "notification-story-reaction";
    return `notification-${type || "other"}`;
}

function notificationTarget(notification) {
    if (notification.notification_type === "friend_request") {
        return "/friend-requests";
    }
    if (notification.notification_type === "message" && notification.sender) {
        return `/messages/${notification.sender}`;
    }
    if (notification.post) return `/posts/${notification.post}`;
    if (notification.sender) return `/users/${notification.sender}`;
    return "/";
}

function Notifications() {
    const navigate = useNavigate();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState(false);
    const [busyIds, setBusyIds] = useState([]);
    const [error, setError] = useState("");
    const [liveStatus, setLiveStatus] = useState("connecting");
    const [refreshKey, setRefreshKey] = useState(0);

    useEffect(() => {
        const controller = new AbortController();
        const load = async () => {
            try {
                const response = await api.get("notifications/", { signal: controller.signal });
                if (controller.signal.aborted) return;
                setNotifications(Array.isArray(response.data) ? response.data : response.data.results || []);
                setError("");
            } catch (requestError) {
                if (controller.signal.aborted || requestError.code === "ERR_CANCELED") return;
                setError("Unable to load notifications. Please try again.");
            } finally {
                if (!controller.signal.aborted) setLoading(false);
            }
        };
        load();
        return () => controller.abort();
    }, [refreshKey]);

    useEffect(() => {
        let active = true;
        let socket = null;
        let reconnectTimer = null;
        let reconnectAttempt = 0;
        let manuallyClosed = false;
        const socketOrigin = API_ORIGIN.replace(/^http/, "ws");

        const connect = () => {
            const token = localStorage.getItem("access");
            if (!active || manuallyClosed || !token) {
                if (active && !token) setLiveStatus("offline");
                return;
            }

            socket = new WebSocket(
                `${socketOrigin}/ws/notifications/?token=${encodeURIComponent(token)}`
            );
            socket.onopen = () => {
                reconnectAttempt = 0;
                if (active) setLiveStatus("connected");
            };
            socket.onmessage = (event) => {
                if (!active) return;
                try {
                    const message = JSON.parse(event.data);
                    if (message.type !== "notification" || !message.notification) return;
                    setNotifications((current) => [
                        message.notification,
                        ...current.filter((item) => item.id !== message.notification.id),
                    ]);
                    window.dispatchEvent(new Event("socialconnect:refresh-counts"));
                } catch {
                    setError("Received an invalid real-time notification.");
                }
            };
            socket.onerror = () => {
                if (active) setLiveStatus("reconnecting");
            };
            socket.onclose = () => {
                if (!active || manuallyClosed) return;
                setLiveStatus("reconnecting");
                const delay = Math.min(1000 * (2 ** reconnectAttempt), 30000);
                reconnectAttempt += 1;
                reconnectTimer = window.setTimeout(async () => {
                    try {
                        await api.get("notifications/unread-count/");
                    } catch {
                        if (!localStorage.getItem("access")) {
                            if (active) setLiveStatus("offline");
                            return;
                        }
                    }
                    if (active && localStorage.getItem("access")) connect();
                    else if (active) setLiveStatus("offline");
                }, delay);
            };
        };

        connect();
        return () => {
            active = false;
            manuallyClosed = true;
            window.clearTimeout(reconnectTimer);
            socket?.close();
        };
    }, []);

    const markNotificationRead = async (notification) => {
        setError("");
        try {
            await api.patch(`notifications/${notification.id}/read/`);
            setNotifications((current) =>
                current.map((item) => item.id === notification.id ? { ...item, is_read: true } : item)
            );
            window.dispatchEvent(new Event("socialconnect:refresh-counts"));
            return true;
        } catch {
            setError("Unable to mark this notification as read. Please try again.");
            return false;
        }
    };

    const markAllRead = async () => {
        if (busy) return;
        setBusy(true);
        setError("");
        try {
            await api.post("notifications/read-all/");
            setNotifications((current) => current.map((item) => ({ ...item, is_read: true })));
            window.dispatchEvent(new Event("socialconnect:refresh-counts"));
        } catch {
            setError("Unable to mark all notifications as read.");
        } finally {
            setBusy(false);
        }
    };

    const markOneRead = async (notification) => {
        if (busyIds.includes(notification.id) || notification.is_read) return;
        setBusyIds((current) => [...current, notification.id]);
        await markNotificationRead(notification);
        setBusyIds((current) => current.filter((id) => id !== notification.id));
    };

    const openNotification = async (event, notification) => {
        if (notification.is_read || busyIds.includes(notification.id)) return;
        event.preventDefault();
        if (await markNotificationRead(notification)) {
            navigate(notificationTarget(notification));
        }
    };

    const unreadCount = notifications.filter((notification) => !notification.is_read).length;
    const listStatus = loading
        ? "Loading notifications..."
        : unreadCount
            ? `${unreadCount} unread notification${unreadCount === 1 ? "" : "s"}`
            : "No unread notifications";

    return (
        <main className="notifications-page">
            <header className="notifications-header">
                <div>
                    <p className="page-eyebrow">YOUR UPDATES</p>
                    <h1>Notifications</h1>
                    <p>{unreadCount ? `${unreadCount} unread notification${unreadCount === 1 ? "" : "s"}` : "You're all caught up."}</p>
                    <p className="notification-live-status">
                        {liveStatus === "connected"
                            ? "Live updates connected"
                            : liveStatus === "offline"
                                ? "Live updates unavailable"
                                : "Reconnecting to live updates..."}
                    </p>
                </div>
                <div className="notification-header-actions">
                    <button
                        type="button"
                        className="button-secondary"
                        onClick={() => {
                            setLoading(true);
                            setRefreshKey((key) => key + 1);
                        }}
                        disabled={loading}
                    >
                        Refresh
                    </button>
                    <button
                        type="button"
                        className="button-primary"
                        onClick={markAllRead}
                        disabled={!unreadCount || busy}
                    >
                        {busy ? "Updating..." : "Mark all read"}
                    </button>
                </div>
            </header>

            {error && <p className="form-error" role="alert">{error}</p>}

            <section className="notification-list" aria-label="Recent notifications">
                <p className="sr-only" role="status">{listStatus}</p>
                {loading ? (
                    <div className="notification-loading">Loading notifications...</div>
                ) : notifications.length ? (
                    notifications.map((notification) => (
                        <article
                            key={notification.id}
                            className={notification.is_read ? "notification-item" : "notification-item unread"}
                        >
                            <span className={`notification-type-icon ${notificationIconClass(notification.notification_type)}`} aria-hidden="true">
                                <NotificationIcon type={notification.notification_type} />
                            </span>
                            <Link
                                to={notificationTarget(notification)}
                                className="notification-copy"
                                style={{ color: "inherit", textDecoration: "none" }}
                                onClick={(event) => openNotification(event, notification)}
                            >
                                <span>
                                    <strong>{notification.sender_username || "A member"}</strong>
                                    {" "}{notificationMessage(notification.notification_type)}
                                </span>
                                <small>
                                    {notification.created_at
                                        ? new Date(notification.created_at).toLocaleString()
                                        : ""}
                                </small>
                            </Link>
                            {!notification.is_read && (
                                <>
                                    <button
                                        type="button"
                                        className="button-secondary notification-mark-read"
                                        onClick={() => markOneRead(notification)}
                                        disabled={busyIds.includes(notification.id)}
                                        aria-label={`Mark notification from ${notification.sender_username || "a member"} as read`}
                                    >
                                        {busyIds.includes(notification.id) ? "Saving..." : "Mark read"}
                                    </button>
                                    <span className="notification-unread-dot" aria-label="Unread" />
                                </>
                            )}
                        </article>
                    ))
                ) : (
                    <div className="empty-state">
                        <span className="empty-state-icon" aria-hidden="true">
                            <svg viewBox="0 0 24 24"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></svg>
                        </span>
                        <h2>No notifications yet</h2>
                        <p>Likes, comments, mentions, story reactions, follows, friend requests, and messages will show up here.</p>
                    </div>
                )}
            </section>
        </main>
    );
}

export default Notifications;
