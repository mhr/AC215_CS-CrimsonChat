// store.js

import { create } from "zustand";

const useStore = create((set) => ({
  // App.js
  isLoaded: false,
  currentPage: "Login",
  selectedPokemon: null,
  // Chatpage.jsx
  showError: false,
  fadeOut: false,
  selectedChatId: null,
  showChatModal: false,
  userQuery: "",
  items: [],
  // ChatInterface.js
  messages: [],
  displayedResponse: "",
  // ChatModal.jsx
  isFadingOut: false,
  notes: [],
  // SideBar.jsx
  isPopoverOpen: false,
  popoverPosition: { top: 0, left: 0 },

  // TypeBar.jsx
  inputValue: "",
  // setters
  setIsLoaded: (isLoaded) => set({ isLoaded }),
  setCurrentPage: (currentPage) => set({ currentPage }),

  setShowError: (showError) => set({ showError }),
  setFadeOut: (fadeOut) => set({ fadeOut }),
  setSelectedChatId: (selectedChatId) => set({ selectedChatId }),
  setShowChatModal: (showChatModal) => set({ showChatModal }),
  setUserQuery: (userQuery) => set({ userQuery }),
  setItems: (items) => set({ items }),

  setMessages: (messages) => set({ messages }),
  appendMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  clearAllMessages: () => set({ messages: [] }),
  setDisplayedResponse: (displayedResponse) => set({ displayedResponse }),
  updateDisplayedResponse: (updater) =>
    set((state) => ({
      displayedResponse:
        typeof updater === "function"
          ? updater(state.displayedResponse)
          : updater,
    })),

  setIsFadingOut: (isFadingOut) => set({ isFadingOut }),
  setNotes: (notes) => set({ notes }),
  addNote: (note) => set((state) => ({ notes: [...state.notes, note] })),
  setIsPopoverOpen: (isPopoverOpen) =>
    set((state) => ({
      isPopoverOpen:
        typeof isPopoverOpen === "function"
          ? isPopoverOpen(state.isPopoverOpen)
          : isPopoverOpen,
    })),
  setPopoverPosition: (popoverPosition) => set({ popoverPosition }),
  setInputValue: (inputValue) => set({ inputValue }),
}));

export default useStore;
