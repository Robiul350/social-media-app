
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { getMediaUrl } from "../api/axios";

function EditProfile() {
    const navigate = useNavigate();
    const profilePreviewRef = useRef("");
    const coverPreviewRef = useRef("");
    const profileInputRef = useRef(null);
    const coverInputRef = useRef(null);

    const [formData, setFormData] = useState({
        first_name: "",
        last_name: "",
        bio: "",
        location: "",
        website: "",
        is_private: false,
        allow_comments: "everyone",
        allow_messages: "everyone",
    });

    const [profilePicture, setProfilePicture] = useState(null);
    const [coverPhoto, setCoverPhoto] = useState(null);
    const [profilePictureUrl, setProfilePictureUrl] = useState("");
    const [coverPhotoUrl, setCoverPhotoUrl] = useState("");
    const [removeProfilePicture, setRemoveProfilePicture] = useState(false);
    const [removeCoverPhoto, setRemoveCoverPhoto] = useState(false);
    const [loading, setLoading] = useState(false);
    const [loadingProfile, setLoadingProfile] = useState(true);
    const [error, setError] = useState("");
    const [profileLoadError, setProfileLoadError] = useState("");

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await api.get("users/profile/");
                const data = response.data;
                const profile = data.profile || {};
                setProfilePictureUrl(profile.profile_picture || "");
                setCoverPhotoUrl(profile.cover_photo || "");

                setFormData({
                    first_name: data.first_name || "",
                    last_name: data.last_name || "",
                    bio: profile.bio || "",
                    location: profile.location || "",
                    website: profile.website || "",
                    is_private: Boolean(profile.is_private),
                    allow_comments: profile.allow_comments || "everyone",
                    allow_messages: profile.allow_messages || "everyone",
                });
            } catch (error) {
                setProfileLoadError(error.response?.data?.detail || "Unable to load your profile.");
            } finally {
                setLoadingProfile(false);
            }
        };

        fetchProfile();
    }, []);

    useEffect(() => () => {
        if (profilePreviewRef.current) URL.revokeObjectURL(profilePreviewRef.current);
        if (coverPreviewRef.current) URL.revokeObjectURL(coverPreviewRef.current);
    }, []);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const data = new FormData();

            Object.keys(formData).forEach((key) => {
                data.append(key, formData[key]);
            });

            if (profilePicture) {
                data.append("profile_picture", profilePicture);
            }

            if (coverPhoto) {
                data.append("cover_photo", coverPhoto);
            }
            if (removeProfilePicture) {
                data.append("remove_profile_picture", "true");
            }
            if (removeCoverPhoto) {
                data.append("remove_cover_photo", "true");
            }

            await api.patch("users/profile/", data);
            window.dispatchEvent(new Event("socialconnect:profile-change"));

            navigate("/profile", {
                replace: true,
                state: { notice: "Profile updated successfully." },
            });

        } catch (error) {
            const responseData = error.response?.data;
            const messages = responseData && typeof responseData === "object"
                ? Object.values(responseData).flat().filter((value) => typeof value === "string")
                : [];
            setError(messages[0] || "Unable to update your profile. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleImageChange = (event, type) => {
        const file = event.target.files[0];
        if (!file) return;

        const maxSizeMb = type === "profile" ? 5 : 10;
        if (!file.type.startsWith("image/") || file.size > maxSizeMb * 1024 * 1024) {
            setError(`Choose an image no larger than ${maxSizeMb} MB.`);
            event.target.value = "";
            return;
        }

        setError("");
        const previewRef = type === "profile" ? profilePreviewRef : coverPreviewRef;
        if (previewRef.current) URL.revokeObjectURL(previewRef.current);
        previewRef.current = URL.createObjectURL(file);

        if (type === "profile") {
            setProfilePicture(file);
            setProfilePictureUrl(previewRef.current);
            setRemoveProfilePicture(false);
        } else {
            setCoverPhoto(file);
            setCoverPhotoUrl(previewRef.current);
            setRemoveCoverPhoto(false);
        }
    };

    const removeImage = (type) => {
        const isProfilePicture = type === "profile";
        const previewRef = isProfilePicture ? profilePreviewRef : coverPreviewRef;
        if (previewRef.current) {
            URL.revokeObjectURL(previewRef.current);
            previewRef.current = "";
        }
        (isProfilePicture ? profileInputRef : coverInputRef).current.value = "";

        if (isProfilePicture) {
            setProfilePicture(null);
            setProfilePictureUrl("");
            setRemoveProfilePicture(true);
        } else {
            setCoverPhoto(null);
            setCoverPhotoUrl("");
            setRemoveCoverPhoto(true);
        }
    };

    return (
        <section className="edit-profile-container">
            <h1>Edit profile</h1>

            {loadingProfile ? (
                <p role="status">Loading your profile...</p>
            ) : profileLoadError ? (
                <div className="form-error" role="alert">
                    <p>{profileLoadError}</p>
                    <p>Reload the page to try again before editing.</p>
                </div>
            ) : (
                <>
                    {error && <p className="form-error" role="alert">{error}</p>}

                    <form onSubmit={handleSubmit}>
                        <label htmlFor="edit-first-name">First name</label>
                        <input id="edit-first-name" type="text" name="first_name" autoComplete="given-name" value={formData.first_name} onChange={handleChange} />

                        <label htmlFor="edit-last-name">Last name</label>
                        <input id="edit-last-name" type="text" name="last_name" autoComplete="family-name" value={formData.last_name} onChange={handleChange} />

                        <label htmlFor="edit-bio">Bio</label>
                        <textarea id="edit-bio" name="bio" value={formData.bio} onChange={handleChange} />

                        <label htmlFor="edit-location">Location</label>
                        <input id="edit-location" type="text" name="location" value={formData.location} onChange={handleChange} />

                        <label htmlFor="edit-website">Website</label>
                        <input id="edit-website" type="url" name="website" value={formData.website} onChange={handleChange} />

                        <label htmlFor="edit-private-profile">
                            <input
                                id="edit-private-profile"
                                type="checkbox"
                                name="is_private"
                                checked={formData.is_private}
                                onChange={(event) => setFormData({ ...formData, is_private: event.target.checked })}
                            />
                            Private profile
                        </label>

                        <label htmlFor="edit-comment-policy">Who can comment</label>
                        <select id="edit-comment-policy" name="allow_comments" value={formData.allow_comments} onChange={handleChange}>
                            <option value="everyone">Everyone</option>
                            <option value="followers">Followers</option>
                            <option value="friends">Friends</option>
                            <option value="nobody">Nobody</option>
                        </select>

                        <label htmlFor="edit-message-policy">Who can message</label>
                        <select id="edit-message-policy" name="allow_messages" value={formData.allow_messages} onChange={handleChange}>
                            <option value="everyone">Everyone</option>
                            <option value="followers">Followers</option>
                            <option value="friends">Friends</option>
                            <option value="nobody">Nobody</option>
                        </select>

                        <label htmlFor="edit-profile-picture">Profile picture</label>
                        <input ref={profileInputRef} id="edit-profile-picture" type="file" accept="image/*" onChange={(event) => handleImageChange(event, "profile")} />
                        {profilePictureUrl && (
                            <div className="edit-image-management">
                                <img className="edit-image-preview edit-avatar-preview" src={getMediaUrl(profilePictureUrl)} alt="Profile picture preview" />
                                <button className="button-secondary" type="button" onClick={() => removeImage("profile")}>Remove profile picture</button>
                            </div>
                        )}

                        <label htmlFor="edit-cover-photo">Cover photo</label>
                        <input ref={coverInputRef} id="edit-cover-photo" type="file" accept="image/*" onChange={(event) => handleImageChange(event, "cover")} />
                        {coverPhotoUrl && (
                            <div className="edit-image-management">
                                <img className="edit-image-preview edit-cover-preview" src={getMediaUrl(coverPhotoUrl)} alt="Cover photo preview" />
                                <button className="button-secondary" type="button" onClick={() => removeImage("cover")}>Remove cover photo</button>
                            </div>
                        )}

                        <button className="button-primary" type="submit" disabled={loading || loadingProfile}>
                            {loading ? "Saving..." : "Save changes"}
                        </button>
                    </form>
                </>
            )}
        </section>
    );
}

export default EditProfile;
