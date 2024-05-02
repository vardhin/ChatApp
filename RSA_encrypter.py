from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os

def encrypt_message(public_key, message):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

def decrypt_message(private_key, encrypted_message):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message.decode()

def gen_keys(seed):
    os.environ['PYTHONHASHSEED'] = seed
    key = RSA.generate(1024)
    return key.export_key(),key.publickey().export_key()

def get_public_key(seed):
    os.environ['PYTHONHASHSEED'] = seed
    key = RSA.generate(1024)
    return key.publickey().export_key()


if __name__ == "__main__":
    print("Let's simulate the scenario where A gives their public key to B")
    print("and B gives their public key to A. In a real-world scenario,")
    print("you'd use something like sockets or a messaging service to exchange keys. \n\n\n")

    # Generating A's key pair with seed "A_seed"
    private_key_A, public_key_A = gen_keys("A_seed")
    print(f"private key of A is = {private_key_A.export_key().decode()}")
    print(f"public key of A is = {public_key_A.export_key().decode()}\n\n")

    # Generating B's key pair with seed "B_seed"
    private_key_B, public_key_B = gen_keys("B_seed")
    print(f"private key of B is = {private_key_B.export_key().decode()}")
    print(f"public key of B is = {public_key_B.export_key().decode()}\n\n")

    # Let's simulate B sending a message to A
    message_from_B = "Hey A, it's me B. How are you?"
    print(f"message from B is = {message_from_B}\n")
    encrypted_message_for_A = encrypt_message(public_key_A, message_from_B)
    print(f"the encrypted message for A is = {encrypted_message_for_A}\n\n")

    print("Now, A decrypts the message from B")
    decrypted_message_by_A = decrypt_message(private_key_A, encrypted_message_for_A)
    print("Message from B decrypted by A:", decrypted_message_by_A,"\n\n")

    print("Simulating A sending a message to B")
    message_from_A = "Hey B, I'm doing great! How about you?"
    encrypted_message_for_B = encrypt_message(public_key_B, message_from_A)
    print(f"message from A: {message_from_A}\n\n")

    print("Now, B decrypts the message from A")
    decrypted_message_by_B = decrypt_message(private_key_B, encrypted_message_for_B)
    print("Message from A decrypted by B:", decrypted_message_by_B)
