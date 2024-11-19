import React, { useState, useEffect } from "react";
import "./CardGrid.css";
import { getLinkPreview } from "link-preview-js";

const colors = [
  "#f8fbf7",
  "#f2f7fa",
  "#fcfcfc",
  "#fff7f9",
  "#ffeef1",
  "#fff5f5",
  "#ffeded",
  "#fef6fa",
  "#f9f8f6",
  "#ffffff",
  "#f3f7fc",
  "#f0f4fc",
  "#faf9f7",
  "#fcf8f6",
];

const getDeterministicColor = (key, ref_list = colors) => {
  // Convert the key to a string if it's not already
  const keyString = String(key);
  // Generate a hash from the string
  let hash = 0;
  for (let i = 0; i < keyString.length; i++) {
    hash = (hash * 31 + keyString.charCodeAt(i)) % 2147483647; // Large prime for better distribution
  }
  // Map the hash to a color index
  const index = hash % ref_list.length;
  return ref_list[index];
};
const CardMeta = ({ datetime, chat_id, clickClassName }) => {
  const formatDate = (isoString) => {
    if (!isoString) return "";
    const date = new Date(isoString);
    return new Intl.DateTimeFormat("en-US", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  };

  return (
    <p className={clickClassName}>
      {datetime && chat_id ? `${formatDate(datetime)}` : ""}
    </p>
  );
};

const getDefaultImage = (key) => {
  const keyString = String(key);
  let hash = 0;
  // Generate a hash value
  for (let i = 0; i < keyString.length; i++) {
    hash = (hash * 31 + keyString.charCodeAt(i)) & 0xffffffff; // Ensure the hash stays within 32-bit
  }
  // Map the hash value to one of the 10 image indices (1-10)
  const index = Math.abs(hash) % 10; // Ensure index is between 0 and 9
  return `/assets/${index + 1}.png`; // Return image path (1.png to 10.png)
};

const LinkCard = ({ item, clickClassName, onCardClick }) => {
  const [linkData, setLinkData] = useState({
    title: "",
    description: "",
    images: [],
    url: item.url,
  });

  useEffect(() => {
    getLinkPreview(`https://cors-anywhere.herokuapp.com/${item.url}`)
      .then((data) => {
        setLinkData({
          title: data.title || new URL(item.url).hostname.replace("www.", ""),
          description: data.description || "No description available.",
          images: data.images.length ? data.images : [],
          url: data.url || item.url,
        });
      })
      .catch(() => {
        setLinkData({
          ...linkData,
          title: "No Title Available",
          description: "No description available.",
          images: [], // No images fetched
        });
      });
  }, [item.url]);

  const imageSrc =
    linkData.images[0] ||
    getDefaultImage(item.chat_id + linkData.title + item.datetime);

  return (
    <div
      className={`${clickClassName} link-card`}
      onClick={() => onCardClick(item.chat_id)} // Card click behavior
    >
      <img
        src={imageSrc}
        className="link-card-image"
        alt={linkData.title || "Link preview"}
      />
      <h3 className="link-card-title">{linkData.title}</h3>
      <p className="link-card-description">{linkData.description}</p>
      <a
        href={linkData.url}
        target="_blank"
        className="link-card-url"
        onClick={(e) => e.stopPropagation()} // Stop card click propagation
      >
        {item.url}
      </a>
    </div>
  );
};

const Card = ({ item, clickClassName, onCardClick, backgroundColor }) => {
  return (
    <div
      className={clickClassName}
      onClick={() => onCardClick(item.chat_id)}
      style={{ backgroundColor }}
    >
      <div className="card-content">
        <span className="quote-mark">“</span>
        <p>{item.content}</p>
        <span className="quote-mark">”</span>
      </div>
    </div>
  );
};

const CardGrid = ({ items, selectedChatId, onCardClick }) => {
  // Assign a color to each item
  const itemColors = items.map((item) =>
    getDeterministicColor(item.chat_id + item.datetime)
  );

  // Divide items into 3 columns
  const columns = [[], [], []];
  items.forEach((item, index) => {
    columns[index % 3].push({ ...item, backgroundColor: itemColors[index] });
  });

  return (
    <div className="grid-wrapper">
      <div className="masonry-grid">
        {selectedChatId && (
          <div className="backdrop" onClick={() => onCardClick(null)}></div>
        )}
        {columns.map((column, colIndex) => (
          <div key={colIndex} className="masonry-column">
            {column.map((item, index) =>
              item.type === "link" ? (
                <div key={index}>
                  <LinkCard
                    item={item}
                    clickClassName={`link-card ${
                      selectedChatId === item.chat_id ? "selected" : ""
                    }`}
                    onCardClick={onCardClick}
                  />
                  <CardMeta
                    datetime={item.datetime}
                    chat_id={item.chat_id}
                    clickClassName={`card-meta ${
                      selectedChatId === item.chat_id ? "selected" : ""
                    }`}
                  />
                </div>
              ) : (
                <div key={index}>
                  <Card
                    item={item}
                    clickClassName={`card ${
                      selectedChatId === item.chat_id ? "selected" : ""
                    }`}
                    onCardClick={onCardClick}
                    backgroundColor={item.backgroundColor}
                  />
                  <CardMeta
                    datetime={item.datetime}
                    chat_id={item.chat_id}
                    clickClassName={`card-meta ${
                      selectedChatId === item.chat_id ? "selected" : ""
                    }`}
                  />
                </div>
              )
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default CardGrid;
