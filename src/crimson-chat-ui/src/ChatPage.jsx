import "./App.css";
import Sidebar from "./components/Sidebar/Sidebar";
import React, { useEffect, useRef, useCallback } from "react";
import TypeBar from "./components/TypeBar/TypeBar";
import CardGrid from "./components/CardGrid/CardGrid";
import ChatModal from "./components/ChatModal/ChatModal";
import { fetchCards } from "./api/api";
import useStore from "./store";
import debounce from "lodash.debounce";

const ChatPage = ({ handleLogout }) => {
  const showError = useStore((state) => state.showError);
  const setShowError = useStore((state) => state.setShowError);
  const fadeOut = useStore((state) => state.fadeOut);
  const setFadeOut = useStore((state) => state.setFadeOut);
  const selectedChatId = useStore((state) => state.selectedChatId);
  const setSelectedChatId = useStore((state) => state.setSelectedChatId);
  const showChatModal = useStore((state) => state.showChatModal);
  const setShowChatModal = useStore((state) => state.setShowChatModal);
  const userQuery = useStore((state) => state.userQuery);
  const setUserQuery = useStore((state) => state.setUserQuery);
  const items = useStore((state) => state.items);
  const setItems = useStore((state) => state.setItems);

  const contentRef = useRef(null);

  // Fetch cards on page load
  useEffect(() => {
    const getCards = async () => {
      try {
        const fetchedCards = await fetchCards();
        setItems(fetchedCards);
      } catch (error) {
        console.error("Error fetching cards:", error);
        setItems([]); // Render empty if an error occurs
      }
    };

    getCards();
  }, [setItems]);

  const openChatModal = (query) => {
    setUserQuery(query); // Store the query in state
    setShowChatModal(true); // Open the modal
  };

  const closeChatModal = async () => {
    if (!showChatModal) return; // Prevent redundant updates
    setShowChatModal(false);
    setFadeOut(true); // Start fade-out effect
    setTimeout(async () => {
      try {
        const fetchedCards = await fetchCards();
        setItems(fetchedCards); // Update with new cards
      } catch (error) {
        console.error("Error fetching cards:", error);
        setItems([]); // Render empty if an error occurs
      } finally {
        setFadeOut(false); // Start fade-in effect once new cards are loaded
      }
    }, 500); // Match the fade-out duration with this timeout
  };

  useEffect(() => {
    const sidebar = document.querySelector(".sidebar");
    const contentContainer = document.querySelector(".content-container");

    // Apply fade-in initially
    if (sidebar && contentContainer) {
      sidebar.classList.add("fade-in");
      contentContainer.classList.add("fade-in");
    }

    const checkScreenRatio = debounce(() => {
      const { innerWidth, innerHeight } = window;
      const isTallScreen = innerHeight / innerWidth > 2 / 3;

      setShowError(isTallScreen);
    }, 300); // Debounced to prevent excessive updates

    checkScreenRatio();
    window.addEventListener("resize", checkScreenRatio);

    return () => {
      window.removeEventListener("resize", checkScreenRatio);
    };
  }, [setShowError]);

  const settingsOptions = [{ name: "Log out", action: handleLogout }];

  // Function to handle card selection
  const handleCardClick = (chatId) => {
    setSelectedChatId((prevChatId) => (prevChatId === chatId ? null : chatId));
    console.log("selected id", chatId);
  };

  // Click outside to deselect cards
  const handleClickOutside = useCallback(
    (event) => {
      if (contentRef.current && !contentRef.current.contains(event.target)) {
        setSelectedChatId(null);
      }
    },
    [setSelectedChatId]
  );

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [handleClickOutside]);

  return (
    <div className="chat-page">
      <Sidebar settingsOptions={settingsOptions} />
      <div className={`content-container ${fadeOut ? "fade-out" : "fade-in"}`}>
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
      {showChatModal && (
        <ChatModal onClose={closeChatModal} userQuery={userQuery} />
      )}
    </div>
  );
};

export default ChatPage;
