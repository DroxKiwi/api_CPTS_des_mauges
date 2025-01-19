
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    print(pwd_context.hash(password))

#get_password_hash("FE8$è-274vGE") #admin1
#get_password_hash("FE23b$éaza4v1") #admin2
#get_password_hash("168GEZ6aè)àùf") #admin3
#get_password_hash("000*$&&8ca6+s") #admin4