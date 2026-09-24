from services import MemberManager, SavingsManager, LoanManager, ReportingEngine

def get_int_input(prompt):
    """Safely gets integer input from the user."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_float_input(prompt):
    """Safely gets float input from the user."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid numeric amount.")

def main():
    while True:
        print("\n" + "="*40)
        print("   SACCO Financial Management System")
        print("="*40)
        print("1. Register Member")
        print("2. View Members")
        print("3. Search Member")
        print("4. Deposit Savings")
        print("5. Withdraw Savings")
        print("6. Check Savings Balance")
        print("7. Apply for Loan")
        print("8. Approve Loan")
        print("9. Make Loan Repayment")
        print("10. View Loan Balance")
        print("11. View Transactions")
        print("12. Generate Reports")
        print("13. Exit")
        print("="*40)

        choice = input("Select an option (1-13): ").strip()

        if choice == '1':
            print("\n--- Register Member ---")
            name = input("Enter Full Name: ").strip()
            phone = input("Enter Phone Number: ").strip()
            email = input("Enter Email Address (optional): ").strip()
            member_id = MemberManager.register_member(name, phone, email)
            if member_id:
                print(f"Success! Member registered with ID: {member_id}")
            else:
                print("Failed to register member.")

        elif choice == '2':
            print("\n--- View Members ---")
            members = MemberManager.get_all_members()
            if members:
                for m in members:
                    print(f"ID: {m.member_id} | Name: {m.full_name} | Phone: {m.phone} | Registered: {m.date_registered}")
            else:
                print("No members found.")

        elif choice == '3':
            print("\n--- Search Member ---")
            member_id = get_int_input("Enter Member ID: ")
            member = MemberManager.search_member(member_id)
            if member:
                print(f"ID: {member.member_id}\nName: {member.full_name}\nPhone: {member.phone}\nEmail: {member.email}")
            else:
                print("Member not found.")

        elif choice == '4':
            print("\n--- Deposit Savings ---")
            member_id = get_int_input("Enter Member ID: ")
            amount = get_float_input("Enter Deposit Amount: ")
            if SavingsManager.deposit(member_id, amount):
                print("Deposit successful.")
            else:
                print("Deposit failed.")

        elif choice == '5':
            print("\n--- Withdraw Savings ---")
            member_id = get_int_input("Enter Member ID: ")
            amount = get_float_input("Enter Withdrawal Amount: ")
            if SavingsManager.withdraw(member_id, amount):
                print("Withdrawal successful.")
            else:
                print("Withdrawal failed.")

        elif choice == '6':
            print("\n--- Check Savings Balance ---")
            member_id = get_int_input("Enter Member ID: ")
            balance = SavingsManager.get_balance(member_id)
            print(f"Current Savings Balance: KES {balance:.2f}")

        elif choice == '7':
            print("\n--- Apply for Loan ---")
            member_id = get_int_input("Enter Member ID: ")
            amount = get_float_input("Enter Loan Amount: ")
            if LoanManager.apply_loan(member_id, amount):
                print("Loan application submitted successfully and is pending approval.")
            else:
                print("Loan application failed.")

        elif choice == '8':
            print("\n--- Approve Loan ---")
            loan_id = get_int_input("Enter Loan ID to Approve: ")
            if LoanManager.approve_loan(loan_id):
                print("Loan approved successfully.")
            else:
                print("Failed to approve loan.")

        elif choice == '9':
            print("\n--- Make Loan Repayment ---")
            member_id = get_int_input("Enter Member ID: ")
            loan_id = get_int_input("Enter Loan ID: ")
            amount = get_float_input("Enter Repayment Amount: ")
            new_balance = LoanManager.repay_loan(member_id, loan_id, amount)
            if new_balance is not None:
                print(f"Repayment successful. Remaining Loan Balance: KES {new_balance:.2f}")
            else:
                print("Repayment failed.")

        elif choice == '10':
            print("\n--- View Loan Balance ---")
            member_id = get_int_input("Enter Member ID: ")
            loans = LoanManager.get_loan_balance(member_id)
            if loans:
                for loan in loans:
                    print(f"Loan ID: {loan['loan_id']} | Amount: {loan['amount']} | Status: {loan['status']} | Balance: {loan['balance']}")
            else:
                print("No loans found for this member.")

        elif choice == '11':
            print("\n--- View Transactions ---")
            transactions = ReportingEngine.get_transactions()
            if transactions:
                for t in transactions:
                    print(f"ID: {t['transaction_id']} | Member ID: {t['member_id']} | Type: {t['transaction_type']} | Amount: {t['amount']} | Date: {t['date']}")
            else:
                print("No transactions found.")

        elif choice == '12':
            print("\n--- Generate Reports ---")
            print(f"Total SACCO Savings: KES {ReportingEngine.get_total_savings():.2f}")
            print(f"Total Approved Loans Issued: KES {ReportingEngine.get_total_loans():.2f}")
            print(f"Total Outstanding Loan Balances: KES {ReportingEngine.get_outstanding_loans():.2f}")

        elif choice == '13':
            print("Exiting SACCO System. Goodbye!")
            break

        else:
            print("Invalid choice. Please select a number between 1 and 13.")

if __name__ == "__main__":
    main()