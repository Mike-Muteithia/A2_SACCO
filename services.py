from database import execute_query, fetch_query
from models import Member

class MemberManager:
    @staticmethod
    def register_member(full_name, phone, email):
        try:
            if not full_name or not phone:
                raise ValueError("Full name and phone are required.")
            
            query = "INSERT INTO members (full_name, phone, email) VALUES (?, ?, ?)"
            member_id = execute_query(query, (full_name, phone, email))
            
            # Initialize savings account for the new member automatically
            if member_id:
                execute_query("INSERT INTO savings (member_id, balance) VALUES (?, 0.0)", (member_id,))
                return member_id
            return None
        except Exception as e:
            print(f"Error registering member: {e}")
            return None

    @staticmethod
    def get_all_members():
        try:
            query = "SELECT * FROM members"
            rows = fetch_query(query)
            return [Member(**dict(row)) for row in rows] if rows else []
        except Exception as e:
            print(f"Error fetching members: {e}")
            return []

    @staticmethod
    def search_member(member_id):
        try:
            query = "SELECT * FROM members WHERE member_id = ?"
            row = fetch_query(query, (member_id,), fetchone=True)
            return Member(**dict(row)) if row else None
        except Exception as e:
            print(f"Error searching member: {e}")
            return None

class SavingsManager:
    @staticmethod
    def deposit(member_id, amount):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Deposit amount must be greater than zero.")
            
            if not MemberManager.search_member(member_id):
                raise ValueError("Member not found.")

            query_update = "UPDATE savings SET balance = balance + ?, last_updated = CURRENT_TIMESTAMP WHERE member_id = ?"
            execute_query(query_update, (amount, member_id))

            query_trans = "INSERT INTO transactions (member_id, transaction_type, amount) VALUES (?, 'Deposit', ?)"
            execute_query(query_trans, (member_id, amount))
            return True
        except ValueError as ve:
            print(f"Validation Error: {ve}")
            return False
        except Exception as e:
            print(f"Error processing deposit: {e}")
            return False

    @staticmethod
    def withdraw(member_id, amount):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Withdrawal amount must be greater than zero.")

            balance = SavingsManager.get_balance(member_id)
            if balance < amount:
                raise ValueError("Insufficient funds.")

            query_update = "UPDATE savings SET balance = balance - ?, last_updated = CURRENT_TIMESTAMP WHERE member_id = ?"
            execute_query(query_update, (amount, member_id))

            query_trans = "INSERT INTO transactions (member_id, transaction_type, amount) VALUES (?, 'Withdrawal', ?)"
            execute_query(query_trans, (member_id, amount))
            return True
        except ValueError as ve:
            print(f"Validation Error: {ve}")
            return False
        except Exception as e:
            print(f"Error processing withdrawal: {e}")
            return False

    @staticmethod
    def get_balance(member_id):
        try:
            query = "SELECT balance FROM savings WHERE member_id = ?"
            row = fetch_query(query, (member_id,), fetchone=True)
            return row['balance'] if row else 0.0
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0.0

class LoanManager:
    @staticmethod
    def apply_loan(member_id, amount):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Loan amount must be positive.")
            
            if not MemberManager.search_member(member_id):
                raise ValueError("Member not found.")
                
            query = "INSERT INTO loans (member_id, amount, status, balance) VALUES (?, ?, 'Pending', ?)"
            execute_query(query, (member_id, amount, amount))
            return True
        except Exception as e:
            print(f"Error applying for loan: {e}")
            return False

    @staticmethod
    def approve_loan(loan_id):
        try:
            query = "UPDATE loans SET status = 'Approved' WHERE loan_id = ?"
            execute_query(query, (loan_id,))
            return True
        except Exception as e:
            print(f"Error approving loan: {e}")
            return False

    @staticmethod
    def repay_loan(member_id, loan_id, amount):
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Repayment amount must be positive.")

            query_loan = "SELECT balance, status FROM loans WHERE loan_id = ? AND member_id = ?"
            loan = fetch_query(query_loan, (loan_id, member_id), fetchone=True)
            
            if not loan:
                raise ValueError("Loan not found for this member.")
            if loan['status'] != 'Approved':
                raise ValueError("Loan is not approved.")
            if loan['balance'] <= 0:
                raise ValueError("Loan is already fully repaid.")

            new_balance = max(0, loan['balance'] - amount)
            query_update = "UPDATE loans SET balance = ? WHERE loan_id = ?"
            execute_query(query_update, (new_balance, loan_id))

            query_trans = "INSERT INTO transactions (member_id, transaction_type, amount) VALUES (?, 'Loan Repayment', ?)"
            execute_query(query_trans, (member_id, amount))
            return new_balance
        except ValueError as ve:
            print(f"Validation Error: {ve}")
            return None
        except Exception as e:
            print(f"Error processing repayment: {e}")
            return None

    @staticmethod
    def get_loan_balance(member_id):
        try:
            query = "SELECT * FROM loans WHERE member_id = ?"
            rows = fetch_query(query, (member_id,))
            return [dict(row) for row in rows] if rows else []
        except Exception as e:
            print(f"Error fetching loan details: {e}")
            return []

class ReportingEngine:
    @staticmethod
    def get_total_savings():
        try:
            row = fetch_query("SELECT SUM(balance) as total FROM savings", fetchone=True)
            return row['total'] if row and row['total'] else 0.0
        except Exception as e:
            print(f"Error fetching reporting data: {e}")
            return 0.0

    @staticmethod
    def get_total_loans():
        try:
            row = fetch_query("SELECT SUM(amount) as total FROM loans WHERE status = 'Approved'", fetchone=True)
            return row['total'] if row and row['total'] else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def get_outstanding_loans():
        try:
            row = fetch_query("SELECT SUM(balance) as total FROM loans WHERE status = 'Approved'", fetchone=True)
            return row['total'] if row and row['total'] else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def get_transactions():
        try:
            rows = fetch_query("SELECT * FROM transactions")
            return [dict(row) for row in rows] if rows else []
        except Exception:
            return []