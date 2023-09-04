import passlib
from passlib.context import CryptContext


class HasherService:
    pwd_context: CryptContext = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        try:
            return cls.pwd_context.verify(plain_password, hashed_password)
        except passlib.exc.UnknownHashError:
            return False

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)
