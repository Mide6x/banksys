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
    """Routes users to their appropriate menu based on role."""
    if bank.current_user.role == "client":
        handle_client_menu(bank)  # Rename the existing menu function
    elif bank.current_user.role == "employee":
        handle_employee_menu(bank)
    elif bank.current_user.role == "admin":
        handle_admin_menu(bank)

def handle_client_menu(bank):
    """Handles client operations."""
    while True:
        print("\n=== Client Dashboard ===")
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

def handle_employee_menu(bank):
    """Handles employee operations."""
    while True:
        print("\n=== Employee Dashboard ===")
        print("1. Process Customer Transaction")
        print("2. View Customer Info")
        print("3. Logout")
        
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            process_customer_transaction(bank)
        elif choice == "2":
            view_customer_info(bank)
        elif choice == "3":
            print("Logging out...")
            bank.current_user = None
            break
        else:
            print("❌ Invalid choice!")

def process_customer_transaction(bank):
    """Handle customer deposits/withdrawals."""
    print("\n--- Process Transaction ---")
    
    username = input("Enter customer username: ").strip()
    
    print("\nTransaction type:")
    print("1. Deposit")
    print("2. Withdrawal")
    type_choice = input("Choose (1-2): ").strip()
    
    if type_choice not in ["1", "2"]:
        print("❌ Invalid transaction type!")
        return
        
    try:
        amount = float(input("Enter amount: $").strip())
        if amount <= 0:
            print("❌ Amount must be positive!")
            return
    except ValueError:
        print("❌ Invalid amount!")
        return
        
    description = input("Enter transaction description: ").strip()
    
    transaction_type = "deposit" if type_choice == "1" else "withdrawal"
    if bank.process_transaction(username, amount, transaction_type, description):
        print(f"✅ {transaction_type.title()} processed successfully!")
    else:
        print("❌ Transaction failed!")

def view_customer_info(bank):
    """Display customer account information."""
    username = input("\nEnter customer username: ").strip()
    info = bank.get_customer_info(username)
    
    if info:
        print("\n--- Customer Information ---")
        print(f"Username: {info['username']}")
        print(f"Role: {info['role']}")
        if "account_id" in info:
            print(f"Account ID: {info['account_id']}")
            print(f"Balance: ${info['balance']:.2f}")
            print(f"Transaction count: {info['transaction_count']}")
    else:
        print("❌ Customer not found or access denied!")

def handle_admin_menu(bank):
    """Handles admin operations."""
    while True:
        print("\n=== Admin Dashboard ===")
        print("1. List All Users")
        print("2. Change User Role")
        print("3. View Customer Info")  # Admins can do everything employees can
        print("4. Logout")
        
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            list_all_users(bank)
        elif choice == "2":
            change_user_role(bank)
        elif choice == "3":
            view_customer_info(bank)
        elif choice == "4":
            print("Logging out...")
            bank.current_user = None
            break
        else:
            print("❌ Invalid choice!")

def list_all_users(bank):
    """Display all users in the system."""
    users = bank.list_users()
    
    if users:
        print("\n--- All Users ---")
        for user in users:
            account_status = "Has Account" if user["has_account"] else "No Account"
            print(f"• {user['username']} ({user['role']}) - {account_status}")
    else:
        print("❌ Access denied or no users found!")

def change_user_role(bank):
    """Change a user's role."""
    print("\n--- Change User Role ---")
    username = input("Enter username: ").strip()
    print("\nAvailable roles:")
    print("1. Client")
    print("2. Employee")
    print("3. Admin")
    
    role_choice = input("Choose new role (1-3): ").strip()
    
    role_map = {"1": "client", "2": "employee", "3": "admin"}
    if role_choice not in role_map:
        print("❌ Invalid role choice!")
        return
        
    if bank.change_user_role(username, role_map[role_choice]):
        print(f"✅ Role updated for '{username}'!")
    else:
        print("❌ Role change failed!")

if __name__ == "__main__":
    main()
