
import { useCallback, useEffect, useState } from "react";
import { useLocation, useParams, Link } from "react-router-dom";
import api, { getMediaUrl } from "../api/axios";
import ConfirmDialog from "../components/ConfirmDialog";
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

function UserProfile() {
    const { userId } = useParams();
    const location = useLocation();
    const notice = location.state?.notice;

    const [dismissedNoticeKey, setDismissedNoticeKey] = useState(null);
    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [following, setFollowing] = useState(false);
    const [followLoading, setFollowLoading] = useState(false);
    const [friendAction, setFriendAction] = useState("");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [viewer, setViewer] = useState(null);
    const [coverLoadFailed, setCoverLoadFailed] = useState(false);
    const [blockLoading, setBlockLoading] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);

    const closeViewer = useCallback(() => setViewer(null), []);
    const closeConfirm = useCallback(() => setConfirmAction(null), []);

    const updatePost = useCallback((postId, changes) => {
        setPosts((current) => current.map((post) =>
            post.id === postId ? { ...post, ...changes } : post
        ));
    }, []);

    const currentUserId = Number(localStorage.getItem("user_id"));
    const isOwnProfile = currentUserId === Number(userId);

    const loadProfileData = useCallback(async () => {
        const response = await api.get(`users/${userId}/`);
        let profilePosts = [];
        let profileError = "";
        try {
            const postsResponse = await api.get(`users/${userId}/posts/`);
            const data = postsResponse.data;
            profilePosts = Array.isArray(data) ? data : data.results || [];
        } catch {
            profileError = "Profile loaded, but posts could not be loaded.";
        }
        return {
            user: response.data,
            posts: profilePosts,
            error: profileError,
        };
    }, [userId]);

    useEffect(() => {
        let active = true;
        const load = async () => {
            try {
                const result = await loadProfileData();
                if (!active) return;
                setUser(result.user);
                setFollowing(Boolean(result.user.is_following));
                setPosts(result.posts);
                setError(result.error);
            } catch (requestError) {
                if (!active) return;
                setError(
                    requestError.response?.data?.detail ||
                    "Unable to load this user's profile."
                );
                setUser(null);
                setPosts([]);
            } finally {
                if (active) setLoading(false);
            }
        };
        load();
        return () => {
            active = false;
        };
    }, [loadProfileData]);

    const handleBlock = async () => {
        if (blockLoading) return;
        const wasBlocked = Boolean(user.is_blocked);
        setBlockLoading(true);
        setError("");
        setSuccess("");
        try {
            if (wasBlocked) {
                await api.delete(`social/users/${userId}/block/`);
                setSuccess("User unblocked.");
            } else {
                await api.post(`social/users/${userId}/block/`);
                setSuccess("User blocked.");
            }
            // A blocked user disappears from the public-profile API, so refetching
            // here would turn a successful block into a misleading 404 error and
            // hide the Unblock button. Keep the visible profile state in sync
            // with the mutation result instead.
            setUser((current) =>
                current ? { ...current, is_blocked: !wasBlocked } : current
            );
        } catch (requestError) {
            setError(requestError.response?.data?.detail || "Unable to update block status.");
        } finally {
            setBlockLoading(false);
        }
    };

    const handleFollow = async () => {
        if (!localStorage.getItem("access")) {
            setError("Please login to follow this user.");
            return;
        }

        try {
            setFollowLoading(true);
            setError("");

            if (following) {
                await api.delete(
                    `social/users/${userId}/follow/`
                );
                setFollowing(false);
            } else {
                await api.post(
                    `social/users/${userId}/follow/`
                );
                setFollowing(true);
            }

            const result = await loadProfileData();
            setUser(result.user);
            setFollowing(Boolean(result.user.is_following));
            setPosts(result.posts);
            setError(result.error);
        } catch (err) {
            setError(
                err.response?.data?.detail ||
                "Unable to update follow status."
            );
        } finally {
            setFollowLoading(false);
        }
    };

    const handleFriendAction = async (action) => {
        if (friendAction) return;
        setFriendAction(action);
        setError("");
        setSuccess("");

        try {
            const requestId = user.friend_request_id;
            if (action === "send") {
                await api.post(`social/users/${userId}/friend-request/`);
            } else if (action === "cancel") {
                await api.delete(`social/friend-requests/${requestId}/`);
            } else if (action === "accept" || action === "reject") {
                await api.post(`social/friend-requests/${requestId}/${action}/`);
            } else if (action === "unfriend") {
                await api.delete(`social/friends/${userId}/`);
            }

            const result = await loadProfileData();
            setUser(result.user);
            setFollowing(Boolean(result.user.is_following));
            setPosts(result.posts);
            setError(result.error);
            setSuccess(
                action === "send"
                    ? "Friend request sent."
                    : action === "cancel"
                        ? "Friend request cancelled."
                        : action === "accept"
                            ? "Friend request accepted."
                            : action === "reject"
                                ? "Friend request rejected."
                                : "Friend removed.",
            );
        } catch (requestError) {
            setError(
                requestError.response?.data?.detail ||
                "Unable to update this friendship. Please try again.",
            );
        } finally {
            setFriendAction("");
        }
    };

    const confirmDestructiveAction = async () => {
        if (!confirmAction) return;
        const action = confirmAction;
        try {
            if (action.type === "unfriend") {
                await handleFriendAction("unfriend");
            } else if (action.type === "block") {
                await handleBlock();
            }
        } finally {
            setConfirmAction(null);
        }
    };

    const sharePost = async (post) => {
        const url = `${window.location.origin}/posts/${post.id}`;
        try {
            if (navigator.share) {
                await navigator.share({
                    title: "SocialConnect Post",
                    text: post.content || "Check out this post on SocialConnect.",
                    url,
                });
            } else if (navigator.clipboard?.writeText) {
                await navigator.clipboard.writeText(url);
                setSuccess("Post link copied.");
            } else {
                throw new Error("Link sharing is not available in this browser.");
            }
        } catch (shareError) {
            if (shareError.name !== "AbortError") {
                setError(shareError.message || "Unable to share this post.");
            }
        }
    };

    if (loading) {
        return <p className="profile-message">Loading profile...</p>;
    }

    if (error && !user) {
        return (
            <div className="profile-message">
                <p role="alert">{error}</p>
                <Link to="/">Back to Home</Link>
            </div>
        );
    }

    if (!user) return null;

    const profile = user.profile || {};
    const displayName = [user.first_name, user.last_name].filter(Boolean).join(" ") || user.username;
    const isUnfriendConfirm = confirmAction?.type === "unfriend";

    return (
        <main className="profile-page">

            {notice && dismissedNoticeKey !== location.key && (
                <div className="form-success" role="status">
                    <span>{notice}</span>
                    <button
                        type="button"
                        className="text-button"
                        onClick={() => setDismissedNoticeKey(location.key)}
                        aria-label="Dismiss notice"
                    >
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
            )}
            {success && <div className="form-success" role="status">{success}</div>}
            {error && <div className="form-error" role="alert">{error}</div>}

            <section className="profile-card">

                <div className="profile-cover">
                    {profile.cover_photo && !coverLoadFailed ? (
                        <button
                            type="button"
                            className="profile-cover-open"
                            onClick={() => setViewer({
                                src: getMediaUrl(profile.cover_photo),
                                alt: "Cover photo",
                            })}
                            aria-label="View cover photo"
                        >
                            <img
                                src={getMediaUrl(profile.cover_photo)}
                                alt=""
                                onError={() => setCoverLoadFailed(true)}
                            />
                        </button>
                    ) : (
                        <div className="profile-cover-empty" role="img" aria-label="No cover photo" />
                    )}
                </div>

                <div className="profile-information">

                    <div className="profile-avatar">
                        {profile.profile_picture ? (
                            <button
                                type="button"
                                className="profile-avatar-open"
                                onClick={() => setViewer({
                                    src: getMediaUrl(profile.profile_picture),
                                    alt: `${displayName}'s profile picture`,
                                })}
                                aria-label="View profile picture"
                            >
                                <UserAvatar
                                    className="profile-picture-avatar"
                                    src={profile.profile_picture}
                                    name={displayName}
                                />
                            </button>
                        ) : (
                            <UserAvatar
                                className="profile-picture-avatar"
                                src={profile.profile_picture}
                                name={displayName}
                            />
                        )}
                    </div>

                    <div className="profile-details">
                        <h2>{displayName}</h2>
                        <p className="profile-username">@{user.username}</p>

                        <p className="profile-bio">{profile.bio || "No bio added yet."}</p>

                        {profile.location && (
                            <p className="profile-meta-row">
                                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z" /><circle cx="12" cy="10" r="2.5" /></svg>
                                {profile.location}
                            </p>
                        )}

                        {profile.website && (
                            <p className="profile-meta-row">
                                <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" /><path d="M3 12h18m-9-9a14 14 0 0 1 0 18m0-18a14 14 0 0 0 0 18" /></svg>
                                <a
                                    href={profile.website}
                                    target="_blank"
                                    rel="noreferrer"
                                >
                                    {profile.website}
                                </a>
                            </p>
                        )}
                    </div>

                    {isOwnProfile ? (
                        <Link
                            to="/edit-profile"
                            className="edit-profile-button"
                        >
                            Edit profile
                        </Link>
                    ) : (
                        <div className="profile-actions">
                            {user.friendship_status === "none" && (
                                <button
                                    type="button"
                                    className="button-primary"
                                    onClick={() => handleFriendAction("send")}
                                    disabled={Boolean(friendAction)}
                                >
                                    {friendAction === "send" ? "Sending..." : "Add friend"}
                                </button>
                            )}
                            {user.friendship_status === "outgoing_pending" && (
                                <button
                                    type="button"
                                    className="button-secondary"
                                    onClick={() => handleFriendAction("cancel")}
                                    disabled={Boolean(friendAction)}
                                >
                                    {friendAction === "cancel" ? "Cancelling..." : "Request sent · Cancel"}
                                </button>
                            )}
                            {user.friendship_status === "incoming_pending" && (
                                <>
                                    <button
                                        type="button"
                                        className="button-primary"
                                        onClick={() => handleFriendAction("accept")}
                                        disabled={Boolean(friendAction)}
                                    >
                                        {friendAction === "accept" ? "Accepting..." : "Accept request"}
                                    </button>
                                    <button
                                        type="button"
                                        className="button-secondary"
                                        onClick={() => handleFriendAction("reject")}
                                        disabled={Boolean(friendAction)}
                                    >
                                        {friendAction === "reject" ? "Rejecting..." : "Reject"}
                                    </button>
                                </>
                            )}
                            {user.friendship_status === "friends" && (
                                <>
                                    <span className="friend-status-badge">Friends</span>
                                    <button
                                        type="button"
                                        className="button-secondary"
                                        onClick={() => setConfirmAction({ type: "unfriend" })}
                                        disabled={Boolean(friendAction)}
                                    >
                                        {friendAction === "unfriend" ? "Removing..." : "Unfriend"}
                                    </button>
                                </>
                            )}
                            <button
                                type="button"
                                className={following ? "button-secondary" : "edit-profile-button"}
                                onClick={handleFollow}
                                disabled={followLoading}
                            >
                                {followLoading
                                    ? "Please wait..."
                                    : following
                                        ? "Unfollow"
                                        : "Follow"}
                            </button>
                            {user.can_message && (
                                <Link className="button-secondary" to={`/messages/${userId}`}>Message</Link>
                            )}
                            <button
                                type="button"
                                className="button-secondary"
                                onClick={() => {
                                    if (user.is_blocked) {
                                        handleBlock();
                                    } else {
                                        setConfirmAction({ type: "block" });
                                    }
                                }}
                                disabled={blockLoading}
                            >
                                {blockLoading ? "Please wait..." : user.is_blocked ? "Unblock" : "Block"}
                            </button>
                        </div>
                    )}

                </div>

                <div className="profile-stats">
                    <div>
                        <strong>{user.posts_count ?? posts.length}</strong>
                        <span>Posts</span>
                    </div>

                    {isOwnProfile ? (
                        <>
                            <Link className="profile-stat-link" to="/connections/followers">
                                <strong>{user.followers_count ?? 0}</strong>
                                <span>Followers</span>
                            </Link>
                            <Link className="profile-stat-link" to="/connections/following">
                                <strong>{user.following_count ?? 0}</strong>
                                <span>Following</span>
                            </Link>
                        </>
                    ) : (
                        <>
                            <div>
                                <strong>{user.followers_count ?? 0}</strong>
                                <span>Followers</span>
                            </div>
                            <div>
                                <strong>{user.following_count ?? 0}</strong>
                                <span>Following</span>
                            </div>
                        </>
                    )}
                </div>

            </section>

            <section className="profile-posts">
                <h3>{user.username}'s Posts</h3>

                {posts.length === 0 ? (
                    <p>No posts available.</p>
                ) : (
                    <div className="posts-container">
                        {posts.map((post) => {
                            const images = getPostImages(post);
                            const authorId = getAuthorId(post);
                            const authorName = [post.author_first_name, post.author_last_name]
                                .filter(Boolean).join(" ")
                                || post.author_full_name
                                || post.author?.username
                                || post.author_username
                                || displayName;

                            return (
                                <article className="post-card" key={post.id}>
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
                                                    @{post.author_username || user.username}
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
                                            aria-label={`Open post by ${authorName}`}
                                        >
                                            View post
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
                                                    onClick={() => setViewer({
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
            </section>

            <ConfirmDialog
                open={Boolean(confirmAction)}
                title={isUnfriendConfirm ? "Remove this friend?" : "Block this user?"}
                message={isUnfriendConfirm
                    ? "They will be removed from your friends list. You can send a new request later."
                    : "They will no longer be able to interact with you. You can unblock them later."}
                confirmLabel={isUnfriendConfirm ? "Remove friend" : "Block user"}
                danger
                busy={friendAction === "unfriend" || blockLoading}
                errorMessage={confirmAction ? error : ""}
                onCancel={closeConfirm}
                onConfirm={confirmDestructiveAction}
            />

            {viewer && (
                <MediaViewer
                    images={viewer.images}
                    initialIndex={viewer.initialIndex ?? 0}
                    alt={viewer.alt}
                    onClose={closeViewer}
                />
            )}
        </main>
    );
}

export default UserProfile;
