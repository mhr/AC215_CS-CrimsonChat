import React, { useState, useEffect, useRef } from 'react';
import TypeBar from './../TypeBar/TypeBar';
import './ChatModal.css';

const ChatInterface = ({ sendMessageToAI, initialQuery }) => {
    const [messages, setMessages] = useState([]);
    const [displayedResponse, setDisplayedResponse] = useState('');
    const chatEndRef = useRef(null);
    const hasProcessedInitialQuery = useRef(false);

    const urlRegex = /https?:\/\/[^\s/$.?#].[^\s]*/g;

    const renderMessage = (text) => {
        const parts = text.split(urlRegex);
        const urls = text.match(urlRegex) || [];
        const elements = [];
        parts.forEach((part, index) => {
            elements.push(part);
            if (urls[index]) {
                elements.push(
                    <a
                        key={`url-${index}`}
                        href={urls[index]}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                            fontWeight: 'bold',
                            color: '#ff5924',
                        }}
                    >
                        {urls[index]}
                    </a>
                );
            }
        });
        return elements;
    };

    const handleDragStart = (e) => {
        const selection = window.getSelection(); // Get the user's selected text
        const selectedText = selection ? selection.toString() : '';
    
        if (selectedText) {
            // If there's highlighted text, set it as the data to drag
            e.dataTransfer.setData('text/plain', selectedText);
        } else if (e.target.tagName === 'A') {
            // If the drag is happening on a link, set the URL as the data to drag
            const url = e.target.href;
            e.dataTransfer.setData('text/plain', url);
        } else {
            // If no text is highlighted, fall back to dragging the entire message
            const messageText = e.target.textContent || '';
            e.dataTransfer.setData('text/plain', messageText);
        }
    };
    
    const handleNewMessage = async (text) => {
        setMessages((prevMessages) => [...prevMessages, { text, sender: 'me' }]);
        const response = await sendMessageToAI(text);
        setDisplayedResponse('');
        const words = response.split(' ');
        let index = 0;
        const interval = setInterval(() => {
            setDisplayedResponse((prev) => `${prev} ${words[index]}`);
            index++;
            if (index >= words.length) {
                clearInterval(interval);
                setMessages((prevMessages) => [
                    ...prevMessages,
                    { text: response, sender: 'ai' }
                ]);
                setDisplayedResponse('');
            }
        }, 100);
    };

    useEffect(() => {
        if (initialQuery && !hasProcessedInitialQuery.current) {
            hasProcessedInitialQuery.current = true;
            handleNewMessage(initialQuery);
        }
    }, [initialQuery]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, displayedResponse]);

    return (
        <div className="chat-interface">
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div
                    key={index}
                    className={`message ${msg.sender === 'me' ? 'user-message' : 'ai-response'}`}
                    onDragStart={handleDragStart} // Handle drag start
                >
                    <span>{renderMessage(msg.text)}</span>
                </div>
                ))}
                {displayedResponse && (
                    <div className="ai-response"><span>{displayedResponse}</span></div>
                )}
                <div ref={chatEndRef} />
            </div>
            <TypeBar
                onEnter={handleNewMessage}
                helperText="Type your thought...and press enter"
                helperTextClass="chat-ai"
                clearOnEnter={true}
            />
        </div>
    );
};

export default ChatInterface;
