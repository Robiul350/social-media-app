import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import api from "../api/axios";
import ConfirmDialog from "./ConfirmDialog";
import UserAvatar from "./UserAvatar";

function responseItems(data) {
    return Array.isArray(data) ? data : data?.results || [];
}

function PostActions({ post, onPostChange, onShare }) {
    const liked = Boolean(post.is_liked);
    const likeCount = post.like_count ?? 0;
    const bookmarked = Boolean(post.is_bookmarked);
    const [bookmarkBusy, setBookmarkBusy] = useState(false);
    const [comments, setComments] = useState([]);
    const [commentsLoaded, setCommentsLoaded] = useState(false);
    const [commentsLoading, setCommentsLoading] = useState(false);
    const [showComments, setShowComments] = useState(false);
    const [commentText, setCommentText] = useState("");
    const [replyingTo, setReplyingTo] = useState(null);
    const [replyText, setReplyText] = useState("");
    const [sendingComment, setSendingComment] = useState(false);
    const [likeBusy, setLikeBusy] = useState(false);
    const [error, setError] = useState("");
    const [editingComment, setEditingComment] = useState(null);
    const [editContent, setEditContent] = useState("");
    const [savingEdit, setSavingEdit] = useState(false);
    const [commentToDelete, setCommentToDelete] = useState(null);
    const [deletingComment, setDeletingComment] = useState(false);
    const currentUserId = Number(localStorage.getItem("user_id"));
    const commentsRequestRef = useRef(null);

    const fetchComments = useCallback(async () => {
        commentsRequestRef.current?.abort();
        const controller = new AbortController();
        commentsRequestRef.current = controller;
        setCommentsLoading(true);
        try {
            const response = await api.get(`social/posts/${post.id}/comments/`, {
                signal: controller.signal,
            });
            const items = responseItems(response.data);
            setComments(items);
            setCommentsLoaded(true);
            onPostChange?.(post.id, { comment_count: items.length });
        } catch (requestError) {
            if (requestError.code !== "ERR_CANCELED" && !controller.signal.aborted) {
                setError("Unable to load comments for this post.");
            }
        } finally {
            if (!controller.signal.aborted) setCommentsLoading(false);
        }
    }, [onPostChange, post.id]);

    useEffect(() => {
        return () => {
            commentsRequestRef.current?.abort();
        };
    }, []);

    const toggleComments = () => {
        if (showComments) {
            setShowComments(false);
            return;
        }
        setShowComments(true);
        if (!commentsLoaded) fetchComments();
    };

    const handleLike = async () => {
        if (!localStorage.getItem("access") || likeBusy) {
            if (!localStorage.getItem("access")) setError("Log in to like this post.");
            return;
        }

        const previousLiked = Boolean(post.is_liked);
        const previousCount = post.like_count ?? 0;
        const nextLiked = !previousLiked;
        const nextCount = Math.max(0, previousCount + (nextLiked ? 1 : -1));
        setLikeBusy(true);
        setError("");
        onPostChange?.(post.id, { is_liked: nextLiked, like_count: nextCount });
        try {
            const response = await api.post(`social/posts/${post.id}/like/`);
            const updatedCount = response.data.like_count ?? likeCount;
            onPostChange?.(post.id, {
                is_liked: Boolean(response.data.liked),
                like_count: updatedCount,
            });
        } catch {
            onPostChange?.(post.id, {
                is_liked: previousLiked,
                like_count: previousCount,
            });
            setError("Unable to update your like. Please try again.");
        } finally {
            setLikeBusy(false);
        }
    };

    const handleBookmark = async () => {
        if (bookmarkBusy) return;
        setBookmarkBusy(true);
        setError("");
        try {
            const response = await api.post(`posts/${post.id}/bookmark/`);
            onPostChange?.(post.id, { is_bookmarked: Boolean(response.data.bookmarked) });
        } catch {
            setError("Unable to update your bookmark. Please try again.");
        } finally {
            setBookmarkBusy(false);
        }
    };

    const handleComment = async (event, parentId = null, content = commentText) => {
        event.preventDefault();
        if (!localStorage.getItem("access")) {
            setError("Log in to comment on this post.");
            return;
        }
        const trimmedContent = content.trim();
        if (!trimmedContent || sendingComment) return;

        setSendingComment(true);
        setError("");
        try {
            await api.post(`social/posts/${post.id}/comments/`, {
                content: trimmedContent,
                ...(parentId ? { parent: parentId } : {}),
            });
            if (parentId) {
                setReplyingTo(null);
                setReplyText("");
            } else {
                setCommentText("");
            }
            setShowComments(true);
            await fetchComments();
        } catch {
            setError("Unable to add your comment. Please try again.");
        } finally {
            setSendingComment(false);
        }
    };

    const saveComment = async (event) => {
        event.preventDefault();
        if (!editingComment || !editContent.trim()) return;

        setSavingEdit(true);
        setError("");
        try {
            await api.patch(`social/comments/${editingComment.id}/`, {
                content: editContent.trim(),
            });
            setEditingComment(null);
            setEditContent("");
            await fetchComments();
        } catch {
            setError("Unable to edit this comment.");
        } finally {
            setSavingEdit(false);
        }
    };

    const deleteComment = async () => {
        if (!commentToDelete) return;
        setDeletingComment(true);
        setError("");
        try {
            await api.delete(`social/comments/${commentToDelete.id}/`);
            setCommentToDelete(null);
            await fetchComments();
        } catch {
            setError("Unable to delete this comment.");
        } finally {
            setDeletingComment(false);
        }
    };

    const commentsByParent = useMemo(() => {
        const grouped = new Map();
        comments.forEach((comment) => {
            const parentKey = comment.parent == null ? null : String(comment.parent);
            const children = grouped.get(parentKey) || [];
            children.push(comment);
            grouped.set(parentKey, children);
        });
        return grouped;
    }, [comments]);

    const renderComment = (comment, ancestors = new Set()) => {
        const commentKey = String(comment.id);
        if (ancestors.has(commentKey)) return null;

        const nextAncestors = new Set(ancestors);
        nextAncestors.add(commentKey);
        const children = commentsByParent.get(commentKey) || [];
        const isOwner = Number(comment.user) === currentUserId;
        const isEditing = editingComment?.id === comment.id;
        const isReplying = replyingTo?.id === comment.id;

        return (
            <article className="comment-item" key={comment.id}>
                <UserAvatar
                    className="comment-avatar"
                    src={comment.profile_picture}
                    name={comment.username || "Member"}
                />
                <div className="comment-body">
                    <div className="comment-content">
                        <strong>{comment.username || "Member"}</strong>
                        {isEditing ? (
                            <form className="comment-edit-form" onSubmit={saveComment}>
                                <label className="sr-only" htmlFor={`edit-comment-${comment.id}`}>Edit comment</label>
                                <input
                                    id={`edit-comment-${comment.id}`}
                                    autoFocus
                                    value={editContent}
                                    onChange={(event) => setEditContent(event.target.value)}
                                />
                                <button type="submit" disabled={savingEdit || !editContent.trim()}>
                                    {savingEdit ? "Saving..." : "Save"}
                                </button>
                                <button type="button" onClick={() => setEditingComment(null)} disabled={savingEdit}>
                                    Cancel
                                </button>
                            </form>
                        ) : (
                            <p>{comment.content}</p>
                        )}
                    </div>

                    {isReplying && (
                        <form
                            className="comment-form comment-reply-form"
                            onSubmit={(event) => handleComment(event, comment.id, replyText)}
                        >
                            <label className="sr-only" htmlFor={`reply-comment-${comment.id}`}>
                                Reply to {comment.username || "comment"}
                            </label>
                            <input
                                id={`reply-comment-${comment.id}`}
                                autoFocus
                                value={replyText}
                                onChange={(event) => setReplyText(event.target.value)}
                                placeholder={`Reply to ${comment.username || "comment"}...`}
                                maxLength={5000}
                            />
                            <button type="submit" className="button-secondary" disabled={sendingComment || !replyText.trim()}>
                                {sendingComment ? "Sending..." : "Reply"}
                            </button>
                        </form>
                    )}

                    {children.length > 0 && (
                        <div className="comment-replies">
                            {children.map((child) => renderComment(child, nextAncestors))}
                        </div>
                    )}
                </div>

                <div className="comment-controls">
                    <button
                        type="button"
                        className="comment-reply-button"
                        aria-expanded={isReplying}
                        onClick={() => {
                            setReplyingTo(isReplying ? null : comment);
                            setReplyText("");
                            setError("");
                        }}
                    >
                        {isReplying ? "Cancel" : "Reply"}
                    </button>
                    {isOwner && !isEditing && (
                        <>
                            <button
                                type="button"
                                onClick={() => {
                                    setEditingComment(comment);
                                    setEditContent(comment.content || "");
                                }}
                            >
                                Edit
                            </button>
                            <button
                                type="button"
                                className="comment-delete-button"
                                onClick={() => {
                                    setError("");
                                    setCommentToDelete(comment);
                                }}
                            >
                                Delete
                            </button>
                        </>
                    )}
                </div>
            </article>
        );
    };

    const displayedCommentCount = commentsLoaded ? comments.length : (post.comment_count ?? 0);

    return (
        <div className="post-actions">
            <div className="post-action-buttons">
                <button
                    type="button"
                    className={liked ? "post-like-button is-liked" : "post-like-button"}
                    onClick={handleLike}
                    disabled={likeBusy}
                    aria-pressed={liked}
                >
                    {likeBusy ? "Updating..." : liked ? "♥ Liked" : "♡ Like"}
                </button>
                <span>{likeCount} {likeCount === 1 ? "Like" : "Likes"}</span>
                <button
                    type="button"
                    className="comments-toggle"
                    onClick={toggleComments}
                    aria-expanded={showComments}
                >
                    {displayedCommentCount} {displayedCommentCount === 1 ? "Comment" : "Comments"}
                </button>
                <span>{post.share_count ?? 0} {post.share_count === 1 ? "Share" : "Shares"}</span>
                <button type="button" className="post-share-button" onClick={onShare}>
                    Share
                </button>
                <button
                    type="button"
                    className={bookmarked ? "post-bookmark-button is-bookmarked" : "post-bookmark-button"}
                    onClick={handleBookmark}
                    disabled={bookmarkBusy}
                    aria-pressed={bookmarked}
                >
                    {bookmarkBusy ? "Saving..." : bookmarked ? "Bookmarked" : "Bookmark"}
                </button>
            </div>

            <form className="comment-form" onSubmit={handleComment}>
                <label className="sr-only" htmlFor={`comment-${post.id}`}>Write a comment</label>
                <input
                    id={`comment-${post.id}`}
                    type="text"
                    placeholder="Write a comment..."
                    value={commentText}
                    onChange={(event) => setCommentText(event.target.value)}
                />
                <button type="submit" className="button-secondary" disabled={sendingComment || !commentText.trim()}>
                    {sendingComment ? "Sending..." : "Comment"}
                </button>
            </form>

            {error && <p className="post-error" role="alert">{error}</p>}

            {showComments && (
                <div className="comment-list" aria-live="polite">
                    {commentsLoading ? (
                        <p className="comment-loading" role="status">Loading comments...</p>
                    ) : (commentsByParent.get(null) || []).map((comment) => renderComment(comment))}
                    {!commentsLoading && !comments.length && <p className="comment-loading">No comments yet.</p>}
                </div>
            )}

            <ConfirmDialog
                open={Boolean(commentToDelete)}
                title="Delete this comment?"
                message="This action cannot be undone."
                confirmLabel="Delete comment"
                danger
                busy={deletingComment}
                errorMessage={commentToDelete ? error : ""}
                onCancel={() => setCommentToDelete(null)}
                onConfirm={deleteComment}
            />
        </div>
    );
}

export default PostActions;
