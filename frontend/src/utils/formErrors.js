export function normalizeFieldErrors(data) {
    if (!data || typeof data !== "object") return {};
    return Object.entries(data).reduce((errors, [key, value]) => {
        if (key === "detail" || key === "non_field_errors") return errors;
        const message = Array.isArray(value)
            ? value.join(" ")
            : typeof value === "string"
                ? value
                : "";
        if (message) errors[key] = message;
        return errors;
    }, {});
}

export function getNonFieldError(data) {
    if (!data || typeof data !== "object") return "";
    if (Array.isArray(data.non_field_errors)) return data.non_field_errors.join(" ");
    return typeof data.detail === "string" ? data.detail : "";
}
