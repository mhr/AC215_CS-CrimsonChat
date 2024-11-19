import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const API_BASE_URL = process.env.REACT_APP_API_URL;
// const API_BASE_URL = "http://0.0.0.0:8000";

/**
 * Sends a user message and chat history to the AI backend for processing and retrieves a response.
 *
 * @param {string} userMessage - The message entered by the user.
 * @param {string[]} chatHistory - The current chat history to include in the request.
 * @returns {Promise<{response: string, updated_history: string[]}>} A promise that resolves to the AI response and updated chat history.
 * @throws {Error} If the API request fails.
 */
export const sendMessageToAI = async (userMessage, chatHistory) => {
  try {
    console.log(
      "Sending user message and chat history to AI:",
      userMessage,
      chatHistory
    );

    const response = await fetch(`${API_BASE_URL}/llm/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("authKey")}`,
      },
      body: JSON.stringify({
        query: userMessage,
        chat_history: chatHistory.map((message) => message.text),
      }),
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      toast.error(`Failed to fetch AI response: ${errorMessage}`);
      throw new Error(errorMessage);
    }

    const data = await response.json();
    console.log("AI response received:", data);
    return {
      response: data.response,
      updated_history: data.updated_history,
    };
  } catch (error) {
    console.error("Error communicating with AI backend:", error);
    toast.error("Error communicating with AI backend. Please try again.");
    throw new Error("Failed to communicate with AI backend.");
  }
};

/**
 * Dummy function to save notes.
 *
 * @param {Array} notes - Array of notes to save.
 * @returns {Promise<{success: boolean, message: string}>} A promise resolving to a success message.
 */
export const saveNotes = async (notes) => {
  console.log("Saving notes to the backend:", notes);

  // Normalize notes to include all required fields
  const normalizedNotes = notes.map((note) => {
    if (note.type === "link") {
      return {
        type: note.type,
        datetime: note.datetime,
        chat_id: note.chat_id || "", // Ensure chat_id is present
        content: note.url || "", // Ensure content is present
      };
    }
    return note; // Return as is for other types
  });

  try {
    const response = await fetch(`${API_BASE_URL}/save-notes`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("authKey")}`,
      },
      body: JSON.stringify(normalizedNotes),
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      toast.error(`Failed to save notes: ${errorMessage}`);
      return { success: false, message: errorMessage };
    }

    const data = await response.json();
    console.log("Notes saved successfully:", data);
    toast.success(data.message);
    return { success: true, message: data.message };
  } catch (error) {
    console.error("Error saving notes:", error);
    toast.error(
      "Failed to save notes. Please check your connection and try again."
    );
    return { success: false, message: "Failed to connect to the server." };
  }
};

/**
 * Validate the password with the backend and store the auth key on success.
 *
 * @param {string} password - The password to validate.
 * @returns {Promise<boolean>} A promise that resolves to `true` if validation is successful, or `false` otherwise.
 */
export const validatePassword = async (password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ password }),
    });

    if (!response.ok) {
      toast.error("Invalid password. Please try again.");
      return false;
    }

    const data = await response.json();

    if (data.key) {
      localStorage.setItem("authKey", data.key);
      toast.success("Login successful!");
      return true;
    } else {
      toast.error("Failed to retrieve authentication key.");
      return false;
    }
  } catch (error) {
    console.error("Error validating password:", error);
    toast.error("Error validating password. Please check your connection.");
    return false;
  }
};

/**
 * Fetch all notes.
 *
 * @returns {Promise<Array>} A promise that resolves to an array of notes.
 */
export const fetchCards = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/get-notes`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("authKey")}`,
      },
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      toast.error(`Failed to fetch notes: ${errorMessage}`);
      return [];
    }

    const data = await response.json();
    console.log("Notes fetched successfully:", data.notes);

    // Normalize notes to handle type 'link'
    const normalizedNotes = data.notes.map((note) => {
      if (note.type === "link") {
        return {
          type: note.type,
          datetime: note.datetime,
          chat_id: note.chat_id,
          url: note.content || "", // Map 'url' into 'content' for 'link' types
        };
      }

      return note; // Return other types as is
    });
    console.log("prosessed notes: ", normalizedNotes);
    toast.success("Notes loaded successfully.");
    return normalizedNotes;
  } catch (error) {
    console.error("Error fetching notes:", error);
    toast.error("Failed to fetch notes. Please check your connection.");
    return [];
  }
};
/**
 * Handle the logout by removing the session key from localStorage.
 *
 * @returns {Promise<void>} A promise that resolves when logout is complete.
 */
export const logout = async () => {
  try {
    localStorage.removeItem("authKey");
    toast.success("Logged out successfully.");
    console.log("Logged out successfully");
  } catch (error) {
    console.error("Error during logout:", error);
    toast.error("Error during logout. Please try again.");
    throw error;
  }
};
