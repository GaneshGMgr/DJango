import base64
import hashlib
import string
import random
import logging
from Crypto.Cipher import AES

BLOCK_SIZE = 16

# Exception for checksum related errors
class ChecksumError(Exception):
    pass

class PaytmChecksum:
    def __init__(self, secret_key):
        """
        Initializes the PaytmChecksum instance with the secret key used 
        for generating and verifying checksums.
        
        :param secret_key: The secret key shared between your system and the payment gateway.
        """
        self.secret_key = secret_key

    def generate_checksum(self, data):
        """
        Generates a checksum from the data using the secret key and SHA-256 algorithm.
        :param data: Dictionary of data to be used to generate the checksum.
        :return: Checksum string
        """
        # Sort the data to maintain consistency
        sorted_data = sorted(data.items())
        
        # Construct the string for checksum generation
        checksum_string = '&'.join(f"{key}={value}" for key, value in sorted_data)
        
        # Append the secret key at the end (as per Paytm's guidelines)
        checksum_string += f"&key={self.secret_key}"
        
        # Generate the checksum using SHA-256 hashing algorithm
        checksum = hashlib.sha256(checksum_string.encode('utf-8')).hexdigest()
        return checksum.upper()  # Some payment gateways require uppercase checksums

    def verify_checksum(self, data, checksum_received):
        """
        Verifies the checksum for the received payment gateway data.
        :param data: Dictionary of data received from the payment gateway.
        :param checksum_received: Checksum sent by the payment gateway that needs to be verified.
        :return: True if the checksum is valid, else raises ChecksumError.
        """
        checksum_calculated = self.generate_checksum(data)
        
        if checksum_calculated != checksum_received:
            error_msg = f"Checksum verification failed. Calculated: {checksum_calculated}, Received: {checksum_received}"
            raise ChecksumError(error_msg)
        
        return True

# AES Encryption & Decryption utilities

def pad(s):
    pad_len = BLOCK_SIZE - len(s) % BLOCK_SIZE
    return s + (chr(pad_len) * pad_len)

def unpad(s):
    return s[:-ord(s[-1])]

def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def get_param_string(params):
    params_string = []
    for key in sorted(params.keys()):
        value = params.get(key, "")  # Safer access with .get
        params_string.append(str(value))
    return '|'.join(params_string)

def encode(to_encode, key):
    iv = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))  # Generate random IV
    to_encode = pad(to_encode)
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    encrypted = c.encrypt(to_encode.encode())
    encrypted_base64 = base64.b64encode(encrypted).decode()
    return iv + encrypted_base64  # Return IV concatenated with encrypted data

def decode(to_decode, key):
    iv = to_decode[:16]  # Extract IV from the first 16 characters
    to_decode = to_decode[16:]  # The rest is the encrypted data
    to_decode = base64.b64decode(to_decode)
    c = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
    decrypted = c.decrypt(to_decode).decode()
    return unpad(decrypted)

def generate_checksum(params, merchant_key, salt=None):
    params_string = get_param_string(params)
    salt = salt if salt else id_generator(4)
    final_string = f"{params_string}|{salt}"
    hash_string = hashlib.sha256(final_string.encode()).hexdigest() + salt
    return encode(hash_string, merchant_key)

def verify_checksum(params, merchant_key, checksum):
    if 'CHECKSUMHASH' in params:
        checksum = params.pop('CHECKSUMHASH')

    try:
        paytm_hash = decode(checksum, merchant_key)
    except Exception as e:
        logging.error(f"Checksum decode failed: {e}")
        return False

    salt = paytm_hash[-4:]
    calculated_checksum = generate_checksum(params, merchant_key, salt=salt)
    return checksum == calculated_checksum
