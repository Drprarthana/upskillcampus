"""
Secure Password Manager
A Python-based password management system with AES-256 encryption.

Author: Prarthana Sharma
Version: 1.0.0
Description: Secure Password Manager with Fernet Encryption
"""

import os
import json
from cryptography.fernet import Fernet
from pathlib import Path
import secrets
import string

class EncryptionManager:
    """Manages encryption and decryption of passwords."""
    
    def __init__(self, key=None):
        """Initialize encryption manager with a key."""
        if key:
            self.key = key
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_password(self, password):
        """Encrypt a password."""
        return self.cipher.encrypt(password.encode()).decode()
    
    def decrypt_password(self, encrypted_password):
        """Decrypt a password."""
        return self.cipher.decrypt(encrypted_password.encode()).decode()

class PasswordGenerator:
    """Generates strong random passwords."""
    
    @staticmethod
    def generate_password(length=16):
        """Generate a random strong password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(characters) for _ in range(length))
        return password

class PasswordDatabase:
    """Manages password storage and retrieval."""
    
    def __init__(self, db_file='passwords.json', encryption_manager=None):
        """Initialize password database."""
        self.db_file = db_file
        self.encryption_manager = encryption_manager
        self.passwords = self._load_passwords()
    
    def _load_passwords(self):
        """Load passwords from database file."""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_passwords(self):
        """Save passwords to database file."""
        with open(self.db_file, 'w') as f:
            json.dump(self.passwords, f, indent=4)
    
    def add_password(self, service, username, password):
        """Add a new password entry."""
        if service in self.passwords:
            print(f"Service '{service}' already exists.")
            return False
        
        encrypted_password = self.encryption_manager.encrypt_password(password) if self.encryption_manager else password
        self.passwords[service] = {
            'username': username,
            'password': encrypted_password
        }
        self._save_passwords()
        return True
    
    def retrieve_password(self, service):
        """Retrieve password for a service."""
        if service not in self.passwords:
            print(f"Service '{service}' not found.")
            return None
        
        entry = self.passwords[service]
        password = entry['password']
        
        if self.encryption_manager:
            password = self.encryption_manager.decrypt_password(password)
        
        return {'username': entry['username'], 'password': password}
    
    def list_services(self):
        """List all stored services."""
        return list(self.passwords.keys())
    
    def delete_password(self, service):
        """Delete password entry for a service."""
        if service in self.passwords:
            del self.passwords[service]
            self._save_passwords()
            return True
        return False

class PasswordManagerCLI:
    """Command-line interface for Password Manager."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.encryption_manager = EncryptionManager()
        self.database = PasswordDatabase(encryption_manager=self.encryption_manager)
    
    def run(self):
        """Run the password manager CLI."""
        while True:
            print("\n=== Secure Password Manager ===")
            print("1. Add Password")
            print("2. Retrieve Password")
            print("3. List Services")
            print("4. Delete Password")
            print("5. Generate Password")
            print("6. Exit")
            
            choice = input("\nSelect an option: ")
            
            if choice == '1':
                self.add_password()
            elif choice == '2':
                self.retrieve_password()
            elif choice == '3':
                self.list_services()
            elif choice == '4':
                self.delete_password()
            elif choice == '5':
                self.generate_password()
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")
    
    def add_password(self):
        """Add a new password."""
        service = input("Enter service name: ")
        username = input("Enter username: ")
        password = input("Enter password: ")
        
        if self.database.add_password(service, username, password):
            print(f"Password for '{service}' added successfully.")
    
    def retrieve_password(self):
        """Retrieve a stored password."""
        service = input("Enter service name: ")
        result = self.database.retrieve_password(service)
        
        if result:
            print(f"Username: {result['username']}")
            print(f"Password: {result['password']}")
    
    def list_services(self):
        """List all stored services."""
        services = self.database.list_services()
        if services:
            print("\nStored Services:")
            for i, service in enumerate(services, 1):
                print(f"{i}. {service}")
        else:
            print("No services stored yet.")
    
    def delete_password(self):
        """Delete a password entry."""
        service = input("Enter service name to delete: ")
        if self.database.delete_password(service):
            print(f"Password for '{service}' deleted successfully.")
        else:
            print(f"Service '{service}' not found.")
    
    def generate_password(self):
        """Generate a new password."""
        length = input("Enter password length (default 16): ")
        try:
            length = int(length) if length else 16
            password = PasswordGenerator.generate_password(length)
            print(f"Generated password: {password}")
        except ValueError:
            print("Invalid length. Using default length of 16.")
            print(f"Generated password: {PasswordGenerator.generate_password()}")

if __name__ == "__main__":
    cli = PasswordManagerCLI()
    cli.run()
