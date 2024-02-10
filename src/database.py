import pandas as pd
from sqlalchemy import create_engine
import psycopg

from src import config


def connect(url, db, user, password, port):
    params_dic = {
        "host": url,
        "dbname": db,
        "user": user,
        "password": password,
        "port": port,
    }

    try:
        # connect to the PostgreSQL server
        conn = psycopg.connect(**params_dic)
    except (Exception, psycopg.DatabaseError) as error:
        print(error)
        exit(1)
    return conn


def postgresql_to_dataframe(conn, select_query):
    """
    Function to download a dataframe from a query

    :param conn: the connection object (connect method)
    :param select_query: the query
    :type select_query: str
    :return: DataFrame obtained from the query
    :rtype: pandas.DataFrame
    """

    cursor = conn.cursor()
    try:
        cursor.execute(select_query)
    except (Exception, psycopg.DatabaseError) as error:
        print("Error: %s" % error)
        cursor.close()
        return None

    # Naturally we get a list of tuples
    tuples = cursor.fetchall()

    # We just need to turn it into a pandas dataframe
    df = pd.DataFrame(tuples, columns=[e.name for e in cursor.description])
    cursor.close()

    return df


def sql_connection(host, database, user, password, port):
    db_url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(db_url)
    return engine


def upload_user(username: str, hassed_password: str, salt: str):
    conn = connect(
        config.TEST_USERDB_URL, config.TEST_USERDB_NAME,
        config.TEST_USERDB_USERNAME, config.TEST_USERDB_PASSWORD,
        config.TEST_USERDB_PORT
    )
    cursor = conn.cursor()

    insert_query = """
        INSERT INTO serverchat.users 
        (username, hassed_password, salt) 
        VALUES (%s, %s, %s);
    """

    data_to_insert = (username, hassed_password, salt)

    cursor.execute(insert_query, data_to_insert)
    conn.commit()
    cursor.close()
    conn.close()


def get_user(username: str):
    conn = connect(
        config.TEST_USERDB_URL, config.TEST_USERDB_NAME,
        config.TEST_USERDB_USERNAME, config.TEST_USERDB_PASSWORD,
        config.TEST_USERDB_PORT
    )
    cursor = conn.cursor()

    select_query = """
        SELECT * FROM serverchat.users
        WHERE username = %s;
    """

    cursor.execute(select_query, (username,))
    value = cursor.fetchone()

    conn.commit()
    cursor.close()
    conn.close()

    return value


if __name__ == "__main__":
    import bcrypt

    # New user
    username = 'juan'
    pw = 'sanchez'

    salt = bcrypt.gensalt()
    hassed_password = bcrypt.hashpw(pw.encode('utf-8'), salt)
    upload_user(username, hassed_password, salt)

    login_user = 'juan'
    login_password_1 = 'sonchez'
    login_password_2 = 'sanchez'

    tableun, tablehp, tablesalt = get_user(login_user)
    print(bcrypt.hashpw(login_password_1.encode(), tablesalt) == tablehp)
    print(bcrypt.hashpw(login_password_2.encode(), tablesalt) == tablehp)
