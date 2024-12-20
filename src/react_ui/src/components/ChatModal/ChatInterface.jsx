// ChatInterface.js

import React, { useEffect, useRef, useCallback } from "react";
import TypeBar from "./../TypeBar/TypeBar";
import "./ChatModal.css";
import useStore from "../../store";

const ChatInterface = ({ sendMessageToAI, initialQuery }) => {
  // Select state and setters from the store
  const messages = useStore((state) => state.messages);
  const appendMessage = useStore((state) => state.appendMessage);
  const displayedResponse = useStore((state) => state.displayedResponse);
  const setDisplayedResponse = useStore((state) => state.setDisplayedResponse);
  const updateDisplayedResponse = useStore(
    (state) => state.updateDisplayedResponse
  );

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
              fontWeight: "bold",
              color: "#ff5924",
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
    const selection = window.getSelection();
    const selectedText = selection ? selection.toString() : "";

    if (selectedText) {
      e.dataTransfer.setData("text/plain", selectedText);
    } else if (e.target.tagName === "A") {
      const url = e.target.href;
      e.dataTransfer.setData("text/plain", url);
    } else {
      const messageText = e.target.textContent || "";
      e.dataTransfer.setData("text/plain", messageText);
    }
  };

  const handleNewMessage = useCallback(
    async (text) => {
        appendMessage({ text, sender: "me" });

        // Set up the loading dots animation
        let dots = 0;
        const loadingDotsInterval = setInterval(() => {
            setDisplayedResponse(`CrimsonChat is thinking${".".repeat(dots + 1)}`);
            dots = (dots + 1) % 3; // Cycle through 0, 1, 2
        }, 500);

        try {
            const { response, _ } = await sendMessageToAI(text, messages); // messages = history array
            clearInterval(loadingDotsInterval); // Stop the dots animation
            setDisplayedResponse("");

            // Animate the AI response
            const words = response.split(" ");
            let index = 0;
            const typingInterval = setInterval(() => {
                updateDisplayedResponse((prev) => `${prev} ${words[index]}`);
                index++;
                if (index >= words.length) {
                    clearInterval(typingInterval);
                    appendMessage({ text: response, sender: "ai" });
                    setDisplayedResponse("");
                }
            }, 100);
        } catch (error) {
            clearInterval(loadingDotsInterval); // Stop the dots animation on error
            setDisplayedResponse("");
            console.error("Error sending message:", error);
        }
    },
    [
        appendMessage,
        setDisplayedResponse,
        updateDisplayedResponse,
        sendMessageToAI,
        messages,
    ]
);

  useEffect(() => {
    if (initialQuery && !hasProcessedInitialQuery.current) {
      hasProcessedInitialQuery.current = true;
      handleNewMessage(initialQuery);
    }
  }, [initialQuery, handleNewMessage]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, displayedResponse]);

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${
              msg.sender === "me" ? "user-message" : "ai-response"
            }`}
            onDragStart={handleDragStart}
          >
            <span>{renderMessage(msg.text)}</span>
          </div>
        ))}
        {displayedResponse && (
          <div className="ai-response">
            <span>{displayedResponse}</span>
          </div>
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
