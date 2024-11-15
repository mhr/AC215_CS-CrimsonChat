import './App.css';
import Sidebar from './components/Sidebar/Sidebar';
import React, { useState, useEffect, useRef } from 'react';
import TypeBar from './components/TypeBar/TypeBar';
import CardGrid from './components/CardGrid/CardGrid';
import ChatModal from './components/ChatModal/ChatModal';
import { fetchCards } from './api/api';

const ChatPage = ({ handleLogout }) => {
    const [showError, setShowError] = useState(false);
    const [fadeOut, setFadeOut] = useState(false);
    const [selectedChatId, setSelectedChatId] = useState(null); // Track selected chat ID
    const [showChatModal, setShowChatModal] = useState(false); // State for chat modal visibility
    const [userQuery, setUserQuery] = useState(""); // State for user query
    const [items, setItems] = useState([]);
    const contentRef = useRef(null);

    // Fetch cards on page load
    useEffect(() => {
        const getCards = async () => {
            try {
                const fetchedCards = await fetchCards();
                setItems(fetchedCards);
            } catch (error) {
                console.error('Error fetching cards:', error);
                setItems([]); // Render empty if an error occurs
            }
        };

        getCards();
    }, []);

    const openChatModal = (query) => {
        setUserQuery(query); // Store the query in state
        setShowChatModal(true); // Open the modal
    };

    const closeChatModal = async () => {
        setShowChatModal(false);
        // When modal closes, trigger refetching of cards
        setFadeOut(true); // Start fade-out effect
        // Wait for the fade-out animation to complete
        setTimeout(async () => {
            // Simulate fetching new cards
            try {
                const fetchedCards = await fetchCards();
                setItems(fetchedCards); // Update with new cards
            } catch (error) {
                console.error('Error fetching cards:', error);
                setItems([]); // Render empty if an error occurs
            }
            setFadeOut(false); // Start fade-in effect once new cards are loaded
        }, 500); // Match the fade-out duration with this timeout
    };

    useEffect(() => {
        const sidebar = document.querySelector('.sidebar');
        const contentContainer = document.querySelector('.content-container');
    
        // Apply fade-in initially
        if (sidebar && contentContainer) {
            sidebar.classList.add('fade-in');
            contentContainer.classList.add('fade-in');
        }
    
        const checkScreenRatio = () => {
            const { innerWidth, innerHeight } = window;
            const isTallScreen = innerHeight / innerWidth > 2 / 3;
    
            if (isTallScreen) {
                sidebar.classList.replace('fade-in', 'fade-out');
                contentContainer.classList.replace('fade-in', 'fade-out');
                setTimeout(() => {
                    setShowError(true);
                    sidebar.classList.replace('fade-out', 'fade-in');
                    contentContainer.classList.replace('fade-out', 'fade-in');
                }, 1000);
            } else {
                sidebar.classList.replace('fade-in', 'fade-out');
                contentContainer.classList.replace('fade-in', 'fade-out');
                setTimeout(() => {
                    setShowError(false);
                    sidebar.classList.replace('fade-out', 'fade-in');
                    contentContainer.classList.replace('fade-out', 'fade-in');
                }, 1000);
            }
        };
    
        checkScreenRatio();
        window.addEventListener('resize', checkScreenRatio);
    
        return () => {
            window.removeEventListener('resize', checkScreenRatio);
        };
    }, []);

    const settingsOptions = [
      { name: 'Log out', action: handleLogout },
    ];

    // Function to handle card selection
    const handleCardClick = (chatId) => {
        setSelectedChatId((prevChatId) => (prevChatId === chatId ? null : chatId));
        console.log("selected id", chatId);
    };

    // Click outside to deselect cards
    const handleClickOutside = (event) => {
        if (contentRef.current && !contentRef.current.contains(event.target)) {
            setSelectedChatId(null);
        }
    };

    useEffect(() => {
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    return (
        <div className="chat-page">
            <Sidebar settingsOptions={settingsOptions} />
            <div className={`content-container ${fadeOut ? 'fade-out' : 'fade-in'}`}>
                {showError ? (
                    <div className="error-message">
                        Ooopsie, I need a wider screen to help you.
                    </div>
                ) : (
                    <>
                        <TypeBar 
                            onEnter={(query) => openChatModal(query)} // Pass user input on Enter
                            helperText="How can I help you?" 
                            helperTextClass="chat-input"
                        />
                        <CardGrid 
                            items={items} 
                            selectedChatId={selectedChatId} 
                            onCardClick={handleCardClick} 
                        />
                    </>
                )}
            </div>
            {showChatModal && <ChatModal onClose={closeChatModal} userQuery={userQuery} />}
        </div>
    );
};

export default ChatPage;
