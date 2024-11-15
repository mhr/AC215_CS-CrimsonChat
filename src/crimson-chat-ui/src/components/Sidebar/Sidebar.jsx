// Sidebar.js
import React, { useState, useEffect, useRef } from 'react';
import './Sidebar.css';

const Popover = ({ isOpen, onClose, options, style }) => {
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (isOpen && !event.target.closest('.popover-content')) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="popover-overlay">
      <div className="popover-content fade-in" style={style}>
        <ul className="popover-options">
          {options.map((option, index) => (
            <li
              key={index}
              className="popover-option"
              onClick={() => {
                option.action();
                onClose();
              }}
            >
              {option.name}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

const Sidebar = ({ settingsOptions }) => {
  const [isPopoverOpen, setPopoverOpen] = useState(false);
  const [popoverPosition, setPopoverPosition] = useState({ top: 0, left: 0 });
  const settingsRef = useRef(null);

  const handleGearClick = () => {
    const rect = settingsRef.current.getBoundingClientRect();
    setPopoverPosition({
      top: rect.top - 20 + window.scrollY,
      left: rect.right + window.scrollX + 10, // Position to the right with 10px gap
    });
    setPopoverOpen((prev) => !prev);
  };

  return (
    <nav className="sidebar">
      <p className="branding">
        <span className="app-name">CrimsonChat</span>
      </p>
      <div className="bottom">
        <div className="referrals-link">
          <a
            className="referrals-icon"
            href="https://github.com/mhr/AC215_CS-CrimsonChat"
            target="_blank"
            rel="noopener noreferrer"
          ></a>
        </div>
        {settingsOptions?.length > 0 && (
          <button className="settings-gear" onClick={handleGearClick} ref={settingsRef}></button>
        )}
      </div>
      <Popover
        isOpen={isPopoverOpen}
        onClose={() => setPopoverOpen(false)}
        options={settingsOptions}
        style={{ position: 'absolute', top: popoverPosition.top, left: popoverPosition.left }}
      />
    </nav>
  );
};



export default Sidebar;
