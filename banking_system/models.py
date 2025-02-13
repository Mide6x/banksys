from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class User:
    """Represents a user in the banking system."""
    username: str
    password_hash: bytes
    salt: bytes
    role: str
    account_id: Optional[str] = None  # Clients have accounts, employees/admins may not


@dataclass
class Account:
    """Represents a bank account."""
    account_id: str
    owner_username: str
    balance: float
    transactions: List[dict]

    def add_transaction(self, amount: float, transaction_type: str, description):
        """Adds a transaction and updates the balance accordingly."""

        # Ensure transaction type is valid
        if transaction_type not in ("credit", "debit"):
            raise ValueError(f"Invalid transaction type: {transaction_type}")

        # If description is a dictionary, extract plaintext part
        if isinstance(description, dict):
            description_text = description.get("plaintext", "No description")  # Fallback if missing
        else:
            description_text = description

        # Record the transaction
        transaction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": round(amount, 2),
            "type": transaction_type,
            "description": description_text.strip()
        }
        self.transactions.append(transaction)

        # Update balance
        if transaction_type == "credit":
            self.balance += amount
        elif transaction_type == "debit":
            if self.balance < amount:
                print("⚠️ Warning: Insufficient funds! Transaction still recorded but may be declined.")
            self.balance -= amount

        print(f"✅ Transaction recorded: {transaction_type} ${amount:.2f} for {self.owner_username}")
