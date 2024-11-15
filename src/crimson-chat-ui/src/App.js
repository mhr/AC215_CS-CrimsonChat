import logo from './logo.svg';
import './App.css';
import './ChatPage.css';
import Sidebar from './components/Sidebar/Sidebar';
import ChatPage from './ChatPage';
import React, { useState, useEffect } from 'react';
import TypeBar from './components/TypeBar/TypeBar';
import { validatePassword, logout } from './api/api';

const FullScreenVideo = ({ src }) => {
  const [isLoaded, setIsLoaded] = useState(false);

  const handleLoadedData = () => {
    setIsLoaded(true);
  };

  return (
    <div className="video-container">
      <video
        className={`video ${isLoaded ? 'fade-in-video' : ''}`}
        src={src}
        autoPlay
        muted
        loop
        onLoadedData={handleLoadedData}
      />
    </div>
  );
};

const Login = ({ onLogin }) => {
  useEffect(() => {
    const appElement = document.querySelector('.app');

    // Fade-in on mount
    if (appElement) {
      appElement.classList.add('fade-in');
    }

    // Fade-out on unmount
    return () => {
      if (appElement) {
        appElement.classList.remove('fade-in');
        appElement.classList.add('fade-out');

        // Delay unmount to allow fade-out to complete
        setTimeout(() => {
          appElement.classList.remove('fade-out');
        }, 1000); // Match this duration with CSS transition
      }
    };
  }, []);


  // API CALL HERE
  const handleLoginAttempt = async (password) => {
    try {
      const isValid = await validatePassword(password);
  
      if (isValid) {
        console.log('Login successful');
        const appElement = document.querySelector('.app');
        appElement.classList.add('fade-out');
  
        // Delay the onLogin call to allow fade-out animation
        setTimeout(onLogin, 1000);
      } else {
        console.log('Invalid password');
      }
    } catch (error) {
      console.error('Failed to validate password:', error);
      alert('There was an error validating your password. Please try again.');
    }
  };


  return (
    <div className="app">
      <Sidebar />
      <FullScreenVideo src="/assets/login.mp4" />
      <div className="text-wrapper">
        <h1>
          Welcome to your new, best buddy <span style={{ color: "#748297" }}>Crimsonchat</span>
        </h1>
      </div>
      <div className="typebar-wrapper">
      <TypeBar onEnter={handleLoginAttempt} />
      </div>
    </div>
  );
};


function App() {
  const [currentPage, setCurrentPage] = useState('Login'); // Start with the Login page

  const handleLogout = async () => {
    try {
      await logout();  // Call the API to log out and remove the session key
      setCurrentPage('Login'); // Return to the login page after logout
    } catch (error) {
      console.error('Error during logout:', error);
      alert('Logout failed. Please try again.');
    }
  };

  return (
    <div>
      {currentPage === 'Login' ? (
        <Login onLogin={() => setCurrentPage('ChatPage')} />
      ) : (
        <ChatPage handleLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
