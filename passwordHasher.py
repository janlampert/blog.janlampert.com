import bcrypt
import hashlib
import base64

class passwordHasher:

    def hash(password: str):
        password = password.encode("utf-8")
        password = base64.b64encode(hashlib.sha256(password).digest())
        hashed = bcrypt.hashpw(
            password,
            bcrypt.gensalt(12)
        )
        return hashed.decode()

    def check(password: str, hash: str):
        password = password.encode("utf-8")
        password = base64.b64encode(hashlib.sha256(password).digest())
        hash = hash.encode("utf-8")
        if bcrypt.checkpw(password, hash):
            return True

        else:
            return False

