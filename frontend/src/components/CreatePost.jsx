import { useRef, useState } from "react";
import api from "../api/axios";

function CreatePost({ onPostCreated }) {
    const [content, setContent] = useState("");
    const [image, setImage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const fileInputRef = useRef(null);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!content.trim() && !image) {
            setError("Write something or select an image.");
            return;
        }

        const formData = new FormData();

        formData.append("content", content);

        if (image) {
            formData.append("image", image);
        }

        try {
            setLoading(true);
            setError("");

            await api.post("posts/", formData);

            setContent("");
            setImage(null);
            if (fileInputRef.current) fileInputRef.current.value = "";
            onPostCreated?.();

        } catch (error) {
            setError(
                JSON.stringify(error.response?.data || "Post creation failed")
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-post">
            <h3>Create a Post</h3>

            <form onSubmit={handleSubmit}>
                <textarea
                    placeholder="What's on your mind?"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                />

                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={(e) => setImage(e.target.files[0])}
                />

                {error && <p className="error">{error}</p>}

                <button type="submit" disabled={loading}>
                    {loading ? "Posting..." : "Post"}
                </button>
            </form>
        </div>
    );
}

export default CreatePost;