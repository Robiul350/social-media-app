import { useEffect, useState } from "react";
import { Link, NavLink, useParams } from "react-router-dom";
import api from "../api/axios";
import UserAvatar from "../components/UserAvatar";

const connectionLists = {
    friends: {
        endpoint: "social/friends/",
        label: "Friends",
        description: "People who have accepted your friend requests.",
    },
    followers: {
        endpoint: "social/users/followers/",
        label: "Followers",
        description: "People who follow your updates.",
    },
    following: {
        endpoint: "social/users/following/",
        label: "Following",
        description: "People whose updates you follow.",
    },
};

function Connections() {
    const { section } = useParams();
    const requestedList = connectionLists[section];
    const activeSection = requestedList ? section : "friends";
    const list = connectionLists[activeSection];
    const [result, setResult] = useState(null);

    useEffect(() => {
        const controller = new AbortController();

        api.get(list.endpoint, { signal: controller.signal })
            .then((response) => {
                const data = response.data;
                setResult({
                    section: activeSection,
                    people: Array.isArray(data) ? data : data.results || [],
                    error: "",
                });
            })
            .catch((requestError) => {
                if (requestError.code !== "ERR_CANCELED") {
                    setResult({
                        section: activeSection,
                        people: [],
                        error: "Unable to load your connections. Please try again.",
                    });
                }
            });

        return () => controller.abort();
    }, [list, activeSection]);

    const loading = result?.section !== activeSection;
    const people = loading ? [] : result.people;
    const error = loading ? "" : result.error;

    return (
        <main className="connections-page">
            <header className="page-heading">
                <div>
                    <p className="page-eyebrow">YOUR COMMUNITY</p>
                    <h1>{list.label}</h1>
                    <p>{list.description}</p>
                </div>
                <Link className="button-secondary" to="/friend-requests">
                    Friend requests
                </Link>
            </header>

            <nav className="connection-tabs" aria-label="Connection lists">
                {Object.entries(connectionLists).map(([key, item]) => (
                    <NavLink
                        key={key}
                        to={`/connections/${key}`}
                        className={({ isActive }) =>
                            isActive ? "connection-tab is-active" : "connection-tab"
                        }
                        aria-current={activeSection === key ? "page" : undefined}
                    >
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            {!requestedList && section && (
                <p className="form-error" role="alert">
                    The &ldquo;{section}&rdquo; list isn&rsquo;t available. Showing your friends instead.
                </p>
            )}

            {error && <p className="form-error" role="alert">{error}</p>}

            <section className="connection-list">
                {loading ? (
                    <>
                        <p className="sr-only" role="status">Loading {list.label.toLowerCase()}...</p>
                        <div className="feed-skeletons" aria-hidden="true">
                            <div className="user-result-skeleton" />
                            <div className="user-result-skeleton" />
                            <div className="user-result-skeleton" />
                        </div>
                    </>
                ) : people.length ? (
                    people.map((person) => {
                        const name = [person.first_name, person.last_name]
                            .filter(Boolean)
                            .join(" ") || person.username;
                        return (
                            <article className="connection-card" key={person.id}>
                                <div className="connection-person">
                                    <Link
                                        className="friend-request-person"
                                        to={`/users/${person.id}`}
                                        aria-label={`View ${name}'s profile`}
                                    >
                                        <UserAvatar
                                            className="connection-avatar"
                                            src={person.profile_picture}
                                            name={name}
                                            interactive={false}
                                        />
                                        <span className="friend-request-person-copy">
                                            <strong>{name}</strong>
                                            <span>@{person.username}</span>
                                        </span>
                                    </Link>
                                </div>
                            </article>
                        );
                    })
                ) : (
                    <div className="empty-state">
                        <h2>No {list.label.toLowerCase()} yet</h2>
                        <p>
                            {activeSection === "friends"
                                ? "Accepted friend requests will appear here."
                                : activeSection === "followers"
                                    ? "People who follow you will appear here."
                                    : "People you follow will appear here."}
                        </p>
                        <Link className="button-primary" to="/search">Discover people</Link>
                    </div>
                )}
            </section>
        </main>
    );
}

export default Connections;
