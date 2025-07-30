from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_string_password(password: str) -> str:
    return pwd_context.hash(password)

print("password verification result: ", verify_password("dupa8", "$2b$12$okceCcGctml/nO3iDjtM/Ox55xVaXXmWmHQ/MwNgwEImnr/Wg21YC"))