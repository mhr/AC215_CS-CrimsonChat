// ChatModal.js

import React from "react";
import "./ChatModal.css";
import ChatInterface from "./ChatInterface";
import NotesSection from "./NotesSection";
import { sendMessageToAI } from "../../api/api"; // Import the API function
import useStore from "../../store";

const ChatModal = ({ onClose, userQuery }) => {
  const isFadingOut = useStore((state) => state.isFadingOut);
  const setIsFadingOut = useStore((state) => state.setIsFadingOut);

  const handleClose = () => {
    setIsFadingOut(true);
    setTimeout(() => {
      onClose();
    }, 500);
  };

  React.useEffect(() => {
    setIsFadingOut(false);
  }, [setIsFadingOut]);

  return (
    <div className={`modal-backdrop ${isFadingOut ? "fade-out" : "fade-in"}`}>
      <div className="chat-modal">
        <button className="close-button" onClick={handleClose}>
          +
        </button>
        <div className="chat-modal-content">
          <ChatInterface
            sendMessageToAI={sendMessageToAI}
            initialQuery={userQuery}
          />
          <NotesSection closeModal={handleClose} />
        </div>
      </div>
    </div>
  );
};

export default ChatModal;
