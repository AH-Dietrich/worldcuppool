import { useAuth0 } from "@auth0/auth0-react";

const Profile = () => {
    const {user, isAuthenticated, isLoading} = useAuth0();
    
    if (isLoading)
    {
        return <div/>
    }

    return (
        isAuthenticated && user ? (<div>
            <p>{user.given_name}</p>
        </div>) : null
    );
}

export default Profile;