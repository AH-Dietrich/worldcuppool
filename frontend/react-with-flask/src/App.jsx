import { useAuth0 } from "@auth0/auth0-react";
import './App.css'
import LoginButton from './components/LoginButton'
import Profile from './components/Profile'
import PredictionSwiper from './components/PredictionSwiper';
import LogoutButton from "./components/LogoutButton";

function App() {
  const { isAuthenticated, isLoading, error } = useAuth0();

  if (isLoading) {
    return (
      <div className="app-container">
        <div className="loading-state">
          <div className="loading-text">Loading...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-container">
        <div className="error-state">
          <div className="error-title">Oops!</div>
          <div className="error-message">Something went wrong</div>
          <div className="error-sub-message">{error.message}</div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div>
        {isAuthenticated ? null : <LoginButton/>}
        {isAuthenticated ? <div><LogoutButton/><Profile/><PredictionSwiper/></div> : null}
      </div>
    </>
  )
}

export default App
