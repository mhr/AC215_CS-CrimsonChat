// TypeBar.js

import React, { useCallback } from "react";
import "./TypeBar.css";
import useStore from "../../store"; // Adjust the path based on your project structure

const TypeBar = ({
  onEnter,
  helperText = "Enter your secret...",
  helperTextClass = "search-input",
  clearOnEnter = true,
}) => {
  // Select state and setter from the store
  const inputValue = useStore((state) => state.inputValue);
  const setInputValue = useStore((state) => state.setInputValue);

  // Local state for hover effect
  const [isHovered, setIsHovered] = React.useState(false);

  // Handle input changes
  const handleInputChange = useCallback(
    (e) => {
      setInputValue(e.target.value);
    },
    [setInputValue]
  );

  // Handle Enter key press using onKeyDown
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" && inputValue.trim()) {
        onEnter(inputValue.trim()); // Triggers action on Enter
        if (clearOnEnter) {
          setInputValue(""); // Clear input if clearOnEnter is true
        }
      }
    },
    [inputValue, onEnter, clearOnEnter, setInputValue]
  );

  return (
    <div className="search-bar-container">
      <input
        type={helperTextClass === "search-input" ? "password" : ""}
        className={`${helperTextClass} ${isHovered ? "hovered" : ""}`}
        placeholder={helperText}
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsHovered(false)}
        onBlur={() => setIsHovered(false)}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      />
    </div>
  );
};

export default TypeBar;
