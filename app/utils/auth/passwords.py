from passlib.hash import bcrypt_sha256


# hasher: "bcrypt_sha256" = bcrypt_sha256.using(rounds=130000)


def get_password_hash(password: str):
    return bcrypt_sha256.hash(password)


def verify_password(password_hash:str, password_string):
    return bcrypt_sha256.verify(password_string,password_string)