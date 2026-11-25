import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import api, { getMediaUrl } from "../api/axios";
import useFocusTrap from "../hooks/useFocusTrap";
import UserAvatar from "./UserAvatar";

const STORY_DURATION = 5000;
const MAX_STORY_SIZE = 25 * 1024 * 1024;

function isVideoSource(source) {
    return /\.(mp4|webm|ogg|mov|m4v)(\?|$)/i.test(source || "");
}

function getErrorMessage(error, fallback) {
    if (!error.response) return "Cannot connect to the server. Please try again.";
    const data = error.response.data;
    if (!data || typeof data === "string") return fallback;
    if (data.detail) return data.detail;
    const first = Object.values(data)[0];
    if (Array.isArray(first) && first.length) return String(first[0]);
    if (typeof first === "string") return first;
    return fallback;
}

function Stories() {
    const [stories, setStories] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [viewedIds, setViewedIds] = useState(() => new Set());
    const [viewer, setViewer] = useState(null);
    const [createOpen, setCreateOpen] = useState(false);
    const [createText, setCreateText] = useState("");
    const [createPrivacy, setCreatePrivacy] = useState("public");
    const [createFile, setCreateFile] = useState(null);
    const [createPreview, setCreatePreview] = useState("");
    const [createProgress, setCreateProgress] = useState(0);
    const [createError, setCreateError] = useState("");
    const [creating, setCreating] = useState(false);
    const [paused, setPaused] = useState(false);
    const [reducedMotion, setReducedMotion] = useState(
        () => window.matchMedia?.("(prefers-reduced-motion: reduce)").matches || false,
    );

    const stripRef = useRef(null);
    const viewedRef = useRef(new Set());
    const previewRef = useRef("");
    const viewerCloseRef = useRef(null);
    const createCloseRef = useRef(null);
    const viewerRef = useRef(null);
    const createDialogRef = useRef(null);
    const fetchAbortRef = useRef(null);
    const currentUserId = Number(localStorage.getItem("user_id"));

    const fetchStories = useCallback(async () => {
        fetchAbortRef.current?.abort();
        const controller = new AbortController();
        fetchAbortRef.current = controller;
        setLoading(true);
        try {
            const response = await api.get("users/stories/", { signal: controller.signal });
            const items = Array.isArray(response.data)
                ? response.data
                : response.data?.results || [];
            setStories(items);
            setError("");
        } catch (error) {
            if (controller.signal.aborted || error.code === "ERR_CANCELED") return;
            setError("Stories could not be loaded right now.");
        } finally {
            if (fetchAbortRef.current === controller) setLoading(false);
        }
    }, []);

    useEffect(() => {
        let active = true;
        queueMicrotask(() => {
            if (active) fetchStories();
        });
        return () => {
            active = false;
        };
    }, [fetchStories]);

    useEffect(() => {
        if (!notice) return undefined;
        const timer = window.setTimeout(() => setNotice(""), 3500);
        return () => window.clearTimeout(timer);
    }, [notice]);

    useFocusTrap(Boolean(viewer), viewerRef, viewerCloseRef);
    useFocusTrap(createOpen, createDialogRef, createCloseRef);

    useEffect(() => {
        const query = window.matchMedia?.("(prefers-reduced-motion: reduce)");
        if (!query) return undefined;
        const handleChange = (event) => setReducedMotion(event.matches);
        query.addEventListener?.("change", handleChange);
        return () => query.removeEventListener?.("change", handleChange);
    }, []);

    useEffect(() => {
        return () => {
            fetchAbortRef.current?.abort();
            if (previewRef.current) URL.revokeObjectURL(previewRef.current);
        };
    }, []);

    const groups = useMemo(() => {
        const grouped = new Map();
        stories.forEach((story) => {
            const authorKey = String(story.author ?? story.author_username ?? "unknown");
            if (!grouped.has(authorKey)) {
                grouped.set(authorKey, {
                    key: authorKey,
                    author: authorKey,
                    username: story.author_username || "Member",
                    stories: [],
                });
            }
            grouped.get(authorKey).stories.push(story);
        });

        const list = [...grouped.values()];
        list.forEach((group) => {
            group.stories.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        });
        list.sort((a, b) => {
            const aOwn = Number(a.author) === currentUserId ? 1 : 0;
            const bOwn = Number(b.author) === currentUserId ? 1 : 0;
            if (aOwn !== bOwn) return bOwn - aOwn;
            return new Date(b.stories[0]?.created_at) - new Date(a.stories[0]?.created_at);
        });
        return list;
    }, [stories, currentUserId]);

    const markViewed = useCallback(async (story) => {
        if (!story || viewedRef.current.has(story.id)) return;
        viewedRef.current.add(story.id);
        setViewedIds(new Set(viewedRef.current));
        try {
            await api.post(`users/stories/${story.id}/view/`);
        } catch {
            viewedRef.current.delete(story.id);
            setViewedIds(new Set(viewedRef.current));
        }
    }, []);

    const activeGroup = viewer ? groups[viewer.groupIndex] : null;
    const activeStory = activeGroup?.stories[viewer.storyIndex] || null;
    const activeIsVideo = Boolean(activeStory?.media && isVideoSource(getMediaUrl(activeStory.media)));
    const autoAdvanceDisabled = paused || reducedMotion || activeIsVideo;

    useEffect(() => {
        if (activeStory) markViewed(activeStory);
    }, [activeStory, markViewed]);

    const closeViewer = useCallback(() => setViewer(null), []);

    const openStory = useCallback((groupIndex) => {
        setPaused(false);
        setViewer({ groupIndex, storyIndex: 0 });
    }, []);

    const goNext = useCallback(() => {
        setViewer((current) => {
            if (!current) return current;
            const group = groups[current.groupIndex];
            if (!group) return null;
            if (current.storyIndex < group.stories.length - 1) {
                return { ...current, storyIndex: current.storyIndex + 1 };
            }
            if (current.groupIndex < groups.length - 1) {
                return { groupIndex: current.groupIndex + 1, storyIndex: 0 };
            }
            return null;
        });
    }, [groups]);

    const goPrevious = useCallback(() => {
        setViewer((current) => {
            if (!current) return current;
            if (current.storyIndex > 0) {
                return { ...current, storyIndex: current.storyIndex - 1 };
            }
            if (current.groupIndex > 0) {
                const previousGroup = groups[current.groupIndex - 1];
                return {
                    groupIndex: current.groupIndex - 1,
                    storyIndex: Math.max((previousGroup?.stories.length || 1) - 1, 0),
                };
            }
            return current;
        });
    }, [groups]);

    useEffect(() => {
        if (!viewer || !activeStory || autoAdvanceDisabled) return undefined;
        const timer = window.setTimeout(goNext, STORY_DURATION);
        return () => window.clearTimeout(timer);
    }, [viewer, activeStory, goNext, autoAdvanceDisabled]);

    useEffect(() => {
        if (!viewer) return undefined;
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        viewerCloseRef.current?.focus();

        const handleKeyDown = (event) => {
            if (event.key === "Escape") closeViewer();
            if (event.key === "ArrowRight") goNext();
            if (event.key === "ArrowLeft") goPrevious();
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.body.style.overflow = previousOverflow;
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [viewer, closeViewer, goNext, goPrevious]);

    const scrollStories = (direction) => {
        stripRef.current?.scrollBy({ left: direction * 320, behavior: "smooth" });
    };

    const resetCreateForm = useCallback(() => {
        if (previewRef.current) URL.revokeObjectURL(previewRef.current);
        previewRef.current = "";
        setCreateFile(null);
        setCreatePreview("");
        setCreateText("");
        setCreatePrivacy("public");
        setCreateProgress(0);
        setCreateError("");
    }, []);

    const closeCreate = useCallback(() => {
        if (creating) return;
        setCreateOpen(false);
        resetCreateForm();
    }, [creating, resetCreateForm]);

    useEffect(() => {
        if (!createOpen) return undefined;
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        createCloseRef.current?.focus();

        const handleKeyDown = (event) => {
            if (event.key === "Escape") closeCreate();
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.body.style.overflow = previousOverflow;
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [createOpen, closeCreate]);

    const handleCreateFile = (event) => {
        const file = event.target.files?.[0];
        if (!file) return;
        if (!file.type.startsWith("image/") && !file.type.startsWith("video/")) {
            setCreateError("Choose an image or video file.");
            event.target.value = "";
            return;
        }
        if (file.size > MAX_STORY_SIZE) {
            setCreateError("Story media must be 25 MB or smaller.");
            event.target.value = "";
            return;
        }
        if (previewRef.current) URL.revokeObjectURL(previewRef.current);
        previewRef.current = URL.createObjectURL(file);
        setCreateFile(file);
        setCreatePreview(previewRef.current);
        setCreateError("");
    };

    const handleCreateStory = async (event) => {
        event.preventDefault();
        if (creating) return;
        if (!createFile && !createText.trim()) {
            setCreateError("Add a photo, video, or a short message.");
            return;
        }

        const formData = new FormData();
        if (createFile) formData.append("media", createFile);
        formData.append("text", createText.trim());
        formData.append("privacy", createPrivacy);

        setCreating(true);
        setCreateError("");
        setCreateProgress(0);
        try {
            const response = await api.post("users/stories/", formData, {
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        setCreateProgress(Math.min(100, Math.round((progressEvent.loaded * 100) / progressEvent.total)));
                    }
                },
            });
            setStories((current) => [response.data, ...current.filter((story) => story.id !== response.data.id)]);
            setNotice("Your story is live for 24 hours.");
            setCreateOpen(false);
            resetCreateForm();
        } catch (err) {
            setCreateError(getErrorMessage(err, "Unable to share your story."));
        } finally {
            setCreating(false);
        }
    };

    if (loading) {
        return (
            <section className="stories-strip" aria-label="Stories" aria-busy="true">
                <div className="stories-skeleton-heading"><span /><span /></div>
                <div className="stories-track">
                    {[1, 2, 3, 4, 5].map((item) => (
                        <div className="story-skeleton" key={item}><span /><i /></div>
                    ))}
                </div>
            </section>
        );
    }

    return (
        <section className="stories-strip" aria-label="Stories">
            <header className="stories-header">
                <div>
                    <span className="rail-eyebrow">STORIES</span>
                    <h2>Moments from your circle</h2>
                </div>
                {groups.length > 3 && (
                    <div className="stories-scroll-controls">
                        <button type="button" onClick={() => scrollStories(-1)} aria-label="Scroll stories left">‹</button>
                        <button type="button" onClick={() => scrollStories(1)} aria-label="Scroll stories right">›</button>
                    </div>
                )}
            </header>

            {notice && <p className="form-success stories-notice" role="status">{notice}</p>}
            {error && (
                <div className="stories-error" role="alert">
                    <span>{error}</span>
                    <button type="button" className="button-secondary" onClick={fetchStories}>Try again</button>
                </div>
            )}

            <div className="stories-track" ref={stripRef}>
                <button type="button" className="story-card story-create-card" onClick={() => setCreateOpen(true)}>
                    <span className="story-avatar-ring is-create"><span className="story-create-plus" aria-hidden="true">+</span></span>
                    <span className="story-card-label">Create story</span>
                </button>

                {groups.map((group, groupIndex) => {
                    const latest = group.stories[0];
                    const hasUnseen = group.stories.some((story) => !viewedIds.has(story.id));
                    const isOwn = Number(group.author) === currentUserId;
                    return (
                        <button
                            type="button"
                            className="story-card"
                            key={group.key}
                            onClick={() => openStory(groupIndex)}
                            aria-label={`View ${isOwn ? "your" : `${group.username}'s`} story`}
                        >
                            <span className={`story-avatar-ring${hasUnseen ? " is-unseen" : ""}`}>
                                <UserAvatar className="story-avatar" name={group.username} />
                            </span>
                            <span className="story-card-label">{isOwn ? "Your story" : group.username}</span>
                            {latest?.created_at && (
                                <small>{new Date(latest.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</small>
                            )}
                        </button>
                    );
                })}

                {!groups.length && !error && (
                    <p className="stories-empty">No active stories yet. Share the first one.</p>
                )}
            </div>

            {viewer && activeGroup && activeStory && (
                <div
                    className="story-viewer-backdrop"
                    onMouseDown={(event) => {
                        if (event.target === event.currentTarget) closeViewer();
                    }}
                >
                    <section
                        ref={viewerRef}
                        className="story-viewer"
                        role="dialog"
                        aria-modal="true"
                        aria-label={`Story from ${activeGroup.username}`}
                    >
                        <header className="story-viewer-top">
                            <div
                                className={`story-progress${paused ? " is-paused" : ""}${autoAdvanceDisabled && !paused ? " is-static" : ""}`}
                                aria-hidden="true"
                            >
                                {activeGroup.stories.map((story) => (
                                    <span
                                        key={story.id}
                                        className={story.id === activeStory.id ? "is-active" : ""}
                                    >
                                        <i
                                            key={`${viewer.groupIndex}-${viewer.storyIndex}`}
                                            style={{ animationDuration: `${STORY_DURATION}ms` }}
                                        />
                                    </span>
                                ))}
                            </div>
                            <div className="story-viewer-author">
                                <UserAvatar className="story-viewer-avatar" name={activeGroup.username} />
                                <div>
                                    <strong>{activeGroup.username}</strong>
                                    {activeStory.created_at && (
                                        <small>{new Date(activeStory.created_at).toLocaleString()}</small>
                                    )}
                                </div>
                            </div>
                            <div className="story-viewer-controls">
                                {!activeIsVideo && !reducedMotion && (
                                    <button
                                        type="button"
                                        className="story-pause"
                                        onClick={() => setPaused((current) => !current)}
                                        aria-label={paused ? "Resume story" : "Pause story"}
                                        aria-pressed={paused}
                                    >
                                        {paused ? "▶" : "❚❚"}
                                    </button>
                                )}
                                <button
                                    ref={viewerCloseRef}
                                    type="button"
                                    className="story-close"
                                    onClick={closeViewer}
                                    aria-label="Close story"
                                >
                                    ×
                                </button>
                            </div>
                        </header>

                        <div className="story-viewer-stage">
                            <button
                                type="button"
                                className="story-nav-button is-prev"
                                onClick={goPrevious}
                                disabled={viewer.groupIndex === 0 && viewer.storyIndex === 0}
                                aria-label="Previous story"
                            >
                                ‹
                            </button>
                            {activeStory.media ? (
                                isVideoSource(getMediaUrl(activeStory.media)) ? (
                                    <video
                                        key={activeStory.id}
                                        src={getMediaUrl(activeStory.media)}
                                        autoPlay
                                        controls
                                        muted
                                        playsInline
                                        preload="metadata"
                                        onEnded={goNext}
                                        aria-label={`Story media from ${activeGroup.username}`}
                                    />
                                ) : (
                                    <img
                                        key={activeStory.id}
                                        src={getMediaUrl(activeStory.media)}
                                        alt={`Story from ${activeGroup.username}`}
                                    />
                                )
                            ) : (
                                <div className="story-text-stage">
                                    <p>{activeStory.text || "Story"}</p>
                                </div>
                            )}
                            <button
                                type="button"
                                className="story-nav-button is-next"
                                onClick={goNext}
                                disabled={viewer.groupIndex === groups.length - 1 && viewer.storyIndex === activeGroup.stories.length - 1}
                                aria-label="Next story"
                            >
                                ›
                            </button>
                        </div>
                        {activeStory.text && activeStory.media && (
                            <p className="story-viewer-text">{activeStory.text}</p>
                        )}
                    </section>
                </div>
            )}

            {createOpen && (
                <div
                    className="dialog-backdrop"
                    onMouseDown={(event) => {
                        if (event.target === event.currentTarget) closeCreate();
                    }}
                >
                    <section
                        ref={createDialogRef}
                        className="story-create-dialog"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="create-story-title"
                    >
                        <header className="story-create-header">
                            <div>
                                <span className="rail-eyebrow">NEW STORY</span>
                                <h2 id="create-story-title">Share a moment</h2>
                            </div>
                            <button
                                ref={createCloseRef}
                                type="button"
                                className="dialog-close"
                                onClick={closeCreate}
                                disabled={creating}
                                aria-label="Close story creator"
                            >
                                ×
                            </button>
                        </header>

                        <form onSubmit={handleCreateStory}>
                            <label className="story-file-drop" htmlFor="story-media">
                                {createPreview ? (
                                    createFile?.type?.startsWith("video/") ? (
                                        <video src={createPreview} controls aria-label="Story preview" />
                                    ) : (
                                        <img src={createPreview} alt="Story preview" />
                                    )
                                ) : (
                                    <span>
                                        <strong>Add a photo or video</strong>
                                        <small>Images and videos up to 25 MB</small>
                                    </span>
                                )}
                            </label>
                            <input
                                id="story-media"
                                className="sr-only"
                                type="file"
                                accept="image/*,video/*"
                                onChange={handleCreateFile}
                                disabled={creating}
                            />

                            <label htmlFor="story-text">Caption</label>
                            <textarea
                                id="story-text"
                                rows={2}
                                maxLength={500}
                                placeholder="Add a caption..."
                                value={createText}
                                onChange={(event) => setCreateText(event.target.value)}
                                disabled={creating}
                            />

                            <label htmlFor="story-privacy">Who can see this?</label>
                            <select
                                id="story-privacy"
                                value={createPrivacy}
                                onChange={(event) => setCreatePrivacy(event.target.value)}
                                disabled={creating}
                            >
                                <option value="public">Public</option>
                                <option value="followers">Followers</option>
                                <option value="friends">Friends</option>
                            </select>

                            {createError && <p className="form-error" role="alert">{createError}</p>}
                            {creating && (
                                <div className="story-upload-progress" aria-label="Uploading story">
                                    <span style={{ width: `${createProgress}%` }} />
                                </div>
                            )}

                            <div className="dialog-actions">
                                <button type="button" className="button-secondary" onClick={closeCreate} disabled={creating}>Cancel</button>
                                <button type="submit" className="button-primary" disabled={creating}>
                                    {creating ? "Sharing..." : "Share story"}
                                </button>
                            </div>
                        </form>
                    </section>
                </div>
            )}
        </section>
    );
}

export default Stories;
