import json
import os
from typing import Dict, Optional
from models import User, Account

class Database:
    """Handles storing and retrieving user and account data."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}  # Stores users by username
        self.accounts: Dict[str, Account] = {}  # Stores accounts by account ID
        self.load_data()  # Load data from files at startup
        
    def load_data(self):
        """Loads user and account data from JSON files (if they exist)."""
        
        # Load user data
        if os.path.exists("users.json"):
            try:
                with open("users.json", "r") as f:
                    user_data = json.load(f)
                for username, data in user_data.items():
                    self.users[username] = User(
                        username=username,
                        password_hash=bytes.fromhex(data["password_hash"]),
                        salt=bytes.fromhex(data["salt"]),
                        role=data["role"],
                        account_id=data.get("account_id")  # May be None
                    )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Warning: Failed to load 'users.json'. Error: {e}")

        # Load account data
        if os.path.exists("accounts.json"):
            try:
                with open("accounts.json", "r") as f:
                    account_data = json.load(f)
                for account_id, data in account_data.items():
                    self.accounts[account_id] = Account(
                        account_id=account_id,
                        owner_username=data["owner_username"],
                        balance=data.get("balance", 0.0),  # Default to 0 if missing
                        transactions=data.get("transactions", [])  # Default to empty list
                    )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"❌ Warning: Failed to load 'accounts.json'. Error: {e}")
    
    def save_data(self):
        """Saves user and account data to JSON files."""
        
        # Prepare user data for JSON storage
        user_data = {
            username: {
                "password_hash": user.password_hash.hex(),
                "salt": user.salt.hex(),
                "role": user.role,
                "account_id": user.account_id
            }
            for username, user in self.users.items()
        }
        
        try:
            with open("users.json", "w") as f:
                json.dump(user_data, f, indent=4)
        except Exception as e:
            print(f"❌ Error: Failed to save 'users.json'. {e}")

        # Prepare account data for JSON storage
        account_data = {
            account_id: {
                "owner_username": account.owner_username,
                "balance": round(account.balance, 2),  # Ensure two decimal places
                "transactions": account.transactions
            }
            for account_id, account in self.accounts.items()
        }
        
        try:
            with open("accounts.json", "w") as f:
                json.dump(account_data, f, indent=4)
        except Exception as e:
            print(f"❌ Error: Failed to save 'accounts.json'. {e}")
