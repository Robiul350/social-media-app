import { useEffect } from "react";
import { BrowserRouter, Navigate, Outlet, Route, Routes, useLocation, useParams } from "react-router-dom";
import AppShell from "./components/AppShell";
import Navbar from "./components/navbar";
import Home from "./pages/home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UserProfile from "./pages/UserProfile";
import UserSearch from "./pages/UserSearch";
import EditProfile from "./pages/EditProfile";
import Messages from "./pages/Messages";
import Notifications from "./pages/Notifications";
import PostDetail from "./pages/PostDetail";
import FriendRequests from "./pages/FriendRequests";
import Connections from "./pages/Connections";
import Bookmarks from "./pages/Bookmarks";

const routeTitles = [
    [/^\/login$/, "Sign in"],
    [/^\/register$/, "Create account"],
    [/^\/$/, "Home"],
    [/^\/search$/, "Explore people"],
    [/^\/edit-profile$/, "Edit profile"],
    [/^\/messages(?:\/\d+)?$/, "Messages"],
    [/^\/notifications$/, "Notifications"],
    [/^\/friend-requests$/, "Friend requests"],
    [/^\/connections\/[\w-]+$/, "Connections"],
    [/^\/bookmarks$/, "Saved posts"],
    [/^\/users\/\d+$/, "Profile"],
    [/^\/posts\/\d+$/, "Post"],
];

function RouteTitle() {
    const location = useLocation();

    useEffect(() => {
        const match = routeTitles.find(([pattern]) => pattern.test(location.pathname));
        document.title = match ? `${match[1]} · SocialConnect` : "SocialConnect";
    }, [location.pathname]);

    return null;
}

function MessagesRoute() {
    const { userId } = useParams();
    return <Messages key={userId || "conversation-list"} />;
}

function UserProfileRoute() {
    const { userId } = useParams();
    return <UserProfile key={userId} />;
}

function PostDetailRoute() {
    const { postId } = useParams();
    return <PostDetail key={postId} />;
}

function PublicLayout() {
    return (
        <>
            <Navbar />
            <Outlet />
        </>
    );
}

function ProtectedLayout() {
    const location = useLocation();

    if (!localStorage.getItem("access")) {
        return <Navigate to="/login" replace state={{ from: location }} />;
    }

    return <AppShell />;
}

function CurrentProfileRedirect() {
    const location = useLocation();
    const userId = localStorage.getItem("user_id");
    return userId
        ? <Navigate to={`/users/${userId}`} replace state={location.state} />
        : <Navigate to="/login" replace />;
}

function App() {
    return (
        <BrowserRouter>
            <RouteTitle />
            <Routes>
                <Route element={<PublicLayout />}>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                </Route>
                <Route element={<ProtectedLayout />}>
                    <Route path="/" element={<Home />} />
                    <Route path="/profile" element={<CurrentProfileRedirect />} />
                    <Route path="/users/:userId" element={<UserProfileRoute />} />
                    <Route path="/posts/:postId" element={<PostDetailRoute />} />
                    <Route path="/search" element={<UserSearch />} />
                    <Route path="/edit-profile" element={<EditProfile />} />
                    <Route path="/messages" element={<MessagesRoute />} />
                    <Route path="/messages/:userId" element={<MessagesRoute />} />
                    <Route path="/notifications" element={<Notifications />} />
                    <Route path="/friend-requests" element={<FriendRequests />} />
                    <Route path="/connections/:section" element={<Connections />} />
                    <Route path="/bookmarks" element={<Bookmarks />} />
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
