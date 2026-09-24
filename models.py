class Member:
    def __init__(self, member_id, full_name, phone, email, date_registered=None):
        self.member_id = member_id
        self.full_name = full_name
        self.phone = phone
        self.email = email
        self.date_registered = date_registered

class SavingsAccount:
    def __init__(self, savings_id, member_id, balance, last_updated=None):
        self.savings_id = savings_id
        self.member_id = member_id
        self.balance = balance
        self.last_updated = last_updated

class Loan:
    def __init__(self, loan_id, member_id, amount, application_date, status, balance):
        self.loan_id = loan_id
        self.member_id = member_id
        self.amount = amount
        self.application_date = application_date
        self.status = status
        self.balance = balance

class Transaction:
    def __init__(self, transaction_id, member_id, transaction_type, amount, date=None):
        self.transaction_id = transaction_id
        self.member_id = member_id
        self.transaction_type = transaction_type
        self.amount = amount
        self.date = date