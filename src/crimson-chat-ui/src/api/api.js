// Long Dummy AI Responses with URLs
const dummyResponses = [
    "I'm here to help! Let me know what you need, and I'll do my best to assist.",
    "That's a fascinating perspective! Have you thought about exploring it further? Check out this article: https://example.com/intriguing-topic",
    "I appreciate you sharing that. For more on this topic, you might find this useful: https://example.com/resources",
    "It sounds like you're on to something intriguing! Here's a similar discussion: https://www.example.com/articles/complex-discussions",
    "Simulated response: You’re bringing up some good points, let’s dive deeper! For background, see https://deepdive.example.com",
    "This conversation is helping me learn and grow. Thank you for that! If you're curious, you can read more here: https://www.example.com/learn-more",
    "Every response you give enriches this discussion. Let me know if I can clarify anything, or take a look at https://www.example.com/community-ideas.",
    "It seems like we're touching on some complex ideas. I'm here to break it down with you. Here's an in-depth article: https://insights.example.com/complex-ideas",
    "Interesting take! What led you to this viewpoint? Here's a related link: https://example.com/related-viewpoints",
    "Thank you for being open in this conversation. I'm here to support your insights. You might find this helpful too: https://support.example.com/resources"
];

const dummyCards = [
    { 
        type: 'quote', 
        datetime: '2023-11-13T09:00:00Z', 
        chat_id: '1234', 
        content: 'The best time to plant a tree was 20 years ago. The second best time is now. Never have I been more stupid than today. Very inspiration, very good.' 
    },
    { 
        type: 'link', 
        url: 'https://techcrunch.com',
        datetime: '2023-11-13T10:30:00Z',
        chat_id: '567', 
    },
    { 
        type: 'quote', 
        datetime: '2023-11-13T10:30:00Z', 
        chat_id: '1234', 
        content: 'Focus on being productive instead of busy.' 
    },
    { 
        type: 'link', 
        url: 'https://unsplash.com/photos/Y8lCoTRgHPE',
        datetime: '2023-11-13T10:30:00Z', 
        chat_id: '5678',
    },
    { 
        type: 'quote', 
        datetime: '2023-11-13T11:45:00Z', 
        chat_id: '5678', 
        content: 'Your limitation—it’s only your imagination.' 
    },
    { 
        type: 'link', 
        url: 'https://coursera.org',
        datetime: '2023-11-13T10:30:00Z',
        chat_id: '567', 
    },
    { 
        type: 'quote', 
        datetime: '2023-11-14T08:15:00Z', 
        chat_id: '567', 
        content: 'Push yourself, because no one else is going to do it for you.' 
    },
    { 
        type: 'link', 
        url: 'https://medium.com',
        datetime: '2023-11-14T09:00:00Z',
        chat_id: '1234',
    },
    { 
        type: 'quote', 
        datetime: '2023-11-14T09:00:00Z', 
        chat_id: '1234', 
        content: 'Great things never come from comfort zones.' 
    },
    { 
        type: 'link', 
        url: 'https://news.ycombinator.com',
        datetime: '2023-11-14T10:00:00Z',
        chat_id: '789',
    },
    { 
        type: 'quote', 
        datetime: '2023-11-14T10:30:00Z', 
        chat_id: '789', 
        content: 'Dream it. Wish it. Do it. Sometimes achieving a dream requires persistence, patience, and an extraordinary amount of coffee. Never stop believing in yourself, even if the road ahead seems endless.' 
    },
    { 
        type: 'link', 
        url: 'https://stackoverflow.com',
        datetime: '2023-11-14T11:00:00Z',
        chat_id: '5678',
    },
    { 
        type: 'quote', 
        datetime: '2023-11-14T11:45:00Z', 
        chat_id: '5678', 
        content: 'Success doesn’t just find you. You have to go out and get it. The journey is not always about reaching the destination quickly, but about embracing the growth that comes along the way.' 
    },
    { 
        type: 'quote', 
        datetime: '2023-11-14T12:00:00Z', 
        chat_id: '567', 
        content: 'The harder you work for something, the greater you’ll feel when you achieve it. Remember, success is a culmination of small, consistent efforts that build up over time.' 
    },
    { 
        type: 'link', 
        url: 'https://example.com',
        datetime: '2023-11-14T12:30:00Z',
        chat_id: '567', 
    },
    { 
        type: 'quote', 
        datetime: '2023-11-14T13:00:00Z', 
        chat_id: '1234', 
        content: 'Don’t stop when you’re tired. Stop when you’re done. Even on the toughest days, remember why you started. Keep moving forward, one step at a time.' 
    },
    { 
        type: 'quote', 
        datetime: '2023-11-15T08:00:00Z', 
        chat_id: '1234', 
        content: 'Opportunities don’t happen. You create them. Stay alert, be proactive, and don’t wait for the perfect moment—it may never come. Take a leap of faith and see where it takes you.' 
    },
    { 
        type: 'link', 
        url: 'https://github.com',
        datetime: '2023-11-15T09:30:00Z',
        chat_id: '789',
    },
    { 
        type: 'quote', 
        datetime: '2023-11-15T10:00:00Z', 
        chat_id: '5678', 
        content: 'Hardships often prepare ordinary people for an extraordinary destiny. In every struggle lies an opportunity to rise stronger and better than before.' 
    },
    { 
        type: 'link', 
        url: 'https://openai.com',
        datetime: '2023-11-15T11:00:00Z',
        chat_id: '1234',
    },
    { 
        type: 'quote', 
        datetime: '2023-11-15T12:00:00Z', 
        chat_id: '567', 
        content: 'It’s not about perfect. It’s about effort. And when you bring that effort every single day, that’s where transformation happens. That’s how change occurs.' 
    },
    { 
        type: 'quote', 
        datetime: '2023-11-15T12:30:00Z', 
        chat_id: '789', 
        content: 'Success is not in what you have, but who you are. Your resilience, determination, and kindness will define your legacy.' 
    },
    { 
        type: 'quote', 
        datetime: '2023-11-15T13:00:00Z', 
        chat_id: '5678', 
        content: 'Motivation is what gets you started. Habit is what keeps you going. Build habits that align with your dreams, and success will follow.' 
    },
    { 
        type: 'link', 
        url: 'https://npmjs.com',
        datetime: '2023-11-15T14:00:00Z',
        chat_id: '1234',
    }
];


// used in ChatInterface.jsx in ChatModal folder
export const sendMessageToAI = async (userMessage) => {
    console.log("Sending user message to AI:", userMessage);

    // Select a random response from the dummy responses
    const selectedResponse = dummyResponses[Math.floor(Math.random() * dummyResponses.length)];

    // Simulate delay and return response
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(selectedResponse);
        }, 100); // Simulated 1-second delay
    });

    // Example: Replace the above logic with an actual API call
    /*
    try {
        const response = await fetch('https://your-ai-api-endpoint.com/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage }),
        });
        const data = await response.json();
        return data.reply; // Replace 'reply' with the actual response key
    } catch (error) {
        console.error('Error fetching AI response:', error);
        throw new Error('Failed to fetch AI response.');
    }
    */
};




/**
 * Dummy function to save notes. 
 * Replace with actual API call implementation. Used in in NotesSection under ChatModal.
 *
 * @param {Array} notes - Array of notes to save
 * @returns {Promise<string>} A promise resolving to a success message
 */
export const saveNotes = async (notes) => {
    console.log('Saving notes:', notes); // Log the notes for debugging
  
    // Simulate API delay
    return new Promise((resolve) => {
      setTimeout(() => {
        // Replace this block with actual API call logic
        console.log('Dummy save successful!');
        resolve('Notes saved successfully (dummy response)');
      }, 1000); // Simulated delay of 1 second
    });
  };


/**
 * Simulate validating the password and storing a key on success.
 * This is a dummy implementation for testing purposes. Used in App.js, Login component
 *
 * @param {string} password - The password to validate
 * @returns {Promise<boolean>} A promise that resolves to `true` if validation is successful, or `false` otherwise
 */
export const validatePassword = async (password) => {
    console.log('Simulating password validation with:', password);
  
    return new Promise((resolve) => {
      setTimeout(() => {
        if (password === 'ligma') {
          // Simulate receiving a key from the server
          const dummyKey = 'dummy_auth_key_12345';
          console.log('Dummy key received:', dummyKey);
  
          // Store the key in localStorage (or sessionStorage)
          localStorage.setItem('authKey', dummyKey);
  
          resolve(true); // Validation successful
        } else {
          console.log('Dummy validation failed: Invalid password');
          resolve(false); // Validation failed
        }
      }, 1000); // Simulated delay of 1 second
    });
  };

  /**
 * Get the stored authentication key. Not used anywhere atm
 *
 * @returns {string|null} The stored key, or `null` if no key is found
 */
export const getAuthKey = () => localStorage.getItem('authKey');



/**
 * Handle the logout by removing the session key from localStorage.
 * Optionally, call the server to invalidate the session. Called in App.js
 *
 * @returns {Promise<void>} A promise that resolves when logout is complete
 */
export const logout = async () => {
    try {
      // Optional: Call an API to inform the server about the logout
      // const response = await fetch('/api/logout', { method: 'POST' });
      // if (!response.ok) throw new Error('Failed to logout from the server');
  
      // Remove the auth key from localStorage
      localStorage.removeItem('authKey');
      
      console.log('Logged out successfully');
    } catch (error) {
      console.error('Error during logout:', error);
      throw error;  // Optionally handle error
    }
  };


  // api.js

/**
 * Dummy function to fetch cards
 * This function simulates an API call and returns a list of sample items.
 * Called in ChatPage to fetch initial card data.
 */
export const fetchCards = async () => {
    // Simulating a delay for an API call
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(dummyCards);
        }, 1000); // Simulates 1 second delay
    });
};
