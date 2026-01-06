import { useAuth0 } from "@auth0/auth0-react";

const Profile = () => {
    const {user, isAuthenticated, isLoading, getAccessTokenWithPopup, getIdTokenClaims} = useAuth0();
    
    if (isLoading)
    {
        return <div/>
    }

    if (!isAuthenticated)
    {
        getAccessTokenWithPopup().then((t) => {
            console.log(t)
        })
    }

    getIdTokenClaims().then((t) => {
        console.log(t)
    })


    console.log("not loading")
    console.log(isAuthenticated)
    console.log(user)
    return (
        isAuthenticated && user ? (<div>
            <p>{user.name}</p>
        </div>) : null
    );
}

export default Profile;