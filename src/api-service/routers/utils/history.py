# history.py

from datetime import datetime


class Message:
    def __init__(self, role, content, links=None):
        self.role = role  # 'user', 'assistant', or 'system'
        self.content = content  # The message text
        self.links = links or []  # List of reference links (if any)
        self.timestamp = datetime.now()  # Timestamp of the message


class History:
    def __init__(self):
        self.messages = []  # List to store Message instances

    def add_message(self, role, content, links=None):
        """Add a new message to the history."""
        message = Message(role, content, links)
        self.messages.append(message)

    def get_conversation(self):
        """Get the conversation history formatted for the language model."""
        conversation = ""
        for message in self.messages:
            if message.role == "user":
                conversation += f"User: {message.content}\n"
            elif message.role == "assistant":
                conversation += f"Assistant: {message.content}\n"
            elif message.role == "system":
                conversation += f"System: {message.content}\n"
        return conversation.strip()

    def get_messages(self):
        """Get all messages as a list of dictionaries (for display)."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "links": msg.links,
                "timestamp": msg.timestamp,
            }
            for msg in self.messages
        ]

