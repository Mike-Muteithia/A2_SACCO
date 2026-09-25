import hashlib
import json
import cv2
import face_recognition
import numpy as np
from database import execute_query, fetch_query
from models import Member

class AuthManager:
    current_user = None

    @staticmethod
    def hash_password(password):
        """Hashes passwords using hashlib for secure cryptography."""
        salt = "sacco_2026_usiu" 
        return hashlib.sha256((password + salt).encode()).hexdigest()

    @staticmethod
    def login(member_id, password):
        """Authenticates a user and establishes a session token."""
        member = MemberManager.search_member(member_id)
        if member and member.password_hash == AuthManager.hash_password(password):
            AuthManager.current_user = member
            return True
        return False

    @staticmethod
    def logout():
        """Clears the active session token."""
        AuthManager.current_user = None

    @staticmethod
    def is_authenticated():
        """Validates if an active session exists."""
        return AuthManager.current_user is not None

    @staticmethod
    def is_admin():
        """Validates if the active session holds Admin privileges."""
        return AuthManager.is_authenticated() and AuthManager.current_user.role == 'Admin'

class BiometricService:
    @staticmethod
    def capture_encoding():
        """Captures a frame from the webcam, with a fallback to a local image for WSL."""
        try:
            print("Initializing webcam... Please look at the camera.")
            video_capture = cv2.VideoCapture(0)
            
            # Check if camera opened successfully (will fail in standard WSL2)
            if not video_capture.isOpened():
                print("Webcam unavailable (WSL driver limitation). Falling back to 'sample_face.jpg'...")
                import os
                if not os.path.exists("sample_face.jpg"):
                    print("Error: Please place a picture with a face named 'sample_face.jpg' in this folder.")
                    return None
                
                # Load the static fallback image
                frame = cv2.imread("sample_face.jpg")
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                # Original webcam logic for native Linux/Windows environments
                for _ in range(5):
                    video_capture.read()
                ret, frame = video_capture.read()
                video_capture.release()
                
                if not ret:
                    print("Error: Could not capture image.")
                    return None
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_frame)
            
            if face_locations:
                encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                return encodings[0]
            
            print("No face detected in the frame.")
            return None
        except Exception as e:
            print(f"Biometric Capture Error: {e}")
            return None

    @staticmethod
    def register_biometrics(member_id):
        """Captures and stores facial encoding in the database as a JSON string."""
        encoding = BiometricService.capture_encoding()
        if encoding is not None:
            encoding_json = json.dumps(encoding.tolist())
            query = "UPDATE members SET biometric_encoding = ? WHERE member_id = ?"
            execute_query(query, (encoding_json, member_id))
            return True
        return False

    @staticmethod
    def verify_admin_action():
        """Prompts for biometric verification during high-privilege actions."""
        if not AuthManager.is_admin() or not AuthManager.current_user.biometric_encoding:
            print("Admin biometric data missing or user not authorized.")
            return False
            
        known_encoding = np.array(json.loads(AuthManager.current_user.biometric_encoding))
        
        print("\n[SECURITY] High-privilege action detected.")
        current_encoding = BiometricService.capture_encoding()
        
        if current_encoding is None:
            return False
            
        matches = face_recognition.compare_faces([known_encoding], current_encoding, tolerance=0.5)
        return matches[0]

class MemberManager:
    @staticmethod
    def register_member(full_name, phone, email, password, role='Member'):
        try:
            if not full_name or not phone or not password:
                raise ValueError("Full name, phone, and password are required.")
            
            password_hash = AuthManager.hash_password(password)
            query = "INSERT INTO members (full_name, phone, email, password_hash, role) VALUES (?, ?, ?, ?, ?)"
            member_id = execute_query(query, (full_name, phone, email, password_hash, role))
            
            if member_id:
                execute_query("INSERT INTO savings (member_id, balance) VALUES (?, 0.0)", (member_id,))
                return member_id
            return None
        except Exception as e:
            print(f"Error registering member: {e}")
            return None

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
        if not AuthManager.is_authenticated():
            print("Unauthorized. Please log in.")
            return False
            
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Deposit amount must be greater than zero.")
                
            query_update = "UPDATE savings SET balance = balance + ?, last_updated = CURRENT_TIMESTAMP WHERE member_id = ?"
            execute_query(query_update, (amount, member_id))
            
            query_trans = "INSERT INTO transactions (member_id, transaction_type, amount) VALUES (?, 'Deposit', ?)"
            execute_query(query_trans, (member_id, amount))
            return True
        except Exception as e:
            print(f"Error processing deposit: {e}")
            return False

    @staticmethod
    def get_balance(member_id):
        if not AuthManager.is_authenticated():
            print("Unauthorized. Please log in.")
            return 0.0
            
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
        if not AuthManager.is_authenticated():
            print("Unauthorized. Please log in.")
            return False
            
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Loan amount must be positive.")
                
            query = "INSERT INTO loans (member_id, amount, status, balance) VALUES (?, ?, 'Pending', ?)"
            execute_query(query, (member_id, amount, amount))
            return True
        except Exception as e:
            print(f"Error applying for loan: {e}")
            return False

    @staticmethod
    def approve_loan(loan_id):
        if not AuthManager.is_admin():
            print("Unauthorized: Only Admins can approve loans.")
            return False
            
        # Enforce biometric verification for high-privilege action
        if not BiometricService.verify_admin_action():
            print("Biometric verification failed. Loan approval aborted.")
            return False
            
        try:
            query = "UPDATE loans SET status = 'Approved' WHERE loan_id = ?"
            execute_query(query, (loan_id,))
            return True
        except Exception as e:
            print(f"Error approving loan: {e}")
            return False

class ReportingEngine:
    @staticmethod
    def get_total_savings():
        try:
            row = fetch_query("SELECT SUM(balance) as total FROM savings", fetchone=True)
            return row['total'] if row and row['total'] else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def get_total_loans():
        try:
            row = fetch_query("SELECT SUM(amount) as total FROM loans WHERE status = 'Approved'", fetchone=True)
            return row['total'] if row and row['total'] else 0.0
        except Exception:
            return 0.0
        