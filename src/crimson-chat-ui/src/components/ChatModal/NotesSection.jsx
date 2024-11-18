// NotesSection.js

import React, { useEffect, useRef } from "react";
import "./ChatModal.css";
import "../CardGrid/CardGrid.css";
import { getLinkPreview } from "link-preview-js";
import { saveNotes } from "../../api/api"; // Import the API function
import useStore from "../../store";

const LinkCard = ({ item }) => {
  const [linkData, setLinkData] = React.useState({
    title: "",
    description: "",
    images: [],
    url: item.url,
  });

  useEffect(() => {
    getLinkPreview(`https://cors-anywhere.herokuapp.com/${item.url}`)
      .then((data) => {
        setLinkData({
          title: data.title || "No Title Available",
          description: data.description || "No description available.",
          images: data.images.length ? data.images : [],
          url: data.url || item.url,
        });
      })
      .catch(() => {
        setLinkData((prevData) => ({
          ...prevData,
          title: "No Title Available",
          description: "No description available.",
          images: [],
        }));
      });
  }, [item.url]);

  return (
    <div
      className="link-card"
      style={{ backgroundColor: "#fcf8f6", width: "100%" }}
    >
      <a href={linkData.url} target="_blank" rel="noopener noreferrer">
        {linkData.images[0] && (
          <img
            src={linkData.images[0]}
            alt={linkData.title}
            className="link-card-image"
          />
        )}
        <h3 className="link-card-title">{linkData.title}</h3>
        <p className="link-card-description">{linkData.description}</p>
        <small className="link-card-url">{item.url}</small>
      </a>
    </div>
  );
};

const Card = ({ item }) => {
  return (
    <div className="card" style={{ width: "100%" }}>
      <div className="card-content">
        <span className="quote-mark">“</span>
        <p>{item.content}</p>
        <span className="quote-mark">”</span>
      </div>
    </div>
  );
};

const NotesSection = ({ closeModal }) => {
  // Select state and setters from the store
  const notes = useStore((state) => state.notes);
  const setNotes = useStore((state) => state.setNotes);
  const addNote = useStore((state) => state.addNote);

  const notesGridRef = useRef(null); // Ref to track the notes grid container

  const handleDrop = (e) => {
    e.preventDefault();
    const draggedText = e.dataTransfer.getData("text/plain"); // Get the dragged text or URL

    if (draggedText) {
      const isUrl = draggedText.startsWith("http"); // Simple URL check
      const newNote = isUrl
        ? { type: "link", url: draggedText, datetime: new Date().toISOString() }
        : {
            type: "quote",
            content: draggedText,
            datetime: new Date().toISOString(),
          };

      addNote(newNote);

      // Scroll to the bottom after updating notes
      setTimeout(() => {
        if (notesGridRef.current) {
          notesGridRef.current.scrollTop = notesGridRef.current.scrollHeight;
        }
      }, 300);
    }

    // Clear text selection
    const selection = window.getSelection();
    if (selection) {
      selection.removeAllRanges(); // Clear all selected ranges
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault(); // Allow drop
  };

  const handleSaveAndClose = async () => {
    if (notes.length === 0) {
      closeModal(); // Close the modal
    } else {
      try {
        await saveNotes(notes); // Send notes to server
        closeModal(); // Close the modal
      } catch (error) {
        alert("Failed to save notes. Please try again.");
      }
    }
  };

  // Clean up notes when component unmounts
  useEffect(() => {
    return () => {
      setNotes([]); // Reset notes in the store
    };
  }, [setNotes]);

  return (
    <div
      className="notes-section"
      onDrop={handleDrop}
      onDragOver={handleDragOver}
    >
      <h3>Bookmarks</h3>
      <p className="helper-text">Select and drag text or URLs to save</p>
      <div className="notes-grid" ref={notesGridRef}>
        {notes.map((note, index) =>
          note.type === "link" ? (
            <LinkCard key={index} item={note} />
          ) : (
            <Card key={index} item={note} />
          )
        )}
      </div>
      <div className="close-save-button-container">
        <button className="close-save-button" onClick={handleSaveAndClose}>
          Close & Save
        </button>
      </div>
    </div>
  );
};

export default NotesSection;
