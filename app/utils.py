from passlib.context import CryptContext
hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return hashing.hash(password)


def verify(password: str, hashed_password: str):
    return hashing.verify(password, hashed_password)