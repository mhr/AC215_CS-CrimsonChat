import React, { useState } from 'react';
import './TypeBar.css';

const TypeBar = ({ onEnter, helperText = "Enter your secret...", helperTextClass ="search-input", clearOnEnter=true  }) => {
  const [inputValue, setInputValue] = useState('');
  const [isHovered, setIsHovered] = useState(false);

  // Handle input changes
  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  // Handle Enter key press using onKeyDown
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      onEnter(inputValue.trim()); // Triggers login on Enter
      if (clearOnEnter) {
        setInputValue(''); // Clear input if clearOnEnter is true
      }
    }
  };

  return (
    <div className="search-bar-container">
      <input
        type={helperTextClass==="search-input" ? 'password' : ''}
        className={`${helperTextClass} ${isHovered ? 'hovered' : ''}`}
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
