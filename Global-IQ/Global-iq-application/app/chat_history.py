"""
Chat History Management for Global IQ Mobility Advisor
Provides multi-chat functionality and conversation persistence
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid
import chainlit as cl
from auth import get_current_user

# Directory to store chat histories
CHAT_HISTORY_DIR = "chat_histories"

class ChatHistoryManager:
    """Manages multiple chat conversations for users"""
    
    def __init__(self):
        self.ensure_history_directory()
    
    def ensure_history_directory(self):
        """Create chat history directory if it doesn't exist"""
        if not os.path.exists(CHAT_HISTORY_DIR):
            os.makedirs(CHAT_HISTORY_DIR)
    
    def get_user_history_file(self, user_id: str) -> str:
        """Get the path to a user's chat history file"""
        return os.path.join(CHAT_HISTORY_DIR, f"{user_id}_chats.json")
    
    def load_user_chats(self, user_id: str) -> Dict[str, Any]:
        """Load all chat conversations for a user"""
        history_file = self.get_user_history_file(user_id)
        
        if not os.path.exists(history_file):
            return {
                "user_id": user_id,
                "chats": {},
                "active_chat_id": None,
                "created_at": datetime.now().isoformat()
            }
        
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chat history for {user_id}: {e}")
            return {
                "user_id": user_id,
                "chats": {},
                "active_chat_id": None,
                "created_at": datetime.now().isoformat()
            }
    
    def save_user_chats(self, user_id: str, chat_data: Dict[str, Any]):
        """Save all chat conversations for a user"""
        history_file = self.get_user_history_file(user_id)
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving chat history for {user_id}: {e}")
    
    def create_new_chat(self, user_id: str, title: str = None, chat_type: str = "general") -> str:
        """Create a new chat conversation"""
        chat_data = self.load_user_chats(user_id)
        
        # Generate unique chat ID
        chat_id = str(uuid.uuid4())
        
        # Create default title if none provided
        if not title:
            chat_count = len(chat_data["chats"]) + 1
            title = f"Chat {chat_count}"
        
        # Create new chat
        new_chat = {
            "id": chat_id,
            "title": title,
            "type": chat_type,  # "general", "policy", "compensation"
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "metadata": {
                "message_count": 0,
                "last_agent_type": None
            }
        }
        
        # Add to user's chats
        chat_data["chats"][chat_id] = new_chat
        chat_data["active_chat_id"] = chat_id
        
        # Save to file
        self.save_user_chats(user_id, chat_data)
        
        return chat_id
    
    def get_chat(self, user_id: str, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chat conversation"""
        chat_data = self.load_user_chats(user_id)
        return chat_data["chats"].get(chat_id)
    
    def get_active_chat_id(self, user_id: str) -> Optional[str]:
        """Get the currently active chat ID for a user"""
        chat_data = self.load_user_chats(user_id)
        return chat_data.get("active_chat_id")
    
    def set_active_chat(self, user_id: str, chat_id: str) -> bool:
        """Set the active chat for a user"""
        chat_data = self.load_user_chats(user_id)
        
        if chat_id not in chat_data["chats"]:
            return False
        
        chat_data["active_chat_id"] = chat_id
        self.save_user_chats(user_id, chat_data)
        return True
    
    def add_message_to_chat(self, user_id: str, chat_id: str, role: str, content: str, metadata: Dict = None):
        """Add a message to a specific chat"""
        chat_data = self.load_user_chats(user_id)
        
        if chat_id not in chat_data["chats"]:
            return False
        
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "role": role,  # "user", "assistant", "system"
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Add to chat
        chat_data["chats"][chat_id]["messages"].append(message)
        chat_data["chats"][chat_id]["updated_at"] = datetime.now().isoformat()
        chat_data["chats"][chat_id]["metadata"]["message_count"] += 1
        
        # Update last agent type if this was a routing decision
        if metadata and "agent_type" in metadata:
            chat_data["chats"][chat_id]["metadata"]["last_agent_type"] = metadata["agent_type"]
        
        # Save to file
        self.save_user_chats(user_id, chat_data)
        return True
    
    def get_chat_messages(self, user_id: str, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages from a specific chat"""
        chat = self.get_chat(user_id, chat_id)
        if not chat:
            return []
        return chat["messages"]
    
    def list_user_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """List all chats for a user"""
        chat_data = self.load_user_chats(user_id)
        
        # Convert to list and sort by updated_at (most recent first)
        chats = list(chat_data["chats"].values())
        chats.sort(key=lambda x: x["updated_at"], reverse=True)
        
        return chats
    
    def delete_chat(self, user_id: str, chat_id: str) -> bool:
        """Delete a specific chat"""
        chat_data = self.load_user_chats(user_id)
        
        if chat_id not in chat_data["chats"]:
            return False
        
        # Remove chat
        del chat_data["chats"][chat_id]
        
        # If this was the active chat, set a new active chat
        if chat_data["active_chat_id"] == chat_id:
            remaining_chats = list(chat_data["chats"].keys())
            chat_data["active_chat_id"] = remaining_chats[0] if remaining_chats else None
        
        # Save to file
        self.save_user_chats(user_id, chat_data)
        return True
    
    def rename_chat(self, user_id: str, chat_id: str, new_title: str) -> bool:
        """Rename a specific chat"""
        chat_data = self.load_user_chats(user_id)
        
        if chat_id not in chat_data["chats"]:
            return False
        
        chat_data["chats"][chat_id]["title"] = new_title
        chat_data["chats"][chat_id]["updated_at"] = datetime.now().isoformat()
        
        self.save_user_chats(user_id, chat_data)
        return True
    
    def get_chat_summary(self, user_id: str, chat_id: str) -> Dict[str, Any]:
        """Get a summary of a chat (title, message count, last message, etc.)"""
        chat = self.get_chat(user_id, chat_id)
        if not chat:
            return {}
        
        last_message = chat["messages"][-1] if chat["messages"] else None
        
        return {
            "id": chat["id"],
            "title": chat["title"],
            "type": chat["type"],
            "created_at": chat["created_at"],
            "updated_at": chat["updated_at"],
            "message_count": len(chat["messages"]),
            "last_message": last_message["content"][:100] + "..." if last_message and len(last_message["content"]) > 100 else last_message["content"] if last_message else None,
            "last_message_role": last_message["role"] if last_message else None,
            "last_agent_type": chat["metadata"].get("last_agent_type")
        }

# Global instance
chat_manager = ChatHistoryManager()
