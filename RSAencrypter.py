from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def encrypt_message(public_key, message):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted_message = cipher.encrypt(message.encode())
    return encrypted_message

def decrypt_message(private_key, encrypted_message):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    return decrypted_message.decode()

# Let's simulate the scenario where A gives their public key to B
# and B gives their public key to A. In a real-world scenario,
# you'd use something like sockets or a messaging service to exchange keys.

# Generating A's key pair
key_pair_A = RSA.generate(2048)
public_key_A = key_pair_A.publickey()
private_key_A = key_pair_A.export_key()

# Generating B's key pair
key_pair_B = RSA.generate(2048)
public_key_B = key_pair_B.publickey()
private_key_B = key_pair_B.export_key()

# Let's simulate B sending a message to A
message_from_B = "Hey A, it's me B. How are you?"
encrypted_message_for_A = encrypt_message(public_key_A, message_from_B)

# Now, A decrypts the message from B
decrypted_message_by_A = decrypt_message(private_key_A, encrypted_message_for_A)

print("Message from B decrypted by A:", decrypted_message_by_A)

# Simulating A sending a message to B
message_from_A = "Hey B, I'm doing great! How about you?"
encrypted_message_for_B = encrypt_message(public_key_B, message_from_A)

# Now, B decrypts the message from A
decrypted_message_by_B = decrypt_message(private_key_B, encrypted_message_for_B)

print("Message from A decrypted by B:", decrypted_message_by_B)
