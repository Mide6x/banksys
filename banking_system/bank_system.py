import uuid
import logging
from crypto_utils import CryptoManager
from database import Database
from models import User, Account

# ========== LOGGING CONFIGURATION ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankingSystem:
    """A simple banking system for user management, transactions, and account handling."""

    def __init__(self):
        """Initialize the banking system with encryption and database handling."""
        self.crypto = CryptoManager()
        self.db = Database()
        self.current_user = None  # Stores the currently logged-in user
    
    # ========== USER MANAGEMENT ==========
    
    def register_user(self, username: str, password: str, role: str = "client") -> bool:
        """Registers a new user. If the role is 'client', an account is created."""
        
        # Basic input validation
        if not username or not password:
            logger.warning("❌ Registration failed: Username and password are required.")
            return False

        if username in self.db.users:
            logger.warning(f"❌ Registration failed: Username '{username}' already exists.")
            return False

        # Secure password hashing
        try:
            password_hash, salt = self.crypto.hash_password(password)
        except Exception as e:
            logger.error(f"❌ Error hashing password: {e}")
            return False

        # Create the user
        user = User(username=username, password_hash=password_hash, salt=salt, role=role)

        # If the user is a client, create a bank account
        if role == "client":
            account_id = str(uuid.uuid4())
            account = Account(account_id=account_id, owner_username=username, balance=0.0, transactions=[])
            user.account_id = account_id
            self.db.accounts[account_id] = account
            logger.info(f"✅ Account created for '{username}' with ID {account_id}")

        # Store user in the database
        self.db.users[username] = user
        self.db.save_data()
        logger.info(f"✅ User '{username}' registered successfully.")
        return True

    def login(self, username: str, password: str) -> bool:
        """Authenticates a user by verifying credentials."""
        
        if username not in self.db.users:
            logger.warning("❌ Login failed: Username not found.")
            return False

        user = self.db.users[username]

        try:
            password_hash, _ = self.crypto.hash_password(password, user.salt)
        except Exception as e:
            logger.error(f"❌ Error hashing password during login: {e}")
            return False

        if password_hash == user.password_hash:
            self.current_user = user
            logger.info(f"✅ User '{username}' logged in successfully.")
            return True

        logger.warning("❌ Login failed: Incorrect password.")
        return False

    # ========== TRANSACTIONS ==========
    
    def transfer_money(self, recipient_username: str, amount: float, description: str) -> bool:
        """Transfers money between accounts."""

        if not self.current_user or self.current_user.role != 'client':
            logger.warning("❌ Transfer failed: User is not a client or not logged in.")
            return False

        if recipient_username not in self.db.users:
            logger.warning(f"❌ Transfer failed: Recipient '{recipient_username}' not found.")
            return False

        sender_account = self.db.accounts[self.current_user.account_id]
        recipient_account = self.db.accounts[self.db.users[recipient_username].account_id]

        if sender_account.balance < amount:
            logger.warning("❌ Transfer failed: Insufficient funds.")
            return False

        # Encrypt transaction description but keep plaintext for UI
        encrypted_description = self.crypto.encrypt_data(description).hex()

        # Record transactions for both parties
        sender_account.add_transaction(amount, "debit", {
            "plaintext": description,
            "encrypted": encrypted_description
        })
        recipient_account.add_transaction(amount, "credit", {
            "plaintext": description,
            "encrypted": encrypted_description
        })

        self.db.save_data()
        logger.info(f"✅ Transfer completed: ${amount:.2f} from '{self.current_user.username}' to '{recipient_username}'.")
        return True

    # ========== EMPLOYEE FUNCTIONS ==========
    
    def process_transaction(self, username: str, amount: float, transaction_type: str, description: str) -> bool:
        """Allows employees to process deposits/withdrawals for customers."""

        if not self.current_user or self.current_user.role != "employee":
            logger.warning("❌ Transaction failed: Only employees can process transactions.")
            return False
        
        if username not in self.db.users:
            logger.warning(f"❌ Transaction failed: Customer '{username}' not found.")
            return False
        
        customer = self.db.users[username]
        if not customer.account_id:
            logger.warning(f"❌ Transaction failed: Customer '{username}' has no account.")
            return False

        account = self.db.accounts[customer.account_id]

        if transaction_type == "withdrawal" and account.balance < amount:
            logger.warning("❌ Transaction failed: Insufficient funds.")
            return False

        account.add_transaction(amount, "debit" if transaction_type == "withdrawal" else "credit", {
            "plaintext": f"{transaction_type.capitalize()} - {description}",
            "encrypted": self.crypto.encrypt_data(description).hex()
        })

        self.db.save_data()
        logger.info(f"✅ {transaction_type.capitalize()} of ${amount:.2f} processed for '{username}'.")
        return True

    # ========== ADMIN FUNCTIONS ==========
    
    def list_users(self) -> list:
        """Allows admins to list all users."""
        
        if not self.current_user or self.current_user.role != "admin":
            logger.warning("❌ Access denied: Admin privileges required.")
            return []
        
        return [{"username": username, "role": user.role, "has_account": bool(user.account_id)} for username, user in self.db.users.items()]

    def change_user_role(self, username: str, new_role: str) -> bool:
        """Allows admins to change user roles."""

        if not self.current_user or self.current_user.role != "admin":
            logger.warning("❌ Access denied: Admin privileges required.")
            return False

        if username not in self.db.users:
            logger.warning(f"❌ User '{username}' not found.")
            return False

        if new_role not in ["client", "employee", "admin"]:
            logger.warning(f"❌ Invalid role: '{new_role}'. Must be 'client', 'employee', or 'admin'.")
            return False

        self.db.users[username].role = new_role
        self.db.save_data()
        logger.info(f"✅ User '{username}' role updated to '{new_role}'.")
        return True
