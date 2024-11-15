# CrimsonChat 📚🤖  
A minimalist support bot UI for Harvard students, inspired by the clean and modern design of MyMind's "second brain" tool. CrimsonChat provides a responsive, easy-to-navigate interface for seamless user support interactions.

---

## 🛠️ API and Utilities

**All API functions are located in** `src/api/api.js`. Current functions are dummy placeholders (11/15/2024)  

**Authentication Requirement:**  
An `authKey` is required for all API functions after login. The `authKey` is stored in `localStorage` upon successful login and must be included in the headers of each subsequent API call.

---

#### `validatePassword`
**Purpose:**  
Simulates password validation. On successful validation, stores a dummy authentication key (`authKey`) in `localStorage`.

**Usage:**  
Called during login to validate the user’s input.

**Schema:**  
- **Input:**  
  ```json
  {
    "password": "string"
  }
  ```
- **Output:**  
  ```json
  {
    "success": "boolean",
    "authKey": "string"
  }
  ```
**Implementation Note:**  
The `authKey` is automatically stored in `localStorage` on successful validation. Example key: `"dummy_auth_key_12345"`.

---

#### `fetchCards`
**Purpose:**  
Fetching ALL card data, including both quotes and link previews. (on Backend, store cards in JSON)

**Usage:**  
Used on the `ChatPage` to load card data initially and on refresh.

**Schema:**  
- **Input:**  
  ```json
  {
    "authKey": "string"
  }
  ```
- **Output:**  
  ```json
  [
    {
      "type": "quote | link",
      "datetime": "string (ISO 8601 format)",
      "chat_id": "string",
      "content": "string (for type: 'quote')",
      "url": "string (for type: 'link')"
    }
  ]
  ```

---

#### `sendMessageToAI`
**Purpose:**  
Provides simulated AI responses to user queries.

**Usage:**  
Called within the `ChatInterface` component to generate responses for user messages.

**Schema:**  
- **Input:**  
  ```json
  {
    "authKey": "string",
    "userMessage": "string"
  }
  ```
- **Output:**  
  ```json
  {
    "response": "string"
  }
  ```

---

#### `saveNotes`
**Purpose:**  
Simulates saving user notes based on chat interactions. (on Backend, append cards to cards JSON file)

**Usage:**  
Called within the `NotesSection` component to save and display notes.

**Schema:**  
- **Input:**  
  ```json
  {
    "authKey": "string",
    "notes": [
      {
        "type": "quote | link",
         "datetime": "string (ISO 8601 format)",
         "chat_id": "string",
         "content": "string (for type: 'quote')",
         "url": "string (for type: 'link')"
      }
    ]
  }
  ```
- **Output:**  
  ```json
  {
    "message": "Notes saved successfully (dummy response)"
  }
  ```

---


#### `logout`
**Purpose:**  
Clears the stored `authKey` from `localStorage`. DOESN'T send anything to backend.

**Usage:**  
Triggered when the user logs out from the sidebar settings.

**Schema:**  
- **Input:**  
  No input required.
- **Output:**  
  ```json
  {
    "message": "Logged out successfully"
  }
  ```
**Authentication:**  
The `authKey` is not required for this API.

---

## 🗂 Project Structure

```
crimson-chat-ui/
├── public/
├── src/
│   ├── api/
│   │   └── api.js
│   ├── components/
│   │   ├── CardGrid/
│   │   │   ├── CardGrid.css
│   │   │   └── CardGrid.jsx
│   │   ├── ChatModal/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── ChatModal.css
│   │   │   ├── ChatModal.jsx
│   │   │   └── NotesSection.jsx
│   │   ├── Sidebar/
│   │   │   ├── Sidebar.css
│   │   │   └── Sidebar.jsx
│   │   └── TypeBar/
│   │       ├── TypeBar.css
│   │       └── TypeBar.jsx
│   ├── App.css
│   ├── App.js
│   ├── App.test.js
│   ├── ChatPage.css
│   ├── ChatPage.jsx
│   ├── index.css
│   └── index.js
├── docker-shell.sh
├── Dockerfile
├── Dockerfile.dev
├── jsconfig.json
├── package.json
└── README.md
```

---

## 📜 Key Components

1. **App**  
   - **Location**: `src/App.js`
   - **Purpose**: Main application component that handles authentication and navigation between login and chat views.

2. **Login**  
   - **Location**: `src/components/Login.jsx`
   - **Purpose**: Displays the login interface with a welcome message. It validates user credentials through `validatePassword`.

3. **ChatPage**  
   - **Location**: `src/ChatPage.jsx`
   - **Purpose**: The main chat area, integrating the sidebar, card grid, and chat modal, as well as managing user interactions and API calls.

4. **Sidebar**  
   - **Location**: `src/components/Sidebar`
   - **Purpose**: Provides navigation and settings options, including the logout function.

5. **TypeBar**  
   - **Location**: `src/components/TypeBar`
   - **Purpose**: A text input component for user queries, with an enter-to-submit feature.

6. **CardGrid**  
   - **Location**: `src/components/CardGrid`
   - **Purpose**: Displays a responsive masonry grid of cards, including quotes and link previews (simulated via dummy data).

7. **ChatModal**  
   - **Location**: `src/components/ChatModal`
   - **Purpose**: Modal that opens upon card selection, displaying the main chat interface and a notes section.

8. **ChatInterface**  
   - **Location**: `src/components/ChatModal/ChatInterface.jsx`
   - **Purpose**: The main chat interface within the modal, simulating interactions and responses from the AI.

9. **NotesSection**  
   - **Location**: `src/components/ChatModal/NotesSection.jsx`
   - **Purpose**: Allows users to save and view notes based on chat interactions.

---

## 🛠️ Tech Stack

- **React.js** - Component-based JavaScript library for building the UI.
- **CSS** - Custom styling without frameworks, allowing for flexibility and simplicity.
- **link-preview-js** - Used to generate metadata previews for external links.

---

## 🚀 Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the app**:
   ```bash
   npm start
   ```

3. **Run tests**:
   ```bash
   npm test
   ```

---

### 📝 Additional Notes

- All API interactions are simulated to enable testing without a backend service.
- The project uses custom CSS animations for smooth modal transitions and fade effects.

---
