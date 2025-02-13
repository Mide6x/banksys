from crypto_utils import CryptoManager
from database import Database
from models import User, Account
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BankingSystem:
    def __init__(self):
        """Initialize banking system with crypto manager and database."""
        self.crypto = CryptoManager()
        self.db = Database()
        self.current_user = None  # Stores logged-in user
    
    def register_user(self, username: str, password: str, role: str = "client") -> bool:
        """Registers a new user. If role is 'client', also creates an account."""
        if not username or not password:
            logger.warning("Username and password are required.")
            return False

        if username in self.db.users:
            logger.warning(f"Username '{username}' already exists.")
            return False

        # Generate hashed password with salt
        try:
            password_hash, salt = self.crypto.hash_password(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            return False

        # Create user object
        user = User(
            username=username,
            password_hash=password_hash,
            salt=salt,
            role=role
        )

        # If the user is a client, create a bank account
        if role == "client":
            account_id = str(uuid.uuid4())
            account = Account(
                account_id=account_id,
                owner_username=username,
                balance=0.0,
                transactions=[]
            )
            user.account_id = account_id
            self.db.accounts[account_id] = account
            logger.info(f"Account created for user '{username}' with ID {account_id}")

        # Store user in database
        self.db.users[username] = user
        self.db.save_data()
        logger.info(f"User '{username}' registered successfully.")
        return True
    
    def login(self, username: str, password: str) -> bool:
        """Authenticates user by verifying username and password."""
        if username not in self.db.users:
            logger.warning("Login failed: Username not found.")
            return False

        user = self.db.users[username]

        try:
            password_hash, _ = self.crypto.hash_password(password, user.salt)
        except Exception as e:
            logger.error(f"Error hashing password during login: {e}")
            return False
        if password_hash == user.password_hash:
            self.current_user = user
            logger.info(f"User '{username}' logged in successfully.")
            return True

        logger.warning("Login failed: Incorrect password.")
        return False
    
    def transfer_money(self, recipient_username: str, amount: float, description: str) -> bool:
        """Transfers money between accounts."""
        if not self.current_user or self.current_user.role != 'client':
            logger.warning("Transfer failed: User is not a client or not logged in.")
            return False

        if recipient_username not in self.db.users:
            logger.warning("Transfer failed: Recipient username not found.")
            return False

        sender_account = self.db.accounts[self.current_user.account_id]
        recipient_account = self.db.accounts[self.db.users[recipient_username].account_id]

        if sender_account.balance < amount:
            logger.warning("Transfer failed: Insufficient funds.")
            return False

        # Encrypt transaction description but keep plaintext for display
        encrypted_description = self.crypto.encrypt_data(description)  # Bytes
        encrypted_description_hex = encrypted_description.hex()  # Store as hex
        
        # Save transaction with both versions
        sender_account.add_transaction(amount, "debit", {
            "plaintext": description,  
            "encrypted": encrypted_description_hex
        })
        recipient_account.add_transaction(amount, "credit", {
            "plaintext": description,
            "encrypted": encrypted_description_hex
        })

        self.db.save_data()
        logger.info(f"Transfer successful: {amount} from '{self.current_user.username}' to '{recipient_username}'.")
        return True

    def get_account_info(self) -> dict:
        """Returns account information for the current user."""
        if not self.current_user:
            logger.warning("Account info failed: No user is logged in.")
            return None
