import tkinter as tk
from tkinter import messagebox, ttk
from services import AuthManager, BiometricService, MemberManager, SavingsManager, LoanManager, ReportingEngine

class SaccoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SACCO Financial Management System")
        self.geometry("700x500")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize UI Frames
        self.frames = {}
        for F in (LoginFrame, RegisterFrame, MemberDashboard, AdminDashboard):
            frame = F(parent=self, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, page_class):
        """Raises the selected frame to the top of the GUI."""
        frame = self.frames[page_class]
        frame.tkraise()
        if hasattr(frame, "refresh"):
            frame.refresh()


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="SACCO Login", font=("Arial", 24, "bold")).pack(pady=40)

        tk.Label(self, text="Member ID:").pack(pady=5)
        self.entry_id = tk.Entry(self)
        self.entry_id.pack()

        tk.Label(self, text="Password:").pack(pady=5)
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.pack()

        tk.Button(self, text="Login", command=self.attempt_login, width=15, bg="blue", fg="white").pack(pady=20)
        tk.Button(self, text="Register New Account", command=lambda: controller.show_frame(RegisterFrame), width=20).pack()

    def attempt_login(self):
        try:
            member_id = int(self.entry_id.get())
            password = self.entry_password.get()

            if AuthManager.login(member_id, password):
                if AuthManager.is_admin():
                    self.controller.show_frame(AdminDashboard)
                else:
                    self.controller.show_frame(MemberDashboard)
                self.entry_id.delete(0, tk.END)
                self.entry_password.delete(0, tk.END)
            else:
                messagebox.showerror("Login Failed", "Invalid Member ID or Password.")
        except ValueError:
            messagebox.showerror("Input Error", "Member ID must be a number.")


class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Register Member", font=("Arial", 20, "bold")).pack(pady=20)

        fields = ["Full Name:", "Phone Number:", "Email:", "Password:"]
        self.entries = {}
        
        for field in fields:
            tk.Label(self, text=field).pack()
            entry = tk.Entry(self, show="*" if field == "Password:" else "")
            entry.pack(pady=2)
            self.entries[field] = entry

        tk.Label(self, text="Role:").pack()
        self.role_var = tk.StringVar(value="Member")
        ttk.Combobox(self, textvariable=self.role_var, values=["Member", "Admin"], state="readonly").pack()

        tk.Button(self, text="Capture Biometrics & Register", command=self.register_user, bg="green", fg="white").pack(pady=20)
        tk.Button(self, text="Back to Login", command=lambda: controller.show_frame(LoginFrame)).pack()

    def register_user(self):
        full_name = self.entries["Full Name:"].get()
        phone = self.entries["Phone Number:"].get()
        email = self.entries["Email:"].get()
        password = self.entries["Password:"].get()
        role = self.role_var.get()

        member_id = MemberManager.register_member(full_name, phone, email, password, role)
        if member_id:
            messagebox.showinfo("Biometrics", "Please look at the webcam. Capturing facial profile...")
            if BiometricService.register_biometrics(member_id):
                messagebox.showinfo("Success", f"Registration Complete! Your Member ID is: {member_id}")
                self.controller.show_frame(LoginFrame)
            else:
                messagebox.showwarning("Biometric Warning", "Account created, but facial registration failed. Please update later.")
                self.controller.show_frame(LoginFrame)
        else:
            messagebox.showerror("Error", "Registration failed. Check inputs.")


class MemberDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.lbl_welcome = tk.Label(self, text="", font=("Arial", 18, "bold"))
        self.lbl_welcome.pack(pady=20)

        self.lbl_balance = tk.Label(self, text="Savings Balance: KES 0.00", font=("Arial", 14))
        self.lbl_balance.pack(pady=10)

        tk.Button(self, text="Deposit 1000 KES", command=self.deposit, width=20).pack(pady=5)
        tk.Button(self, text="Apply for 5000 KES Loan", command=self.apply_loan, width=20).pack(pady=5)
        tk.Button(self, text="Logout", command=self.logout, width=20, bg="red", fg="white").pack(pady=20)

    def refresh(self):
        if AuthManager.current_user:
            self.lbl_welcome.config(text=f"Welcome, {AuthManager.current_user.full_name}")
            balance = SavingsManager.get_balance(AuthManager.current_user.member_id)
            self.lbl_balance.config(text=f"Savings Balance: KES {balance:.2f}")

    def deposit(self):
        if SavingsManager.deposit(AuthManager.current_user.member_id, 1000.0):
            messagebox.showinfo("Success", "Deposited 1000 KES successfully.")
            self.refresh()

    def apply_loan(self):
        if LoanManager.apply_loan(AuthManager.current_user.member_id, 5000.0):
            messagebox.showinfo("Success", "Loan application submitted. Pending admin approval.")

    def logout(self):
        AuthManager.logout()
        self.controller.show_frame(LoginFrame)


class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.lbl_welcome = tk.Label(self, text="", font=("Arial", 18, "bold"), fg="blue")
        self.lbl_welcome.pack(pady=20)

        tk.Label(self, text="Administrative Controls", font=("Arial", 14)).pack(pady=10)

        tk.Button(self, text="Approve Pending Loan (Requires Biometrics)", command=self.trigger_biometric_approval, bg="orange").pack(pady=10)
        
        self.lbl_stats = tk.Label(self, text="")
        self.lbl_stats.pack(pady=20)

        tk.Button(self, text="Logout", command=self.logout, width=20, bg="red", fg="white").pack(pady=20)

    def refresh(self):
        if AuthManager.current_user:
            self.lbl_welcome.config(text=f"Admin Panel: {AuthManager.current_user.full_name}")
            savings = ReportingEngine.get_total_savings()
            loans = ReportingEngine.get_total_loans()
            self.lbl_stats.config(text=f"System Stats\nTotal Savings: KES {savings:.2f}\nApproved Loans: KES {loans:.2f}")

    def trigger_biometric_approval(self):
        """Uses a Toplevel window to warn the Admin before activating the webcam."""
        popup = tk.Toplevel(self)
        popup.title("Security Check")
        popup.geometry("300x150")
        
        tk.Label(popup, text="High-Privilege Action Detected.", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(popup, text="Webcam will activate for verification.").pack(pady=5)
        
        def run_approval():
            popup.destroy()
            if LoanManager.approve_loan(1): # Hardcoded Loan ID 1 for testing simplicity
                messagebox.showinfo("Success", "Identity Verified. Loan Approved.")
                self.refresh()
            else:
                messagebox.showerror("Access Denied", "Biometric match failed or unauthorized.")

        tk.Button(popup, text="Start Facial Scan", command=run_approval, bg="green", fg="white").pack(pady=10)

    def logout(self):
        AuthManager.logout()
        self.controller.show_frame(LoginFrame)


if __name__ == "__main__":
    app = SaccoApp()
    app.mainloop()