import { useEffect, useRef, useState } from "react";
import api from "../api/axios";
import useFocusTrap from "../hooks/useFocusTrap";

const preferenceLabels = [
    { key: "likes", label: "Likes", hint: "When someone likes your post" },
    { key: "comments", label: "Comments", hint: "When someone comments on your post" },
    { key: "replies", label: "Replies", hint: "When someone replies to your comment" },
    { key: "follows", label: "Follows", hint: "When someone follows you" },
    { key: "friend_requests", label: "Friend requests", hint: "When someone sends you a request" },
    { key: "messages", label: "Messages", hint: "When someone messages you" },
    { key: "mentions", label: "Mentions", hint: "When someone mentions you" },
    { key: "story_reactions", label: "Story reactions", hint: "When someone reacts to your story" },
];

function NotificationSettingsDialog({ open = true, onClose }) {
    const [preferences, setPreferences] = useState(null);
    const [savingKey, setSavingKey] = useState("");
    const [error, setError] = useState("");
    const closeButtonRef = useRef(null);
    const dialogRef = useRef(null);

    useFocusTrap(open, dialogRef, closeButtonRef);

    useEffect(() => {
        if (!open) return undefined;
        let active = true;
        api.get("notifications/preferences/")
            .then((response) => {
                if (active) setPreferences(response.data);
            })
            .catch(() => {
                if (active) setError("Notification settings could not be loaded.");
            });
        return () => {
            active = false;
        };
    }, [open]);

    useEffect(() => {
        if (!open) return undefined;
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        closeButtonRef.current?.focus();

        const handleKeyDown = (event) => {
            if (event.key === "Escape") onClose();
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.body.style.overflow = previousOverflow;
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [open, onClose]);

    const togglePreference = async (key) => {
        if (!preferences || savingKey) return;
        const previousValue = Boolean(preferences[key]);
        const nextValue = !previousValue;
        setPreferences((current) => ({ ...current, [key]: nextValue }));
        setSavingKey(key);
        setError("");
        try {
            const response = await api.patch("notifications/preferences/", { [key]: nextValue });
            setPreferences(response.data);
        } catch {
            setPreferences((current) => ({ ...current, [key]: previousValue }));
            setError(`Could not update ${preferenceLabels.find((item) => item.key === key)?.label || "that setting"}.`);
        } finally {
            setSavingKey("");
        }
    };

    if (!open) return null;

    return (
        <div
            className="dialog-backdrop"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) onClose();
            }}
        >
            <section
                ref={dialogRef}
                className="settings-dialog"
                role="dialog"
                aria-modal="true"
                aria-labelledby="notification-settings-title"
            >
                <header className="settings-dialog-header">
                    <div>
                        <p className="page-eyebrow">PREFERENCES</p>
                        <h2 id="notification-settings-title">Notification settings</h2>
                    </div>
                    <button
                        ref={closeButtonRef}
                        type="button"
                        className="dialog-close"
                        onClick={onClose}
                        aria-label="Close notification settings"
                    >
                        ×
                    </button>
                </header>

                {error && <p className="form-error" role="alert">{error}</p>}

                {!preferences && !error ? (
                    <div className="settings-loading" role="status" aria-label="Loading notification settings">
                        <span /><span /><span />
                    </div>
                ) : preferences ? (
                    <div className="settings-list">
                        {preferenceLabels.map((item) => {
                            const enabled = Boolean(preferences[item.key]);
                            const busy = savingKey === item.key;
                            return (
                                <div className="settings-row" key={item.key}>
                                    <div>
                                        <strong>{item.label}</strong>
                                        <small>{item.hint}</small>
                                    </div>
                                    <button
                                        type="button"
                                        role="switch"
                                        aria-checked={enabled}
                                        aria-label={`${enabled ? "Disable" : "Enable"} ${item.label} notifications`}
                                        className={`settings-switch${enabled ? " is-on" : ""}`}
                                        onClick={() => togglePreference(item.key)}
                                        disabled={Boolean(savingKey)}
                                    >
                                        <span aria-hidden="true" />
                                        <span className="sr-only">{busy ? "Saving" : enabled ? "On" : "Off"}</span>
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                ) : null}

                <footer className="settings-dialog-footer">
                    <button type="button" className="button-secondary" onClick={onClose}>Done</button>
                </footer>
            </section>
        </div>
    );
}

export default NotificationSettingsDialog;
