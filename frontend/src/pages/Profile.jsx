
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { getMediaUrl } from "../api/axios";

function Profile() {
    const { userId: routeUserId } = useParams();
    const userId = routeUserId || localStorage.getItem("user_id");

    const [user, setUser] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [following, setFollowing] = useState(false);
    const [error, setError] = useState("");
    const [followLoading, setFollowLoading] = useState(false);

    const currentUserId = Number(localStorage.getItem("user_id"));
    const isOwnProfile = currentUserId === Number(userId);

    const fetchProfile = useCallback(async () => {
        try {
            setLoading(true);
            setError("");

            // Fetch user profile
            const response = await api.get(
                isOwnProfile ? "users/profile/" : `users/${userId}/`
            );

            const userData = response.data.user || response.data;

            setUser(userData);
            setFollowing(Boolean(userData.is_following));

            // Fetch user's posts
            const postsResponse = await api.get(
                `users/${userId}/posts/`
            );

            const postsData = postsResponse.data;

            setPosts(
                Array.isArray(postsData)
                    ? postsData
                    : postsData.results || []
            );

        } catch (err) {
            console.error("Profile Error:", err.response?.data || err);

            setError(
                err.response?.data?.detail ||
                "Unable to load profile."
            );
        } finally {
            setLoading(false);
        }
    }, [userId, isOwnProfile]);

    useEffect(() => {
    const loadProfile = async () => {
        await fetchProfile();
    };

    loadProfile();
}, [fetchProfile]);

    const handleFollow = async () => {
        if (!user || followLoading) return;

        if (!localStorage.getItem("access")) {
            setError("Please login to follow this user.");
            return;
        }

        try {
            setFollowLoading(true);
            setError("");

            if (following) {
                await api.delete(
                    `social/users/${user.id}/follow/`
                );
            } else {
                await api.post(
                    `social/users/${user.id}/follow/`
                );
            }

            // Get updated follow status and counts from backend
            await fetchProfile();

        } catch (err) {
            console.error("Follow Error:", err.response?.data || err);

            setError(
                err.response?.data?.detail ||
                "Follow action failed."
            );
        } finally {
            setFollowLoading(false);
        }
    };

    if (loading) {
        return <h3>Loading Profile...</h3>;
    }

    if (error && !user) {
        return <h3>{error}</h3>;
    }

    if (!user) {
        return <h3>User not found.</h3>;
    }

    const profile = user.profile || {};

    const profileImage =
        profile.profile_picture || user.profile_picture;

    const coverImage =
        profile.cover_photo || user.cover_photo;

    return (
        <div className="profile-container">

            {error && (
                <p className="error-message">{error}</p>
            )}

            <div className="profile-header">

                <div className="profile-cover">
                    {coverImage && (
                        <img
                            src={getMediaUrl(coverImage)}
                            alt="Cover"
                        />
                    )}
                </div>

                <div className="profile-image">
                    {profileImage ? (
                        <img
                            src={getMediaUrl(profileImage)}
                            alt="Profile"
                        />
                    ) : (
                        <div className="default-avatar">
                            {user.username?.charAt(0).toUpperCase()}
                        </div>
                    )}
                </div>

                <div className="profile-info">

                    <h2>
                        {user.first_name || user.username}
                        {user.last_name ? ` ${user.last_name}` : ""}
                    </h2>

                    <p>@{user.username}</p>

                    <p>
                        {profile.bio || user.bio || "No bio available."}
                    </p>

                    {profile.location && (
                        <p>{profile.location}</p>
                    )}

                    {profile.website && (
                        <a
                            href={profile.website}
                            target="_blank"
                            rel="noreferrer"
                        >
                            {profile.website}
                        </a>
                    )}

                    <div className="profile-stats">

                        <span>
                            <strong>
                                {user.posts_count ?? posts.length}
                            </strong>
                            Posts
                        </span>

                        <span>
                            <strong>
                                {user.followers_count ?? 0}
                            </strong>
                            Followers
                        </span>

                        <span>
                            <strong>
                                {user.following_count ?? 0}
                            </strong>
                            Following
                        </span>

                    </div>

                    {isOwnProfile ? (
                        <Link
                            to="/profile"
                            className="follow-btn"
                        >
                            Edit Profile
                        </Link>
                    ) : (
                        <button
                            onClick={handleFollow}
                            disabled={followLoading}
                            className="follow-btn"
                        >
                            {followLoading
                                ? "Please wait..."
                                : following
                                    ? "Unfollow"
                                    : "Follow"}
                        </button>
                    )}

                </div>

            </div>

            <hr />

            <h3 className="posts-heading">Posts</h3>

            <div className="profile-posts">

                {posts.length === 0 ? (
                    <p>No posts yet.</p>
                ) : (
                    posts.map((post) => (
                        <div
                            className="profile-post"
                            key={post.id}
                        >

                            <p>{post.content}</p>

                            {post.image && (
                                <img
                                    src={getMediaUrl(post.image)}
                                    alt="Post"
                                />
                            )}

                            {post.video && (
                                <video controls>
                                    <source
                                        src={getMediaUrl(post.video)}
                                        type="video/mp4"
                                    />
                                </video>
                            )}

                        </div>
                    ))
                )}

            </div>

            <Link to="/">Back to Home</Link>

        </div>
    );
}

export default Profile;
