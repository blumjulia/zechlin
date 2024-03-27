from flask import g
import mariadb

from zechlin import credentials


def get_database_connection() -> mariadb.connections.Connection:
    """
    Stellt die Verbindung zur MariaDB Datenbank her

    :return: Datenbank-Verbindung
    """

    # Stellt nur neue Datenbank-Verbindung her, wenn nicht schon eine besteht
    if 'database_connect' not in g:
        # Zugangsdaten werden aus der credentials.py ausgelesen und verwendet
        database_connection = mariadb.connect(
            user=credentials.config['database']['user'],
            password=credentials.config['database']['password'],
            host=credentials.config['database']['host'],
            port=credentials.config['database']['port'],
            database=credentials.config['database']['database']
        )

        g.database_connection = database_connection

    return g.database_connection


def close_database_cursor() -> None:
    """
    Beendet bestehende Datenbank-Verbindungen und Datenbank-Cursor

    :return: void
    """

    database_connection = g.pop('database_connection', None)
    database_cursor = g.pop('database_cursor', None)

    if database_cursor is not None:
        database_cursor.close()
