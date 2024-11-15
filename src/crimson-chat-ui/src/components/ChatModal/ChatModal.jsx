// ChatModal.js
import React, { useState, useEffect } from 'react';
import './ChatModal.css';
import ChatInterface from './ChatInterface';
import NotesSection from './NotesSection';
import { sendMessageToAI } from '../../api/api'; // Import the API function

const ChatModal = ({ onClose, userQuery }) => {
    const [isFadingOut, setIsFadingOut] = useState(false);
    const [notes, setNotes] = useState([]);

    const handleAddNote = (newNote) => {
        setNotes((prevNotes) => [...prevNotes, newNote]);
    };

    const handleClose = () => {
        setIsFadingOut(true);
        setTimeout(() => {
            onClose();
        }, 500);
    };

    useEffect(() => {
        setIsFadingOut(false);
    }, []);

    return (
        <div className={`modal-backdrop ${isFadingOut ? 'fade-out' : 'fade-in'}`}>
            <div className="chat-modal">
                <button className="close-button" onClick={handleClose}>+</button>
                <div className="chat-modal-content">
                    <ChatInterface sendMessageToAI={sendMessageToAI} initialQuery={userQuery} onDragMessage={handleAddNote} />
                    <NotesSection initialNotes={notes} closeModal={handleClose}/>
                </div>
            </div>
        </div>
    );
};

export default ChatModal;