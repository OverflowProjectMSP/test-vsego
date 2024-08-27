import os
import psycopg2
from psycopg2 import extras, Error
from dotenv import load_dotenv
import logging
import hashlib

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y—%m—%d %H:%M:%S",
)

PASSWORD_PG = os.getenv('DB_PASSWORD')
PORT_PG = os.getenv('DB_PORT')
USER_PG = os.getenv('DB_USERNAME')
HOST_PG = os.getenv('DB_HOST')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def hash_all():
    try:
        pg = psycopg2.connect(f"""
                host={HOST_PG}
                dbname=postgres
                user={USER_PG}
                password={PASSWORD_PG}
                port={PORT_PG}
            """)

        cursor = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute("SELECT id, password FROM users")

        res = cursor.fetchall()

        for i in range(len(res)):
            res[i] = dict(res[i])


        for i in range(len(res)):
            res[i]['password'] = hash_password(res[i]['password'])


        for i in range(len(res)):
            cursor.execute(f"UPDATE users SET password=$${res[i]['password']}$$ WHERE id=$${res[i]["id"]}$$")

        pg.commit()

    except (Exception, Error) as error:
        logging.error(f'DB: ', error)

    finally:
        if pg:
            cursor.close()
            pg.close()
            logging.info("Соединение с PostgreSQL закрыто")

def verify_password(stored_hash, password):
    return stored_hash == hash_password(password)

def check_password(stored_hash, input_password):
    if verify_password(stored_hash, input_password):
        return True
    return False

logging.info(check_password("ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f", "password123"))

if __name__ == '__main__':
    hash_all()

