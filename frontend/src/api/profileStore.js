import api from "./axios";

let state = {
    userId: null,
    data: null,
    error: "",
    loading: false,
};
let inFlight = null;
const listeners = new Set();

function publish() {
    listeners.forEach((listener) => listener());
}

export function getProfileSnapshot() {
    return state;
}

export function subscribeProfile(listener) {
    listeners.add(listener);
    return () => listeners.delete(listener);
}

export function loadProfile({ force = false } = {}) {
    const access = localStorage.getItem("access");
    const userId = localStorage.getItem("user_id");

    if (!access) {
        state = { userId: null, data: null, error: "", loading: false };
        publish();
        return Promise.resolve(null);
    }

    if (!force && state.userId === userId && state.data) {
        return Promise.resolve(state.data);
    }

    if (inFlight && !force) return inFlight;

    state = {
        userId,
        data: state.userId === userId ? state.data : null,
        error: "",
        loading: true,
    };
    publish();

    const request = api.get("users/profile/")
        .then((response) => {
            state = { userId, data: response.data, error: "", loading: false };
            publish();
            return response.data;
        })
        .catch(() => {
            state = {
                userId,
                data: null,
                error: "Your profile could not be loaded.",
                loading: false,
            };
            publish();
            return null;
        })
        .finally(() => {
            if (inFlight === request) inFlight = null;
        });

    inFlight = request;
    return request;
}

export function resetProfile({ reload = false } = {}) {
    inFlight = null;
    state = { userId: null, data: null, error: "", loading: false };
    publish();
    if (reload) loadProfile();
}
