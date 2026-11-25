import { useEffect } from "react";

const FOCUSABLE_SELECTOR = [
    "a[href]",
    "button:not([disabled])",
    "input:not([disabled])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    '[tabindex]:not([tabindex="-1"])',
].join(",");

function useFocusTrap(active, containerRef, initialFocusRef) {
    useEffect(() => {
        if (!active) return undefined;

        const handleKeyDown = (event) => {
            if (event.key !== "Tab") return;
            const container = containerRef.current;
            if (!container) return;

            const focusable = [...container.querySelectorAll(FOCUSABLE_SELECTOR)]
                .filter((element) => element.offsetParent !== null || element === document.activeElement);
            if (!focusable.length) {
                event.preventDefault();
                return;
            }

            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            const current = document.activeElement;

            if (event.shiftKey && (current === first || !container.contains(current))) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && (current === last || !container.contains(current))) {
                event.preventDefault();
                first.focus();
            }
        };

        document.addEventListener("keydown", handleKeyDown);
        return () => document.removeEventListener("keydown", handleKeyDown);
    }, [active, containerRef, initialFocusRef]);
}

export default useFocusTrap;
