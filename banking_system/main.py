from bank_system import BankingSystem
import logging

# Set up logging (but keep it simple, like a human might)
logging.basicConfig(level=logging.INFO)

def main():
    """Main function for the banking terminal."""
    bank = BankingSystem()
    
    print("\nWelcome to ArinolaBank Terminal!")
    
    while True:
        print("\n----------------------")
        print(" 1. Register")
        print(" 2. Login")
        print(" 3. Exit")
        print("----------------------")

        choice = input("Select an option (1-3): ").strip()
        
        if choice == '1':
            register_user(bank)
        elif choice == '2':
            login_user(bank)
        elif choice == '3':
            print("Exiting... Have a great day!")
            break
        else:
            print("Invalid option. Try again.")

def register_user(bank):
    """Handles user registration."""
    print("\n--- User Registration ---")
    username = input("Enter a username: ").strip()
    password = input("Enter a password: ").strip()
    role = input("Enter role (client/employee/admin): ").strip().lower()
    
    if not username or not password:
        print("Error: Username and password cannot be empty.")
        return

    if role not in ["client", "employee", "admin"]:
        print("Invalid role. Defaulting to 'client'.")
        role = "client"

    success = bank.register_user(username, password, role)
    if success:
        print(f"✅ User '{username}' registered successfully!")
    else:
        print("❌ Registration failed. Username may already exist.")

def login_user(bank):
    """Handles user login."""
    print("\n--- User Login ---")
    username = input("Enter your username: ").strip()
    password = input("Enter your password: ").strip()
    
    if bank.login(username, password):
        print(f"✅ Welcome back, {username}!")
        handle_logged_in_user(bank)
    else:
        print("❌ Login failed. Please check your credentials.")

def handle_logged_in_user(bank):
    """Handles actions after user logs in."""
    while True:
        print("\n=== User Dashboard ===")
        print("1. View Balance")
        print("2. Transfer Money")
        print("3. View Transactions")
        print("4. Logout")
        
        choice = input("Choose an option: ").strip()
        
        if choice == '1':
            show_balance(bank)
        elif choice == '2':
            transfer_money(bank)
        elif choice == '3':
            view_transactions(bank)
        elif choice == '4':
            print("Logging out...")
            bank.current_user = None
            break
        else:
            print("❌ Invalid choice. Please try again.")

def show_balance(bank):
    """Displays the user's account balance."""
    user = bank.current_user
    if not user or user.role != "client":
        print("❌ Only clients can view balances.")
        return

    account = bank.db.accounts.get(user.account_id)
    if account:
        print(f"💰 Current Balance: ${account.balance:.2f}")
    else:
        print("❌ Account not found.")

def transfer_money(bank):
    """Handles money transfers."""
    user = bank.current_user
    if not user or user.role != "client":
        print("❌ Only clients can transfer money.")
        return

    recipient = input("Enter recipient's username: ").strip()
    
    try:
        amount = float(input("Enter amount to transfer: ").strip())
        if amount <= 0:
            print("❌ Amount must be greater than zero.")
            return
    except ValueError:
        print("❌ Invalid amount entered.")
        return

    description = input("Enter a description: ").strip()
    
    if bank.transfer_money(recipient, amount, description):
        print(f"✅ Transfer of ${amount:.2f} to '{recipient}' successful!")
    else:
        print("❌ Transfer failed. Check your balance and recipient details.")

def view_transactions(bank):
    """Displays transaction history."""
    user = bank.current_user
    if not user or user.role != "client":
        print("❌ Only clients can view transactions.")
        return

    account = bank.db.accounts.get(user.account_id)
    if not account or not account.transactions:
        print("❌ No transactions found.")
        return

    print("\n📜 Transaction History:")
    for tx in account.transactions:
        print(f"- {tx['timestamp']} | {tx['type'].upper()} | ${tx['amount']:.2f}")
        print(f"  Description: {tx['description']}")
        print("  ----------------------")

if __name__ == "__main__":
    main()
