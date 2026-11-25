import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import api, { getMediaUrl } from "../api/axios";
import MediaViewer from "../components/MediaViewer";
import PostActions from "../components/PostActions";
import UserAvatar from "../components/UserAvatar";

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

const getPostImages = (post) => [...new Set([
    post.image,
    ...(Array.isArray(post.images) ? post.images : []),
].filter(Boolean))].map(getMediaUrl);

const getAuthorId = (post) => {
    if (post.author_id) return post.author_id;
    if (post.author && typeof post.author === "object") return post.author.id;
    return post.author;
};

function Bookmarks() {
    const requestRef = useRef(null);
    const initialLoadRef = useRef(false);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState("");
    const [feedbackError, setFeedbackError] = useState("");
    const [notice, setNotice] = useState("");
    const [viewingImage, setViewingImage] = useState(null);
    const closeMediaViewer = useCallback(() => setViewingImage(null), []);

    const loadBookmarks = useCallback(async () => {
        requestRef.current?.abort();
        const controller = new AbortController();
        requestRef.current = controller;
        try {
            const response = await api.get("posts/?bookmarked=true", {
                signal: controller.signal,
            });
            if (controller.signal.aborted) return;
            const data = response.data;
            setPosts(Array.isArray(data) ? data : data.results || []);
            setLoadError("");
        } catch (requestError) {
            if (requestError.code === "ERR_CANCELED" || controller.signal.aborted) return;
            setLoadError("Unable to load your bookmarks. Please try again.");
        } finally {
            if (!controller.signal.aborted) setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (initialLoadRef.current) return undefined;
        initialLoadRef.current = true;
        loadBookmarks();
        return () => {
            // StrictMode remounts the effect after cleanup; allow the retry.
            initialLoadRef.current = false;
            requestRef.current?.abort();
        };
    }, [loadBookmarks]);

    const updatePost = (postId, changes) => {
        if (changes.is_bookmarked === false) {
            setPosts((current) => current.filter((post) => post.id !== postId));
            return;
        }
        setPosts((current) => current.map((post) =>
            post.id === postId ? { ...post, ...changes } : post
        ));
    };

    const refreshBookmarks = () => {
        setLoading(true);
        setFeedbackError("");
        loadBookmarks();
    };

    const sharePost = async (post) => {
        const url = `${window.location.origin}/posts/${post.id}`;
        try {
            if (navigator.share) {
                await navigator.share({
                    title: "SocialConnect Post",
                    text: post.content || "Check out this post!",
                    url,
                });
            } else if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(url);
                setNotice("Post link copied.");
            } else {
                throw new Error("Link sharing is not available in this browser.");
            }
        } catch (shareError) {
            if (shareError.name !== "AbortError") {
                setFeedbackError(shareError.message || "Unable to share this post.");
            }
        }
    };

    return (
        <section className="bookmarks-page">
            <header className="feed-header">
                <div>
                    <p className="page-eyebrow">SAVED FOR LATER</p>
                    <h1>Bookmarks</h1>
                </div>
                <button type="button" className="button-secondary" onClick={refreshBookmarks} disabled={loading}>
                    {loading ? "Refreshing..." : "Refresh"}
                </button>
            </header>
            {loadError && (posts.length > 0 ? (
                <p className="form-error" role="alert">{loadError}</p>
            ) : (
                <div className="empty-state">
                    <p role="alert">{loadError}</p>
                    <button type="button" className="button-secondary" onClick={refreshBookmarks}>Try again</button>
                </div>
            ))}
            {feedbackError && <p className="form-error" role="alert">{feedbackError}</p>}
            {notice && <p className="form-success" role="status">{notice}</p>}
            {loading ? (
                <div className="feed-skeletons" role="status" aria-label="Loading bookmarks">
                    {[1, 2].map((item) => <div className="post-skeleton" key={item} />)}
                </div>
            ) : !loadError && posts.length === 0 ? (
                <div className="empty-state">
                    <h2>No bookmarks yet</h2>
                    <p>Save a post from your feed and it will be waiting here.</p>
                    <Link to="/" className="button-primary">Browse your feed</Link>
                </div>
            ) : (
                <div className="posts-container">
                    {posts.map((post) => {
                        const authorId = getAuthorId(post);
                        const images = getPostImages(post);
                        const name = [post.author_first_name, post.author_last_name]
                            .filter(Boolean).join(" ")
                            || post.author_full_name
                            || post.author?.username
                            || post.author_username
                            || "SocialConnect member";

                        return (
                            <article className="post-card" key={post.id}>
                                <div className="post-header">
                                    <div className="post-user">
                                        <UserAvatar
                                            className="post-author-avatar"
                                            src={post.author_profile_picture}
                                            name={name}
                                        />
                                        <div className="post-author-info">
                                            <div className="post-name-row">
                                                <Link
                                                    className="post-author-name"
                                                    to={authorId ? `/users/${authorId}` : "/"}
                                                >
                                                    <h4>{name}</h4>
                                                </Link>
                                                {post.is_pinned && (
                                                    <span className="post-pin-badge" title="Pinned post">Pinned</span>
                                                )}
                                                {post.repost_of && (
                                                    <span className="post-repost-badge" title="Repost">Repost</span>
                                                )}
                                            </div>
                                            <small>
                                                @{post.author_username || "member"}
                                                {post.created_at && (
                                                    <>
                                                        {" · "}
                                                        <time
                                                            dateTime={post.created_at}
                                                            title={new Date(post.created_at).toLocaleString()}
                                                        >
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
                                    <Link
                                        className="post-permalink"
                                        to={`/posts/${post.id}`}
                                        aria-label={`Open post by ${name}`}
                                    >
                                        Open post
                                    </Link>
                                </div>
                                {post.content && <p className="post-content">{post.content}</p>}
                                {images.length > 0 && (
                                    <div className={images.length > 1 ? "post-image-gallery" : "post-image-gallery is-single"}>
                                        {images.map((src, index) => (
                                            <button
                                                type="button"
                                                className="post-image-open"
                                                key={`${post.id}-${src}`}
                                                onClick={() => setViewingImage({
                                                    images,
                                                    initialIndex: index,
                                                    alt: `Image shared by ${name}`,
                                                })}
                                                aria-label={`Open post image ${index + 1}`}
                                            >
                                                <img
                                                    className="post-media"
                                                    src={src}
                                                    alt={`Post image ${index + 1} shared by ${name}`}
                                                    loading="lazy"
                                                />
                                            </button>
                                        ))}
                                    </div>
                                )}
                                {post.video && (
                                    <video
                                        className="post-media"
                                        controls
                                        preload="metadata"
                                        src={getMediaUrl(post.video)}
                                    />
                                )}
                                <PostActions
                                    post={post}
                                    onPostChange={updatePost}
                                    onShare={() => sharePost(post)}
                                />
                            </article>
                        );
                    })}
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

export default Bookmarks;
