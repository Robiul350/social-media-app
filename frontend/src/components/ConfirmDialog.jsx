import { useEffect, useRef } from "react";

function ConfirmDialog({
    open,
    title,
    message,
    confirmLabel = "Confirm",
    onCancel,
    onConfirm,
    danger = false,
    busy = false,
    errorMessage = "",
}) {
    const dialogRef = useRef(null);
    const onCancelRef = useRef(onCancel);

    useEffect(() => {
        onCancelRef.current = onCancel;
    }, [onCancel]);

    useEffect(() => {
        if (!open) return undefined;

        const previousFocus = document.activeElement;
        const dialog = dialogRef.current;
        const focusable = dialog?.querySelectorAll("button:not(:disabled)");
        focusable?.[0]?.focus();

        const handleKeyDown = (event) => {
            if (event.key === "Escape" && !busy) onCancelRef.current();
            if (event.key !== "Tab" || !dialog) return;

            const controls = [...dialog.querySelectorAll("button:not(:disabled)")];
            if (!controls.length) return;
            const first = controls[0];
            const last = controls[controls.length - 1];

            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        };

        document.addEventListener("keydown", handleKeyDown);
        return () => {
            document.removeEventListener("keydown", handleKeyDown);
            previousFocus?.focus?.();
        };
    }, [busy, open]);

    if (!open) return null;

    return (
        <div
            className="dialog-backdrop"
            onMouseDown={(event) => {
                if (event.target === event.currentTarget && !busy) onCancel();
            }}
        >
            <section
                ref={dialogRef}
                className="confirm-dialog"
                role="alertdialog"
                aria-modal="true"
                aria-labelledby="confirm-dialog-title"
                aria-describedby="confirm-dialog-message"
            >
                <span className="dialog-mark" aria-hidden="true">!</span>
                <h2 id="confirm-dialog-title">{title}</h2>
                <p id="confirm-dialog-message">{message}</p>
                {errorMessage && <p className="form-error" role="alert">{errorMessage}</p>}
                <div className="dialog-actions">
                    <button type="button" className="button-secondary" onClick={onCancel} disabled={busy}>
                        Cancel
                    </button>
                    <button
                        type="button"
                        className={danger ? "button-danger" : "button-primary"}
                        onClick={onConfirm}
                        disabled={busy}
                    >
                        {busy ? "Please wait..." : confirmLabel}
                    </button>
                </div>
            </section>
        </div>
    );
}

export default ConfirmDialog;
