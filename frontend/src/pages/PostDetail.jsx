import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { getMediaUrl } from "../api/axios";
import PostActions from "../components/PostActions";
import MediaViewer from "../components/MediaViewer";
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

function PostDetail() {
    const { postId } = useParams();
    const requestRef = useRef(null);
    const loadedPostIdRef = useRef(null);
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [notice, setNotice] = useState("");
    const [viewingImage, setViewingImage] = useState(null);
    const closeMediaViewer = useCallback(() => setViewingImage(null), []);

    const fetchPost = useCallback(async () => {
        requestRef.current?.abort();
        const controller = new AbortController();
        requestRef.current = controller;
        try {
            const response = await api.get(`posts/${postId}/`, {
                signal: controller.signal,
            });
            if (controller.signal.aborted) return;
            setPost(response.data);
            setError("");
        } catch (requestError) {
            if (controller.signal.aborted || requestError.code === "ERR_CANCELED") return;
            setError(
                requestError.response?.status === 404
                    ? "This post could not be found."
                    : "Unable to load this post. Please try again."
            );
        } finally {
            if (!controller.signal.aborted) setLoading(false);
        }
    }, [postId]);

    useEffect(() => {
        if (loadedPostIdRef.current === postId) return undefined;
        loadedPostIdRef.current = postId;
        fetchPost();
        return () => {
            // StrictMode remounts the effect after cleanup; allow the retry.
            loadedPostIdRef.current = null;
            requestRef.current?.abort();
        };
    }, [fetchPost, postId]);

    const sharePost = async () => {
        const url = window.location.href;
        try {
            if (navigator.share) {
                await navigator.share({
                    title: "SocialConnect post",
                    text: post.content || "View this post on SocialConnect.",
                    url,
                });
            } else if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(url);
                setNotice("Post link copied.");
            } else {
                throw new Error("Link sharing is not available in this browser.");
            }
        } catch (shareError) {
            if (shareError.name !== "AbortError") setError(shareError.message);
        }
    };

    if (loading) {
        return <section className="post-detail-page"><div className="post-skeleton" role="status" aria-label="Loading post" /></section>;
    }

    if (error && !post) {
        return (
            <section className="post-detail-page">
                <div className="empty-state">
                    <h1>Post unavailable</h1>
                    <p role="alert">{error}</p>
                    <button
                        className="button-secondary"
                        type="button"
                        onClick={() => {
                            setLoading(true);
                            fetchPost();
                        }}
                    >
                        Try again
                    </button>
                </div>
            </section>
        );
    }

    if (!post) return null;

    const authorId = getAuthorId(post);
    const authorName = [post.author_first_name, post.author_last_name].filter(Boolean).join(" ")
        || post.author_full_name
        || post.author?.username
        || post.author_username
        || "SocialConnect member";
    const images = getPostImages(post);

    return (
        <section className="post-detail-page">
            <header className="post-detail-heading">
                <div>
                    <p className="page-eyebrow">SHARED POST</p>
                    <h1>Post</h1>
                    <p className="post-detail-subtitle">Shared by {authorName}</p>
                </div>
                <Link to="/" className="button-secondary">Back to home</Link>
            </header>
            {error && <p className="form-error" role="alert">{error}</p>}
            {notice && <p className="form-success" role="status">{notice}</p>}
            <article className="post-card">
                <div className="post-header">
                    <div className="post-user">
                        <UserAvatar
                            className="post-author-avatar"
                            src={post.author_profile_picture}
                            name={authorName}
                        />
                        <div className="post-author-info">
                            <div className="post-name-row">
                                <Link
                                    to={authorId ? `/users/${authorId}` : "/profile"}
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
                                    alt: `Image shared by ${authorName}`,
                                })}
                                aria-label={`Open post image ${index + 1}`}
                            >
                                <img
                                    className="post-media"
                                    src={src}
                                    alt={`Post image ${index + 1} shared by ${authorName}`}
                                    loading="lazy"
                                />
                            </button>
                        ))}
                    </div>
                )}
                {post.video && (
                    <video
                        className="post-media"
                        src={getMediaUrl(post.video)}
                        controls
                        preload="metadata"
                    />
                )}
                <PostActions
                    post={post}
                    onShare={sharePost}
                    onPostChange={(_postId, changes) => setPost((current) => ({ ...current, ...changes }))}
                />
            </article>
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

export default PostDetail;
