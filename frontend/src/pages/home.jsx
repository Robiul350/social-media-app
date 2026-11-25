
import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Link, useNavigate } from "react-router-dom";
import api, { getMediaUrl } from "../api/axios";
import { getProfileSnapshot, subscribeProfile } from "../api/profileStore";
import ConfirmDialog from "../components/ConfirmDialog";
import MediaViewer from "../components/MediaViewer";
import PostActions from "../components/PostActions";
import Stories from "../components/Stories";
import UserAvatar from "../components/UserAvatar";

const getErrorMessage = (err, fallback) => {
    if (!err.response) {
        return "Cannot connect to the server. Please try again.";
    }

    const data = err.response.data;

    if (!data || typeof data === "string") return fallback;
    if (data.detail) return data.detail;

    const first = Object.values(data)[0];

    if (Array.isArray(first) && first.length) return String(first[0]);
    if (typeof first === "string") return first;

    return fallback;
};

const getAuthorId = (post) => {
    if (post.author_id) return post.author_id;
    const author = post.author;

    if (author && typeof author === "object") {
        return author.id;
    }

    return author;
};

const getAuthorName = (post) => {
    if (post.author_full_name && post.author_full_name !== post.author_username) {
        return post.author_full_name;
    }
    const fullName = [
        post.author_first_name,
        post.author_last_name
    ].filter(Boolean).join(" ");

    return (
        fullName ||
        post.author?.username ||
        post.author_username ||
        post.username ||
        (typeof post.author === "string" ? post.author : "") ||
        "User"
    );
};

const audienceLabels = {
    public: "Public",
    followers: "Followers",
    friends: "Friends",
};

const formatRelativeTime = (value) => {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    const seconds = Math.round((date.getTime() - Date.now()) / 1000);
    const absolute = Math.abs(seconds);
    if (absolute < 60) return "just now";
    const units = [
        ["year", 31536000],
        ["month", 2592000],
        ["week", 604800],
        ["day", 86400],
        ["hour", 3600],
        ["minute", 60],
    ];
    for (const [unit, amount] of units) {
        if (absolute >= amount) {
            return new Intl.RelativeTimeFormat(undefined, { numeric: "auto" })
                .format(Math.round(seconds / amount), unit);
        }
    }
    return "just now";
};

function Home() {
    const navigate = useNavigate();
    const fileInputRef = useRef(null);
    const mediaPreviewRef = useRef("");
    const loadMoreRef = useRef(null);
    const initialLoadRef = useRef(false);
    const firstPageIdsRef = useRef([]);

    const [posts, setPosts] = useState([]);
    const profileState = useSyncExternalStore(subscribeProfile, getProfileSnapshot, getProfileSnapshot);
    const [nextPageUrl, setNextPageUrl] = useState(null);
    const [loadingMore, setLoadingMore] = useState(false);
    const [paginationError, setPaginationError] = useState("");
    const [error, setError] = useState("");
    const [feedError, setFeedError] = useState("");
    const [notice, setNotice] = useState("");
    const [composerError, setComposerError] = useState("");
    const [content, setContent] = useState("");
    const [media, setMedia] = useState(null);
    const [mediaType, setMediaType] = useState("image");
    const [mediaPreview, setMediaPreview] = useState("");
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [audience, setAudience] = useState("public");
    const [busyPostId, setBusyPostId] = useState(null);
    const [editingPost, setEditingPost] = useState(null);
    const [editContent, setEditContent] = useState("");
    const [savingEdit, setSavingEdit] = useState(false);
    const [postToDelete, setPostToDelete] = useState(null);
    const [deletingPost, setDeletingPost] = useState(false);
    const [viewingImage, setViewingImage] = useState(null);
    const [openPostMenu, setOpenPostMenu] = useState(null);
    const [reportReasons, setReportReasons] = useState({});
    const [reporting, setReporting] = useState(false);

    const loggedIn = Boolean(localStorage.getItem("access"));
    const currentUserId = Number(localStorage.getItem("user_id"));
    const currentUsername = localStorage.getItem("username");
    const closeMediaViewer = useCallback(() => setViewingImage(null), []);
    const updatePost = useCallback((postId, changes) => {
        setPosts((current) => current.map((item) =>
            item.id === postId ? { ...item, ...changes } : item
        ));
    }, []);

    // Session Expired
    const handleSessionExpired = useCallback(() => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user_id");
        localStorage.removeItem("username");
        window.dispatchEvent(new Event("socialconnect:auth-change"));
        navigate("/login", { replace: true });
    }, [navigate]);

    const fetchPosts = useCallback(async ({ preservePages = false } = {}) => {
        try {
            const response = await api.get("social/feed/?page=1");
            const data = response.data;
            const firstPage = Array.isArray(data) ? data : data.results || [];

            if (preservePages) {
                setPosts((current) => {
                    const staleFirstPageIds = new Set(firstPageIdsRef.current);
                    const freshIds = new Set(firstPage.map((post) => post.id));
                    const retained = current.filter((post) =>
                        !staleFirstPageIds.has(post.id) && !freshIds.has(post.id)
                    );
                    return [...firstPage, ...retained];
                });
                setNextPageUrl(Array.isArray(data) ? null : data.next || null);
            } else {
                setPosts(firstPage);
                setNextPageUrl(Array.isArray(data) ? null : data.next || null);
            }

            firstPageIdsRef.current = firstPage.map((post) => post.id);
            setPaginationError("");

            setFeedError("");
            return data;

        } catch (err) {
            if (
                err.response?.status === 401 &&
                localStorage.getItem("access")
            ) {
                handleSessionExpired();
                return null;
            }

            setFeedError(
                getErrorMessage(err, "Unable to load posts.")
            );
            return null;

        } finally {
            setLoading(false);
        }
    }, [handleSessionExpired]);

    const loadMorePosts = useCallback(async () => {
        if (!nextPageUrl || loadingMore) return;
        setLoadingMore(true);
        setPaginationError("");
        try {
            const response = await api.get(nextPageUrl);
            const data = response.data;
            const newPosts = Array.isArray(data) ? data : data.results || [];
            setPosts((current) => {
                const seenIds = new Set(current.map((post) => post.id));
                return [...current, ...newPosts.filter((post) => !seenIds.has(post.id))];
            });
            setNextPageUrl(Array.isArray(data) ? null : data.next || null);
        } catch {
            setPaginationError("Unable to load more posts.");
        } finally {
            setLoadingMore(false);
        }
    }, [loadingMore, nextPageUrl]);

    useEffect(() => {
        if (initialLoadRef.current) return;
        initialLoadRef.current = true;
        fetchPosts();
    }, [fetchPosts]);

    useEffect(() => {
        const target = loadMoreRef.current;
        if (!target || !nextPageUrl || paginationError || !("IntersectionObserver" in window)) {
            return undefined;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                if (entries.some((entry) => entry.isIntersecting)) loadMorePosts();
            },
            { rootMargin: "280px" }
        );
        observer.observe(target);
        return () => observer.disconnect();
    }, [loadMorePosts, nextPageUrl, paginationError]);

    useEffect(() => {
        return () => {
            if (mediaPreviewRef.current) URL.revokeObjectURL(mediaPreviewRef.current);
        };
    }, []);

    useEffect(() => {
        if (!editingPost) return undefined;
        const handleKeyDown = (event) => {
            if (event.key === "Escape" && !savingEdit) setEditingPost(null);
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [editingPost, savingEdit]);

    // Auto Hide Notice
    useEffect(() => {
        if (!notice) return undefined;

        const timer = setTimeout(() => setNotice(""), 3000);

        return () => clearTimeout(timer);
    }, [notice]);

    // Check Post Ownership
    const isMyPost = (post) => {
        const authorId = getAuthorId(post);

        if (
            currentUserId > 0 &&
            authorId !== undefined &&
            Number(authorId) === currentUserId
        ) {
            return true;
        }

        return (
            Boolean(currentUsername) &&
            (
                post.author_username === currentUsername ||
                post.author?.username === currentUsername
            )
        );
    };

    // Reset Media
    const resetMedia = () => {
        if (mediaPreviewRef.current) URL.revokeObjectURL(mediaPreviewRef.current);
        mediaPreviewRef.current = "";
        setMedia(null);
        setMediaPreview("");
        if (fileInputRef.current) fileInputRef.current.value = "";
    };

    // Change Media Type
    const handleMediaTypeChange = (e) => {
        setMediaType(e.target.value);
        resetMedia();
    };

    // Select Media
    const handleMediaChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const expectedType = mediaType === "video" ? "video/" : "image/";
        const sizeLimit = mediaType === "video" ? 100 : 10;

        if (!file.type.startsWith(expectedType)) {
            setComposerError(`Choose a valid ${mediaType} file.`);
            e.target.value = "";
            return;
        }
        if (file.size > sizeLimit * 1024 * 1024) {
            setComposerError(`${mediaType === "video" ? "Videos" : "Images"} must be ${sizeLimit} MB or smaller.`);
            e.target.value = "";
            return;
        }

        setComposerError("");
        if (mediaPreviewRef.current) URL.revokeObjectURL(mediaPreviewRef.current);
        mediaPreviewRef.current = URL.createObjectURL(file);
        setMediaPreview(mediaPreviewRef.current);
        setMedia(file);
    };

    // Create Post
    const handleCreatePost = async (e) => {
        e.preventDefault();

        if (uploading) return;
        if (!loggedIn) {
            setComposerError("Please login before creating a post.");
            return;
        }

        if (!content.trim() && !media) {
            setComposerError("Please write something or select a media file.");
            return;
        }

        const formData = new FormData();
        formData.append("content", content.trim());
        formData.append("audience", audience);

        if (media) {
            formData.append(
                mediaType === "video" ? "video" : "image",
                media
            );
        }

        try {
            setUploading(true);
            setUploadProgress(0);
            setComposerError("");

            const response = await api.post("posts/", formData, {
                onUploadProgress: (progressEvent) => {
                    if (progressEvent.total) {
                        setUploadProgress(
                            Math.min(100, Math.round((progressEvent.loaded * 100) / progressEvent.total))
                        );
                    }
                },
            });

            setContent("");
            resetMedia();
            setPosts((current) => [
                response.data,
                ...current.filter((post) => post.id !== response.data.id),
            ]);

            setNotice("Post published successfully!");

        } catch (err) {
            if (err.response?.status === 401) {
                handleSessionExpired();
                return;
            }

            setComposerError(
                getErrorMessage(err, "Unable to create post.")
            );

        } finally {
            setUploading(false);
            setUploadProgress(0);
        }
    };

    const openEditPost = (post) => {
        if (!isMyPost(post)) {
            setError("You cannot edit someone else's post.");
            return;
        }
        setOpenPostMenu(null);
        setEditingPost(post);
        setEditContent(post.content || "");
    };

    const handleEditPost = async (event) => {
        event.preventDefault();
        if (!editingPost) return;

        if (!editContent.trim() && !editingPost.image && !editingPost.video) {
            setError("Post content cannot be empty.");
            return;
        }

        try {
            setError("");
            setSavingEdit(true);
            const response = await api.patch(`posts/${editingPost.id}/`, {
                content: editContent.trim(),
            });
            setPosts((current) =>
                current.map((item) => item.id === editingPost.id
                    ? { ...item, ...response.data }
                    : item)
            );
            setNotice("Post updated successfully!");
            setEditingPost(null);

        } catch (err) {
            setError(
                getErrorMessage(err, "Unable to edit post.")
            );
        } finally {
            setSavingEdit(false);
        }
    };

    const handleDeletePost = async () => {
        if (!postToDelete || !isMyPost(postToDelete)) {
            setError("You cannot delete someone else's post.");
            return;
        }

        try {
            setError("");
            setDeletingPost(true);
            await api.delete(`posts/${postToDelete.id}/`);
            setPosts((previousPosts) =>
                previousPosts.filter((item) => item.id !== postToDelete.id)
            );
            setNotice("Post deleted successfully!");
        } catch (err) {
            setError(
                getErrorMessage(err, "Unable to delete post.")
            );
        } finally {
            setDeletingPost(false);
            setPostToDelete(null);
        }
    };

    const handleShare = async (post) => {
        const shareUrl = `${window.location.origin}/posts/${post.id}`;

        try {
            if (navigator.share) {
                await navigator.share({
                    title: "SocialConnect Post",
                    text: post.content || "Check out this post!",
                    url: shareUrl,
                });
            } else {
                if (!navigator.clipboard?.writeText) {
                    throw new Error("Link copying is not available in this browser.");
                }
                await navigator.clipboard.writeText(shareUrl);
                setNotice("Post link copied!");
            }

        } catch (err) {
            if (err.name !== "AbortError") {
                setError(err.message || "Unable to share this post.");
            }
        }
    };

    const handleReportPost = async (event, post) => {
        event.preventDefault();
        const reason = (reportReasons[post.id] || "").trim();
        if (!reason || reporting) return;

        setReporting(true);
        setError("");
        try {
            await api.post(`posts/${post.id}/report/`, { reason });
            setNotice("Thanks for reporting this post.");
            setReportReasons((current) => ({ ...current, [post.id]: "" }));
            setOpenPostMenu(null);
        } catch (err) {
            setError(getErrorMessage(err, "Unable to report this post."));
        } finally {
            setReporting(false);
        }
    };

    const handleRepost = async (post) => {
        if (!loggedIn || busyPostId) return;
        setBusyPostId(post.id);
        setError("");
        try {
            const response = await api.post(`posts/${post.id}/repost/`);
            const createdRepost = response.status === 201;
            setPosts((current) => [
                response.data,
                ...current
                    .map((item) => item.id === post.id
                        ? {
                            ...item,
                            ...(createdRepost
                                ? { share_count: (item.share_count || 0) + 1 }
                                : {}),
                        }
                        : item)
                    .filter((item) => item.id !== response.data.id),
            ]);
            setNotice("Reposted to your profile.");
            setOpenPostMenu(null);
        } catch (err) {
            if (err.response?.status === 401) {
                handleSessionExpired();
                return;
            }
            setError(getErrorMessage(err, "Unable to repost this post."));
        } finally {
            setBusyPostId(null);
        }
    };

    const handlePinPost = async (post) => {
        if (!isMyPost(post) || busyPostId) return;
        setBusyPostId(post.id);
        setError("");
        try {
            const response = await api.post(`posts/${post.id}/pin/`);
            updatePost(post.id, { is_pinned: Boolean(response.data.pinned) });
            setNotice(response.data.pinned ? "Post pinned to your profile." : "Post unpinned.");
            setOpenPostMenu(null);
        } catch (err) {
            setError(getErrorMessage(err, "Unable to update your pinned post."));
        } finally {
            setBusyPostId(null);
        }
    };

    useEffect(() => {
        if (!openPostMenu) return undefined;

        const panel = document.querySelector(`[data-post-menu-panel="${openPostMenu}"]`);
        panel?.querySelector("button")?.focus();

        const handlePointerDown = (event) => {
            if (!event.target.closest?.(".post-menu")) setOpenPostMenu(null);
        };
        const handleKeyDown = (event) => {
            if (event.key === "Escape") {
                setOpenPostMenu(null);
                return;
            }
            if (event.key !== "ArrowDown" && event.key !== "ArrowUp") return;
            const items = panel
                ? [...panel.querySelectorAll('[role="menuitem"], button:not([disabled])')]
                    .filter((item) => item.offsetParent !== null)
                : [];
            if (!items.length) return;
            event.preventDefault();
            const currentIndex = items.indexOf(document.activeElement);
            const nextIndex = event.key === "ArrowDown"
                ? (currentIndex + 1) % items.length
                : (currentIndex <= 0 ? items.length - 1 : currentIndex - 1);
            items[nextIndex].focus();
        };
        document.addEventListener("pointerdown", handlePointerDown);
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.removeEventListener("pointerdown", handlePointerDown);
            document.removeEventListener("keydown", handleKeyDown);
        };
    }, [openPostMenu]);

    const refreshFeed = useCallback(async () => {
        setRefreshing(true);
        await fetchPosts({ preservePages: true });
        setRefreshing(false);
    }, [fetchPosts]);

    return (
        <section className="feed-container">
                <header className="feed-header">
                    <div>
                        <p className="page-eyebrow">YOUR COMMUNITY</p>
                        <h1>Home</h1>
                    </div>
                    <button
                        type="button"
                        className="button-secondary refresh-button"
                        onClick={refreshFeed}
                        disabled={refreshing || loading}
                    >
                        {refreshing || loading ? "Refreshing..." : "Refresh"}
                    </button>
                </header>

                {loggedIn && <Stories />}

                {loggedIn && (
                    <div className="create-post-card">
                        <div className="composer-heading">
                            <UserAvatar
                                className="composer-avatar"
                                src={profileState.data?.profile?.profile_picture}
                                name={profileState.data?.username || currentUsername || "You"}
                            />
                            <div>
                                <h2>Share an update</h2>
                                <p>Post to your community</p>
                            </div>
                        </div>

                        <form onSubmit={handleCreatePost}>
                            <textarea
                                aria-label="Write a post"
                                placeholder="What's on your mind?"
                                rows={3}
                                value={content}
                                onChange={(e) =>
                                    setContent(e.target.value)
                                }
                            />

                            <div className="composer-toolbar">
                                <div className="composer-tool-group">
                                    <label className="sr-only" htmlFor="post-media-type">Media type</label>
                                    <select
                                        id="post-media-type"
                                        value={mediaType}
                                        onChange={handleMediaTypeChange}
                                        disabled={uploading}
                                    >
                                        <option value="image">Photo</option>
                                        <option value="video">Video</option>
                                    </select>
                                    <input
                                        id="post-media"
                                        ref={fileInputRef}
                                        className="sr-only"
                                        type="file"
                                        accept={
                                            mediaType === "video"
                                                ? "video/*"
                                                : "image/*"
                                        }
                                        onChange={handleMediaChange}
                                        disabled={uploading}
                                    />
                                    <label className="file-picker" htmlFor="post-media">
                                        Add {mediaType === "video" ? "video" : "photo"}
                                    </label>
                                    {media && (
                                        <button
                                            type="button"
                                            className="text-button"
                                            onClick={resetMedia}
                                            disabled={uploading}
                                        >
                                            Remove file
                                        </button>
                                    )}
                                </div>

                                <div className="composer-tool-group">
                                    <label className="sr-only" htmlFor="post-audience">Audience</label>
                                    <select
                                        id="post-audience"
                                        value={audience}
                                        onChange={(event) => setAudience(event.target.value)}
                                        disabled={uploading}
                                    >
                                        <option value="public">Public</option>
                                        <option value="followers">Followers</option>
                                        <option value="friends">Friends</option>
                                    </select>
                                    <button
                                        className="button-primary composer-submit"
                                        type="submit"
                                        disabled={uploading}
                                    >
                                        {uploading ? "Publishing..." : "Publish"}
                                    </button>
                                </div>
                            </div>

                            {uploading && (
                                <div className="composer-upload-progress" aria-label="Uploading post">
                                    <span style={{ width: `${uploadProgress}%` }} />
                                </div>
                            )}

                            {mediaPreview && (
                                <div className="media-preview">
                                    {mediaType === "video" ? (
                                        <video src={mediaPreview} controls aria-label="Video preview" />
                                    ) : (
                                        <img src={mediaPreview} alt={`Preview of ${media.name}`} />
                                    )}
                                    <span>{media.name}</span>
                                </div>
                            )}
                        </form>
                        {composerError && <p className="form-error composer-error" role="alert">{composerError}</p>}
                        {profileState.error && <p className="composer-profile-error" role="status">{profileState.error}</p>}
                    </div>
                )}

                {notice && (
                    <div className="form-success" role="status">
                        {notice}
                    </div>
                )}

                {error && (
                    <div className="form-error" role="alert">
                        {error}
                    </div>
                )}

                {feedError && posts.length > 0 && (
                    <div className="form-error" role="alert">
                        {feedError}
                    </div>
                )}

                <div className="posts-container">
                    <div className="posts-heading">
                        <h2>Latest posts</h2>
                        <span>Newest first</span>
                    </div>

                    {loading ? (
                        <div className="feed-skeletons" role="status" aria-label="Loading posts">
                            {[1, 2, 3].map((item) => <div className="post-skeleton" key={item} />)}
                        </div>
                    ) : feedError && posts.length === 0 ? (
                        <div className="empty-state">
                            <h3>Feed unavailable</h3>
                            <p role="alert">{feedError}</p>
                            <button type="button" className="button-secondary" onClick={refreshFeed}>Try again</button>
                        </div>
                    ) : posts.length === 0 ? (
                        <div className="empty-state">
                            <span className="empty-state-icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24"><path d="m12 3 1.8 6.2L20 11l-6.2 1.8L12 19l-1.8-6.2L4 11l6.2-1.8L12 3ZM19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z" /></svg>
                            </span>
                            <h3>Your feed starts here</h3>
                            <p>Follow people or share a post to start a conversation.</p>
                            <Link className="button-primary" to="/search">Discover people</Link>
                        </div>
                    ) : (
                        posts.map((post) => {
                            const authorId = getAuthorId(post);

                            const authorPicture =
                                post.author_profile_picture ||
                                post.author?.profile_picture;

                            const authorName = getAuthorName(post);

                            return (
                                <article
                                    className="post-card"
                                    key={post.id}
                                    id={`post-${post.id}`}
                                    tabIndex={-1}
                                >

                                    {/* Post Header */}
                                    <div className="post-header">

                                        <div className="post-user">

                                            <UserAvatar
                                                className="post-author-avatar"
                                                src={authorPicture}
                                                name={authorName}
                                            />

                                            <div className="post-author-info">

                                                <div className="post-name-row">
                                                    <Link
                                                        to={
                                                            authorId
                                                                ? `/users/${authorId}`
                                                                : "/profile"
                                                        }
                                                        className="post-author-name"
                                                    >
                                                        <h4>{authorName}</h4>
                                                    </Link>
                                                    {post.is_pinned && (
                                                        <span className="post-pin-badge" title="Pinned post">Pinned</span>
                                                    )}
                                                    {post.repost_of && (
                                                        <span className="post-repost-badge" title="Repost">Repost</span>
                                                    )}
                                                </div>

                                                <small>
                                                    @{post.author_username || "user"}
                                                    {post.created_at && (
                                                        <>
                                                            {" · "}
                                                            <time dateTime={post.created_at} title={new Date(post.created_at).toLocaleString()}>
                                                                {formatRelativeTime(post.created_at)}
                                                            </time>
                                                        </>
                                                    )}
                                                    {" · "}
                                                    <span className="post-audience-badge">
                                                        {audienceLabels[post.audience] || "Public"}
                                                    </span>
                                                </small>

                                            </div>
                                        </div>
                                    </div>

                                    <div className="post-menu">
                                        <button
                                            type="button"
                                            className="post-menu-trigger"
                                            aria-label="Post options"
                                            aria-haspopup="menu"
                                            aria-controls={`post-menu-${post.id}`}
                                            aria-expanded={openPostMenu === post.id}
                                            onClick={() => setOpenPostMenu((current) => current === post.id ? null : post.id)}
                                        >
                                            <span aria-hidden="true">···</span>
                                        </button>
                                        {openPostMenu === post.id && (
                                            <div
                                                id={`post-menu-${post.id}`}
                                                className="post-menu-panel"
                                                role="menu"
                                                aria-label="Post options"
                                                data-post-menu-panel={post.id}
                                            >
                                                {isMyPost(post) ? (
                                                    <>
                                                        <button type="button" role="menuitem" onClick={() => openEditPost(post)}>Edit post</button>
                                                        <button
                                                            type="button"
                                                            role="menuitem"
                                                            onClick={() => handlePinPost(post)}
                                                            disabled={busyPostId === post.id}
                                                        >
                                                            {busyPostId === post.id ? "Updating..." : post.is_pinned ? "Unpin from profile" : "Pin to profile"}
                                                        </button>
                                                        <button
                                                            type="button"
                                                            role="menuitem"
                                                            className="delete-post-btn"
                                                            onClick={() => {
                                                                setOpenPostMenu(null);
                                                                setPostToDelete(post);
                                                            }}
                                                        >
                                                            Delete post
                                                        </button>
                                                    </>
                                                ) : (
                                                    <>
                                                        <button
                                                            type="button"
                                                            role="menuitem"
                                                            onClick={() => handleRepost(post)}
                                                            disabled={busyPostId === post.id}
                                                        >
                                                            {busyPostId === post.id ? "Reposting..." : "Repost"}
                                                        </button>
                                                        <form onSubmit={(event) => handleReportPost(event, post)}>
                                                            <label htmlFor={`report-reason-${post.id}`}>Report this post</label>
                                                            <textarea
                                                                id={`report-reason-${post.id}`}
                                                                value={reportReasons[post.id] || ""}
                                                                onChange={(event) => setReportReasons((current) => ({
                                                                    ...current,
                                                                    [post.id]: event.target.value,
                                                                }))}
                                                                placeholder="Tell us why..."
                                                                maxLength={250}
                                                                required
                                                            />
                                                            <button type="submit" disabled={reporting || !(reportReasons[post.id] || "").trim()}>
                                                                {reporting ? "Sending..." : "Submit report"}
                                                            </button>
                                                        </form>
                                                    </>
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {/* Post Content */}
                                    {post.content && (
                                        <p className="post-content">
                                            {post.content}
                                        </p>
                                    )}

                                    {(() => {
                                        const images = [...new Set([
                                            post.image,
                                            ...(Array.isArray(post.images) ? post.images : []),
                                        ].filter(Boolean))];
                                        if (!images.length) return null;
                                        const imageSources = images.map(getMediaUrl);
                                        return (
                                            <div className={images.length > 1 ? "post-image-gallery" : "post-image-gallery is-single"}>
                                                {imageSources.map((src, index) => (
                                                    <button
                                                        type="button"
                                                        className="post-image-open"
                                                        key={`${post.id}-${src}`}
                                                        onClick={() => setViewingImage({
                                                            images: imageSources,
                                                            initialIndex: index,
                                                            alt: `Image shared by ${authorName}`,
                                                        })}
                                                        aria-label={`Open post image ${index + 1}`}
                                                    >
                                                        <img
                                                            src={src}
                                                            alt={`Post image ${index + 1} shared by ${authorName}`}
                                                            className="post-media"
                                                            loading="lazy"
                                                        />
                                                    </button>
                                                ))}
                                            </div>
                                        );
                                    })()}

                                    {/* Post Video */}
                                    {post.video && (
                                        <video
                                            controls
                                            preload="metadata"
                                            className="post-media"
                                            src={getMediaUrl(post.video)}
                                        />
                                    )}

                                    {/* Like and Comment */}
                                    <PostActions
                                        post={post}
                                        onPostChange={updatePost}
                                        onShare={() => handleShare(post)}
                                    />

                                </article>
                            );
                        })
                    )}
                    {nextPageUrl && (
                        <div className="feed-load-more" ref={loadMoreRef}>
                            {paginationError && <p className="form-error" role="alert">{paginationError}</p>}
                            <button
                                type="button"
                                className="button-secondary"
                                onClick={loadMorePosts}
                                disabled={loadingMore}
                            >
                                {loadingMore ? "Loading more posts..." : paginationError ? "Try loading more" : "Load more posts"}
                            </button>
                        </div>
                    )}
                </div>
                <ConfirmDialog
                    open={Boolean(postToDelete)}
                    title="Delete this post?"
                    message="This action cannot be undone."
                    confirmLabel="Delete post"
                    danger
                    busy={deletingPost}
                    errorMessage={postToDelete ? error : ""}
                    onCancel={() => setPostToDelete(null)}
                    onConfirm={handleDeletePost}
                />
                {editingPost && (
                    <div
                        className="dialog-backdrop"
                        onMouseDown={(event) => {
                            if (event.target === event.currentTarget && !savingEdit) setEditingPost(null);
                        }}
                    >
                        <section
                            className="post-edit-dialog"
                            role="dialog"
                            aria-modal="true"
                            aria-labelledby="edit-post-title"
                        >
                            <h2 id="edit-post-title">Edit your post</h2>
                            {error && <p className="form-error" role="alert">{error}</p>}
                            <form onSubmit={handleEditPost}>
                                <label htmlFor="edit-post-content">Post text</label>
                                <textarea
                                    id="edit-post-content"
                                    autoFocus
                                    rows={5}
                                    value={editContent}
                                    onChange={(event) => setEditContent(event.target.value)}
                                />
                                <div className="dialog-actions">
                                    <button type="button" className="button-secondary" onClick={() => setEditingPost(null)} disabled={savingEdit}>Cancel</button>
                                    <button type="submit" className="button-primary" disabled={savingEdit}>{savingEdit ? "Saving..." : "Save changes"}</button>
                                </div>
                            </form>
                        </section>
                    </div>
                )}
                {viewingImage && (
                    <MediaViewer
                        images={viewingImage.images}
                        initialIndex={viewingImage.initialIndex ?? 0}
                        alt={viewingImage.alt}
                        onClose={closeMediaViewer}
                    />
                )}
        </section>
    );
}

export default Home;
