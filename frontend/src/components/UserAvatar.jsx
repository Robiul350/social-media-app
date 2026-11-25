import { useCallback, useState } from "react";
import { getMediaUrl } from "../api/axios";
import MediaViewer from "./MediaViewer";

function UserAvatar({
    src,
    name = "User",
    className = "",
    loading = "lazy",
    interactive = true,
}) {
    const [failedSrc, setFailedSrc] = useState("");
    const [viewerOpen, setViewerOpen] = useState(false);
    const imageSrc = src ? getMediaUrl(src) : "";
    const imageFailed = Boolean(imageSrc && failedSrc === imageSrc);
    const hasImage = Boolean(imageSrc && !imageFailed);
    const initial = name.trim().charAt(0).toUpperCase() || "U";
    const triggerClass = `user-avatar-trigger${hasImage ? "" : " user-avatar-fallback"} ${className}`.trim();

    const closeViewer = useCallback(() => setViewerOpen(false), []);

    if (!interactive) {
        return (
            <span
                className={triggerClass}
                role="img"
                aria-label={hasImage ? `${name}'s profile picture` : `${name}'s default profile picture`}
            >
                {hasImage ? (
                    <img
                        src={imageSrc}
                        alt=""
                        loading={loading}
                        onError={() => setFailedSrc(imageSrc)}
                    />
                ) : initial}
            </span>
        );
    }

    return (
        <>
            {hasImage ? (
                <button
                    type="button"
                    className={triggerClass}
                    onClick={() => setViewerOpen(true)}
                    aria-label={`View ${name}'s profile picture`}
                >
                    <img
                        src={imageSrc}
                        alt=""
                        loading={loading}
                        onError={() => setFailedSrc(imageSrc)}
                    />
                </button>
            ) : (
                <span className={triggerClass} role="img" aria-label={`${name}'s default profile picture`}>
                    {initial}
                </span>
            )}
            {viewerOpen && (
                <MediaViewer
                    src={imageSrc}
                    alt={`${name}'s profile picture`}
                    onClose={closeViewer}
                />
            )}
        </>
    );
}

export default UserAvatar;
