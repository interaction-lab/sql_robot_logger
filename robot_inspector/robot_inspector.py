import yaml
import mysql.connector
import mysql.connector.errors as errors
import robot_inspector.query as query
from mysql.connector import pooling


class SQLInspector:

    def __init__(self, filename=None):

        self.logging_information = self._read_config_file(filename)
        self.database_name = self.logging_information["log_info"]["database_name"]
        self.robot_id = self.logging_information["log_info"]["robot_id"]
        self.db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool",
                                                                   pool_size=5,
                                                                   **self.logging_information["sql_database"])

    def get_query(self, table_name, condition):

        statement = "SELECT * FROM " + table_name + " WHERE " + condition

        try:
            list_of_matches = self._execute_query(statement)
        except errors.ProgrammingError as e:
            raise ValueError("Cannot get query") from e
        else:
            header = self._execute_query("SHOW COLUMNS FROM "+table_name)
            query_ = query.Query(list_of_matches, [item[0] for item in header])
            return query_

    @staticmethod
    def _read_config_file(filename="config.yml"):

        with open(filename, 'r') as f:
            db1 = yaml.safe_load(f)

        return db1

    def _get_connection(self):

        while True:
            try:
                connection = self.db_pool.get_connection()
            except errors.PoolError:
                continue
            else:
                break

        return connection

    def _execute_query(self, statement):

        connection = self._get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("USE " + self.database_name)
        except errors.ProgrammingError as e:
            print(e)

        cursor.execute(statement)
        return_set = cursor.fetchall()
        connection.commit()
        connection.close()

        return return_set
