import { Fragment, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { API_ORIGIN, getMediaUrl } from "../api/axios";
import UserAvatar from "../components/UserAvatar";

function responseItems(data) {
    return Array.isArray(data) ? data : data?.results || [];
}

function mergeMessages(current, incoming) {
    const messages = new Map();
    [...current, ...incoming].forEach((message) => {
        const key = message.id ?? `${message.sender_id || message.sender}-${message.created_at}-${message.content || message.message}`;
        messages.set(key, message);
    });
    return [...messages.values()].sort(
        (left, right) => new Date(left.created_at || 0) - new Date(right.created_at || 0)
    );
}

function isImageAttachment(source) {
    return /\.(png|jpe?g|gif|webp|bmp|svg)(\?|$)/i.test(source || "");
}

function messageDate(message) {
    if (!message.created_at) return null;
    const date = new Date(message.created_at);
    return Number.isNaN(date.getTime()) ? null : date;
}

function messageDayKey(message) {
    const date = messageDate(message);
    return date
        ? `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
        : "unknown";
}

function messageDayLabel(message) {
    const date = messageDate(message);
    if (!date) return "Earlier";

    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    const isSameDay = (left, right) =>
        left.getFullYear() === right.getFullYear()
        && left.getMonth() === right.getMonth()
        && left.getDate() === right.getDate();

    if (isSameDay(date, today)) return "Today";
    if (isSameDay(date, yesterday)) return "Yesterday";
    return date.toLocaleDateString([], {
        month: "long",
        day: "numeric",
        ...(date.getFullYear() === today.getFullYear() ? {} : { year: "numeric" }),
    });
}

function Messages() {
    const { userId } = useParams();
    const currentUserId = Number(localStorage.getItem("user_id"));
    const [conversations, setConversations] = useState([]);
    const [messages, setMessages] = useState([]);
    const [text, setText] = useState("");
    const [attachment, setAttachment] = useState(null);
    const [error, setError] = useState("");
    const [loadingConversations, setLoadingConversations] = useState(true);
    const [loadingMessages, setLoadingMessages] = useState(Boolean(userId));
    const [sending, setSending] = useState(false);
    const [activeUser, setActiveUser] = useState(null);
    const [socketStatus, setSocketStatus] = useState(
        localStorage.getItem("access") ? "connecting" : "offline",
    );
    const [peerOnline, setPeerOnline] = useState(false);
    const [peerTyping, setPeerTyping] = useState(false);
    const [announcement, setAnnouncement] = useState({ userId: null, text: "" });
    const [conversationQuery, setConversationQuery] = useState("");
    const socketRef = useRef(null);
    const attachmentInputRef = useRef(null);
    const endOfMessagesRef = useRef(null);
    const reconnectTimerRef = useRef(null);
    const typingTimerRef = useRef(null);

    useEffect(() => {
        let active = true;
        api.get("chat/conversations/")
            .then((response) => {
                if (active) setConversations(responseItems(response.data));
            })
            .catch(() => {
                if (active) setError("Unable to load conversations. Please try again.");
            })
            .finally(() => {
                if (active) setLoadingConversations(false);
            });
        return () => {
            active = false;
        };
    }, []);

    useEffect(() => {
        if (!userId) return undefined;
        let active = true;
        api.get(`users/${userId}/`)
            .then((response) => {
                if (active) setActiveUser(response.data);
            })
            .catch(() => {
                if (active) setError("Unable to load this user's profile.");
            });
        return () => {
            active = false;
        };
    }, [userId]);

    useEffect(() => {
        if (!userId) return undefined;
        let active = true;
        const controller = new AbortController();
        const socketOrigin = API_ORIGIN.replace(/^http/, "ws");
        let reconnectAttempt = 0;
        let manuallyClosed = false;

        api.get(`chat/conversations/${userId}/`, { signal: controller.signal })
            .then((response) => {
                if (active) setMessages((current) => mergeMessages(current, responseItems(response.data)));
            })
            .catch((requestError) => {
                if (active && requestError.code !== "ERR_CANCELED") {
                    setError("Unable to load this conversation.");
                }
            })
            .finally(() => {
                if (active) setLoadingMessages(false);
            });

        api.post(`chat/conversations/${userId}/read/`)
            .then(() => {
                if (active) {
                    window.dispatchEvent(new Event("socialconnect:refresh-counts"));
                    setConversations((current) =>
                        current.map((conversation) =>
                            String(conversation.id) === String(userId)
                                ? { ...conversation, unread_count: 0 }
                                : conversation
                        )
                    );
                }
            })
            .catch(() => {
                if (active) setError("Unable to update the conversation's read status.");
            });

        const refreshConversations = () => {
            api.get("chat/conversations/")
                .then((response) => {
                    if (active) setConversations(responseItems(response.data));
                })
                .catch(() => {
                    if (active) setError("Unable to refresh your conversation list.");
                });
        };

        const handleSocketMessage = (event) => {
            if (!active) return;
            try {
                const message = JSON.parse(event.data);
                if (message.error) {
                    setError(message.error);
                } else if (message.type === "typing") {
                    if (Number(message.user_id) !== currentUserId) {
                        setPeerTyping(Boolean(message.is_typing));
                    }
                } else if (message.type === "presence") {
                    if (Number(message.user_id) !== currentUserId) {
                        setPeerOnline(Boolean(message.is_online));
                    }
                } else if (message.type === "read_receipt") {
                    if (Number(message.reader_id) !== currentUserId) {
                        const readIds = new Set(message.message_ids || []);
                        setMessages((current) =>
                            current.map((item) =>
                                readIds.has(item.id) ? { ...item, is_read: true } : item
                            )
                        );
                    }
                } else if (message.type === "message_updated") {
                    setMessages((current) =>
                        current.map((item) =>
                            item.id === message.message_id
                                ? { ...item, content: message.content, edited_at: message.edited_at }
                                : item
                        )
                    );
                } else if (message.type === "message_deleted") {
                    setMessages((current) =>
                        current.filter((item) => item.id !== message.message_id)
                    );
                } else if (message.id) {
                    setMessages((current) => mergeMessages(current, [message]));
                    refreshConversations();
                    if (Number(message.sender_id) !== currentUserId) {
                        const content = message.content || message.message || "";
                        setAnnouncement({
                            userId: String(userId),
                            text: `New message from ${message.sender_username || "someone"}${content ? `: ${content}` : ""}`,
                        });
                        api.post(`chat/conversations/${userId}/read/`)
                            .then(() => {
                                if (active) {
                                    window.dispatchEvent(new Event("socialconnect:refresh-counts"));
                                    setConversations((current) =>
                                        current.map((conversation) =>
                                            String(conversation.id) === String(userId)
                                                ? { ...conversation, unread_count: 0 }
                                                : conversation
                                        )
                                    );
                                }
                            })
                            .catch(() => {
                                if (active) setError("Unable to update the conversation's read status.");
                            });
                    }
                }
            } catch {
                setError("Received an invalid real-time message.");
            }
        };

        const connectSocket = () => {
            const token = localStorage.getItem("access");
            if (!active || manuallyClosed || !token) {
                if (active && !token) setSocketStatus("offline");
                return;
            }
            const socket = new WebSocket(
                `${socketOrigin}/ws/chat/${userId}/?token=${encodeURIComponent(token)}`
            );
            socketRef.current = socket;
            socket.onopen = () => {
                reconnectAttempt = 0;
                if (active) {
                    setSocketStatus("connected");
                    api.get(`chat/conversations/${userId}/`)
                        .then((response) => {
                            if (active) setMessages((current) => mergeMessages(current, responseItems(response.data)));
                        })
                        .catch(() => {
                            if (active) setError("Unable to synchronize conversation messages.");
                        });
                    refreshConversations();
                }
            };
            socket.onmessage = handleSocketMessage;
            socket.onerror = () => {
                if (active) setSocketStatus("reconnecting");
            };
            socket.onclose = () => {
                if (!active || manuallyClosed) return;
                setSocketStatus("reconnecting");
                setPeerOnline(false);
                setPeerTyping(false);
                const delay = Math.min(1000 * (2 ** reconnectAttempt), 30000);
                reconnectAttempt += 1;
                reconnectTimerRef.current = window.setTimeout(async () => {
                    try {
                        await api.get(`chat/conversations/${userId}/`, {
                            signal: controller.signal,
                        });
                    } catch (requestError) {
                        if (
                            active &&
                            requestError.code !== "ERR_CANCELED"
                        ) {
                            setError("Unable to refresh your chat session.");
                        }
                    }
                    if (active && localStorage.getItem("access")) {
                        connectSocket();
                    } else if (active) {
                        setSocketStatus("offline");
                    }
                }, delay);
            };
        };

        if (localStorage.getItem("access")) {
            connectSocket();
        }

        return () => {
            active = false;
            manuallyClosed = true;
            controller.abort();
            window.clearTimeout(reconnectTimerRef.current);
            window.clearTimeout(typingTimerRef.current);
            if (socketRef.current) {
                socketRef.current.close();
                socketRef.current = null;
            }
        };
    }, [currentUserId, userId]);

    useEffect(() => {
        endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages]);

    const sendMessage = async (event) => {
        event.preventDefault();
        const content = text.trim();
        if (!content || !userId || sending) return;

        if (attachment && attachment.size > 25 * 1024 * 1024) {
            setError("Attachments must be 25 MB or smaller.");
            return;
        }
        if (attachment && !/^(image\/|video\/|audio\/|application\/pdf$|text\/plain$)/i.test(attachment.type)) {
            setError("Only images, videos, audio, PDF, and text files are allowed.");
            return;
        }

        setSending(true);
        setError("");
        if (socketRef.current?.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify({ type: "typing", is_typing: false }));
        }
        window.clearTimeout(typingTimerRef.current);
        setPeerTyping(false);
        try {
            if (attachment) {
                const payload = new FormData();
                payload.append("content", content);
                payload.append("attachment", attachment);
                const response = await api.post(`chat/conversations/${userId}/`, payload);
                setMessages((current) => mergeMessages(current, [response.data]));
            } else if (socketRef.current?.readyState === WebSocket.OPEN) {
                socketRef.current.send(JSON.stringify({ message: content }));
            } else {
                const response = await api.post(`chat/conversations/${userId}/`, { content });
                setMessages((current) => mergeMessages(current, [response.data]));
            }
            if (attachment || socketRef.current?.readyState !== WebSocket.OPEN) {
                api.get("chat/conversations/")
                    .then((conversationsResponse) => setConversations(responseItems(conversationsResponse.data)))
                    .catch(() => setError("Message sent, but the conversation list could not be refreshed."));
            }
            setText("");
            setAttachment(null);
            if (attachmentInputRef.current) attachmentInputRef.current.value = "";
        } catch (requestError) {
            setError(
                requestError.response?.data?.attachment?.[0] ||
                requestError.response?.data?.detail ||
                "Unable to send your message. Please try again.",
            );
        } finally {
            setSending(false);
        }
    };

    const handleTextChange = (event) => {
        const value = event.target.value;
        setText(value);
        if (socketRef.current?.readyState !== WebSocket.OPEN) return;

        socketRef.current.send(JSON.stringify({
            type: "typing",
            is_typing: Boolean(value.trim()),
        }));
        window.clearTimeout(typingTimerRef.current);
        if (value.trim()) {
            typingTimerRef.current = window.setTimeout(() => {
                if (socketRef.current?.readyState === WebSocket.OPEN) {
                    socketRef.current.send(JSON.stringify({
                        type: "typing",
                        is_typing: false,
                    }));
                }
            }, 1200);
        }
    };

    const activeConversation = conversations.find(
        (conversation) => String(conversation.id) === String(userId)
    );
    const activeProfile = activeUser?.id === Number(userId) ? activeUser : null;
    const activeName = [
        activeProfile?.first_name ?? activeConversation?.first_name,
        activeProfile?.last_name ?? activeConversation?.last_name,
    ].filter(Boolean).join(" ")
        || activeProfile?.username
        || activeConversation?.username
        || `user-${userId}`;
    const activePicture = activeProfile?.profile?.profile_picture
        || activeConversation?.profile_picture;
    const visibleConversations = conversations.filter((conversation) => {
        const searchText = `${conversation.username} ${conversation.first_name} ${conversation.last_name} ${conversation.last_message}`
            .toLowerCase();
        return searchText.includes(conversationQuery.trim().toLowerCase());
    });
    const incomingAnnouncement = announcement.userId === String(userId) ? announcement.text : "";
    const presenceLabel = peerOnline
        ? "Online"
        : socketStatus === "offline"
            ? "Live updates unavailable"
            : socketStatus === "reconnecting"
                ? "Reconnecting to live updates..."
                : socketStatus === "connected"
                    ? "Offline"
                    : "Connecting...";

    return (
        <main className={userId ? "messages-page has-active-chat" : "messages-page"}>
            <aside className="conversation-list">
                <header className="conversation-heading">
                    <div>
                        <p className="page-eyebrow">YOUR INBOX</p>
                        <h1>Messages</h1>
                    </div>
                    <Link to="/search" className="new-message-link" aria-label="Find someone to message">+</Link>
                </header>

                <label className="sr-only" htmlFor="conversation-search">Search conversations</label>
                <input
                    id="conversation-search"
                    className="conversation-search"
                    type="search"
                    value={conversationQuery}
                    onChange={(event) => setConversationQuery(event.target.value)}
                    placeholder="Search conversations"
                />

                {loadingConversations ? (
                    <div className="conversation-loading" role="status">Loading conversations...</div>
                ) : visibleConversations.length ? (
                    <nav aria-label="Conversations">
                        {visibleConversations.map((conversation) => {
                            const displayName = [conversation.first_name, conversation.last_name].filter(Boolean).join(" ")
                                || conversation.username;
                            return (
                                <div
                                    key={conversation.id}
                                    className={String(userId) === String(conversation.id) ? "conversation-entry is-active" : "conversation-entry"}
                                >
                                    <span className="conversation-avatar-wrap">
                                        <UserAvatar
                                            className="conversation-avatar"
                                            src={conversation.profile_picture}
                                            name={displayName}
                                        />
                                        {String(userId) === String(conversation.id) && peerOnline && (
                                            <span className="conversation-online-dot" aria-label="Online" />
                                        )}
                                    </span>
                                    <Link
                                        to={`/messages/${conversation.id}`}
                                        className="conversation-link"
                                        aria-current={String(userId) === String(conversation.id) ? "page" : undefined}
                                    >
                                        <span className="conversation-copy">
                                            <strong>{displayName}</strong>
                                            <small>{conversation.last_message || "Start a conversation"}</small>
                                        </span>
                                        {conversation.unread_count > 0 && (
                                            <span className="unread-count" aria-label={`${conversation.unread_count} unread messages`}>
                                                {conversation.unread_count}
                                            </span>
                                        )}
                                    </Link>
                                </div>
                            );
                        })}
                    </nav>
                ) : (
                    <div className="chat-list-empty">
                        <p>{conversations.length ? "No conversations match your search." : "No conversations yet."}</p>
                        <Link to="/search">Find someone to message</Link>
                    </div>
                )}
            </aside>

            {userId ? (
                <section className="chat-panel" aria-label="Conversation">
                    <header className="chat-heading">
                        <Link to="/messages" className="chat-back-link" aria-label="Back to conversations">‹</Link>
                        <UserAvatar
                            className="conversation-avatar"
                            src={activePicture}
                            name={activeName}
                        />
                        <div>
                            <strong>{activeName}</strong>
                            <small className="chat-presence">
                                <span className={peerOnline ? "chat-presence-dot is-online" : "chat-presence-dot"} />
                                {presenceLabel}
                            </small>
                        </div>
                    </header>

                    {error && <p className="form-error chat-error" role="alert">{error}</p>}

                    <p className="sr-only message-sr-status" role="status">{incomingAnnouncement}</p>

                    <div className="chat-history">
                        {loadingMessages ? (
                            <p className="chat-loading" role="status">Loading messages...</p>
                        ) : messages.length ? (
                            messages.map((message, index) => {
                                const isOwnMessage = Number(message.sender ?? message.sender_id) === currentUserId;
                                const content = message.content || message.message;
                                const previousMessage = messages[index - 1];
                                const showDateSeparator = !previousMessage
                                    || messageDayKey(previousMessage) !== messageDayKey(message);
                                return (
                                    <Fragment key={message.id || `${message.created_at}-${index}`}>
                                        {showDateSeparator && (
                                            <div className="message-date-separator">
                                                <span>{messageDayLabel(message)}</span>
                                            </div>
                                        )}
                                        <div className={isOwnMessage ? "chat-message own" : "chat-message"}>
                                            {content && <p>{content}</p>}
                                            {message.attachment && (() => {
                                                const attachmentUrl = getMediaUrl(message.attachment);
                                                return isImageAttachment(attachmentUrl) ? (
                                                    <a href={attachmentUrl} target="_blank" rel="noreferrer">
                                                        <img className="chat-attachment-image" src={attachmentUrl} alt="Chat attachment" />
                                                    </a>
                                                ) : (
                                                    <a className="chat-attachment-link" href={attachmentUrl} target="_blank" rel="noreferrer">
                                                        Open attachment
                                                    </a>
                                                );
                                            })()}
                                            <small>
                                                {message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) : ""}
                                                {isOwnMessage && message.is_read ? " · Seen" : ""}
                                            </small>
                                        </div>
                                    </Fragment>
                                );
                            })
                        ) : (
                            <div className="chat-empty">
                                <h2>Start the conversation</h2>
                                <p>Send a message to get things going.</p>
                            </div>
                        )}
                        {peerTyping && <p className="typing-indicator">Typing...</p>}
                        <div ref={endOfMessagesRef} />
                    </div>

                    <form className="message-form" onSubmit={sendMessage}>
                        <label className="chat-attachment-picker">
                            <input
                                ref={attachmentInputRef}
                                type="file"
                                accept="image/*,video/*,audio/*,application/pdf,text/plain"
                                onChange={(event) => setAttachment(event.target.files?.[0] || null)}
                                disabled={sending}
                            />
                            <span>{attachment ? "Change file" : "Attach"}</span>
                        </label>
                        {attachment && <span className="chat-attachment-name">{attachment.name}</span>}
                        <label className="sr-only" htmlFor="message-input">Write a message</label>
                        <input
                            id="message-input"
                            value={text}
                            onChange={handleTextChange}
                            placeholder="Write a message..."
                            maxLength={5000}
                            autoComplete="off"
                            disabled={sending}
                        />
                        {attachment && (
                            <button
                                type="button"
                                className="chat-attachment-remove"
                                onClick={() => {
                                    setAttachment(null);
                                    if (attachmentInputRef.current) attachmentInputRef.current.value = "";
                                }}
                                disabled={sending}
                            >
                                Remove file
                            </button>
                        )}
                        <button className="button-primary" type="submit" disabled={sending || !text.trim()}>
                            {sending ? "Sending..." : "Send"}
                        </button>
                    </form>
                </section>
            ) : (
                <section className="chat-empty chat-empty-panel">
                    <span className="empty-state-icon" aria-hidden="true">✉</span>
                    <h2>Select a conversation</h2>
                    <p>Choose a person from your inbox or find someone new.</p>
                    <Link to="/search" className="button-secondary">Discover people</Link>
                </section>
            )}
        </main>
    );
}

export default Messages;
