
import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/";
export const API_ORIGIN = new URL(
    import.meta.env.VITE_API_ORIGIN || apiBaseUrl,
    window.location.origin
).origin;

export function getMediaUrl(path) {
    if (!path) return "";
    try {
        return new URL(path, `${API_ORIGIN}/`).toString();
    } catch {
        return path;
    }
}

const api = axios.create({
    baseURL: apiBaseUrl,
});

function expireSession() {
    const hadSession = Boolean(
        localStorage.getItem("access") || localStorage.getItem("refresh")
    );
    ["access", "refresh", "user_id", "username"].forEach((key) =>
        localStorage.removeItem(key)
    );
    window.dispatchEvent(new Event("socialconnect:auth-change"));
    if (
        hadSession &&
        window.location.pathname !== "/login" &&
        window.location.pathname !== "/register"
    ) {
        window.location.assign("/login");
    }
}

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("access");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

let refreshing = null;

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status !== 401 || !originalRequest) {
            return Promise.reject(error);
        }

        if (originalRequest._skipAuthRefresh || originalRequest._retry) {
            expireSession();
            return Promise.reject(error);
        }

        const refreshToken = localStorage.getItem("refresh");
        if (!refreshToken) {
            expireSession();
            return Promise.reject(error);
        }

        originalRequest._retry = true;
        try {
            refreshing ||= api.post(
                "users/token/refresh/",
                { refresh: refreshToken },
                { _skipAuthRefresh: true }
            );
            const response = await refreshing;
            refreshing = null;

            if (!response.data?.access) {
                throw new Error("The token refresh response did not include an access token.");
            }

            localStorage.setItem("access", response.data.access);
            if (response.data.refresh) {
                localStorage.setItem("refresh", response.data.refresh);
            }
            originalRequest.headers.Authorization =
                `Bearer ${response.data.access}`;
            return api(originalRequest);
        } catch (refreshError) {
            refreshing = null;
            expireSession();
            return Promise.reject(refreshError);
        }
    }
);

export default api;
