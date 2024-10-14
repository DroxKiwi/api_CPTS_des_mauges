
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    print(pwd_context.hash(password))

get_password_hash("FE8$è-274vGE")