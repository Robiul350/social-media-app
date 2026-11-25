import { useCallback, useEffect, useRef, useState } from "react";

function isVideoSource(source) {
    return /\.(mp4|webm|ogg|mov|m4v)(\?|$)/i.test(source || "");
}

function MediaViewer({
    src,
    images,
    initialIndex = 0,
    alt = "Image",
    onClose,
}) {
    const closeButtonRef = useRef(null);
    const closeTimerRef = useRef(null);
    const [imageIndex, setImageIndex] = useState(initialIndex);
    const [failedSrc, setFailedSrc] = useState("");
    const [isClosing, setIsClosing] = useState(false);
    const [zoom, setZoom] = useState(1);
    const sources = images?.length ? images : src ? [src] : [];
    const currentIndex = Math.min(imageIndex, Math.max(sources.length - 1, 0));
    const activeSrc = sources[currentIndex];
    const isVideo = isVideoSource(activeSrc);
    const canNavigate = sources.length > 1;

    const requestClose = useCallback(() => {
        if (closeTimerRef.current !== null) return;
        setIsClosing(true);
        closeTimerRef.current = window.setTimeout(() => {
            closeTimerRef.current = null;
            onClose();
        }, 180);
    }, [onClose]);

    const stepImage = useCallback((offset) => {
        setImageIndex((current) => (current + offset + sources.length) % sources.length);
        setZoom(1);
    }, [sources.length]);

    useEffect(() => {
        if (!activeSrc) return undefined;
        const previousFocus = document.activeElement;
        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        closeButtonRef.current?.focus();
        const handleKeyDown = (event) => {
            if (event.key === "Escape") requestClose();
            if (canNavigate && event.key === "ArrowLeft") stepImage(-1);
            if (canNavigate && event.key === "ArrowRight") stepImage(1);
        };
        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.body.style.overflow = previousOverflow;
            document.removeEventListener("keydown", handleKeyDown);
            previousFocus?.focus?.();
        };
    }, [activeSrc, canNavigate, requestClose, sources.length, stepImage]);

    useEffect(() => () => {
        window.clearTimeout(closeTimerRef.current);
    }, []);

    if (!activeSrc) return null;

    return (
        <div
            className={isClosing ? "media-viewer-backdrop is-closing" : "media-viewer-backdrop"}
            onMouseDown={(event) => {
                if (event.target === event.currentTarget) requestClose();
            }}
        >
            <section className="media-viewer-dialog" role="dialog" aria-modal="true" aria-label={alt}>
                <button
                    ref={closeButtonRef}
                    type="button"
                    className="media-viewer-close"
                    onClick={requestClose}
                    aria-label="Close image viewer"
                >
                    ×
                </button>
                {canNavigate && (
                    <>
                        <button
                            type="button"
                            className="media-viewer-navigation previous"
                            onClick={() => stepImage(-1)}
                            aria-label="Previous image"
                        >
                            ‹
                        </button>
                        <button
                            type="button"
                            className="media-viewer-navigation next"
                            onClick={() => stepImage(1)}
                            aria-label="Next image"
                        >
                            ›
                        </button>
                    </>
                )}
                {failedSrc === activeSrc ? (
                    <p className="media-viewer-error" role="alert">This media is unavailable.</p>
                ) : isVideo ? (
                    <video
                        key={activeSrc}
                        src={activeSrc}
                        controls
                        playsInline
                        onError={() => setFailedSrc(activeSrc)}
                    />
                ) : (
                    <img
                        key={activeSrc}
                        src={activeSrc}
                        alt={alt}
                        onError={() => setFailedSrc(activeSrc)}
                        style={{ transform: `scale(${zoom})`, transformOrigin: "center center" }}
                    />
                )}
                {!isVideo && (
                    <div className="media-viewer-zoom" role="group" aria-label="Zoom controls">
                        <button type="button" onClick={() => setZoom((z) => Math.max(0.5, +(z - 0.25).toFixed(2)))} aria-label="Zoom out">−</button>
                        <button type="button" onClick={() => setZoom(1)} aria-label="Fit to screen">Fit</button>
                        <button type="button" onClick={() => setZoom((z) => Math.min(4, +(z + 0.25).toFixed(2)))} aria-label="Zoom in">+</button>
                    </div>
                )}
                {canNavigate && (
                    <span className="media-viewer-counter" aria-live="polite">
                        {currentIndex + 1} / {sources.length}
                    </span>
                )}
            </section>
        </div>
    );
}

export default MediaViewer;
