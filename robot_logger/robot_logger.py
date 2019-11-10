import mysql.connector
from mysql.connector import pooling
from mysql.connector import errors
import time
import threading
import yaml


class RobotLogger:

    def __init__(self, filename=None):

        self.logging_information = self._read_config_file(filename)
        self.database_name = self.logging_information["log_info"]["database_name"]
        self.robot_id = self.logging_information["log_info"]["robot_id"]

        self.db_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool",
                                                                   pool_size=5,
                                                                   **self.logging_information["sql_database"])

        self._execute_insert("CREATE DATABASE IF NOT EXISTS  " + self.database_name, True)
        self._create_tables()

        if not self.robot_id:
            self._execute_insert("INSERT INTO robots VALUES (NULL)")
            rs = self._execute_query("SELECT robot_id FROM robots ORDER BY robot_id DESC LIMIT 0, 1")
            self.logging_information["log_info"]["robot_id"] = rs[0][0]
            self.robot_id = rs[0][0]

    def write(self, topic_name, data, source, is_keep_local_copy=False):
        thread = threading.Thread(target=self.write_callback, args=(topic_name, data, source, is_keep_local_copy,))
        thread.start()

    def write_callback(self, topic_name, data, source, is_keep_local_copy=False):

        statement = "INSERT INTO log VALUES (NOW(),%s,%s,'%s',%s,%s)"
        topic_id = "(SELECT topic_id FROM topics WHERE topic_name = '" + topic_name + "')"
        mismatched = "(SELECT EXISTS(SELECT * FROM topics WHERE topic_name = '" +\
                     topic_name + \
                     "' and data_type='" +\
                     type(data).__name__ + "'))"

        values = (topic_id, data, source, mismatched, self.robot_id)
        statement = statement % values

        try:
            self._execute_insert(statement)
        except errors.IntegrityError as ie:
            raise ValueError("Cannot write to log") from ie

        if is_keep_local_copy:
            statement = "INSERT INTO local_log VALUES (NOW(),%s,%s,'%s',%s,%s)"
            statement = statement % values

            try:
                self._execute_insert(statement)
            except errors.IntegrityError as ie:
                raise ValueError("Cannot write to local_log") from ie

    def _clear_tables(self):

        self._execute_insert("DROP TABLE local_log;")
        self._execute_insert("DROP TABLE log;")
        self._execute_insert("DROP TABLE topics;")
        self._execute_insert("DROP TABLE robots;")
        self._create_tables()

    def add_topic(self, topic_name, data_type=str):

        statement = "INSERT INTO topics VALUES (NULL, '%s', '%s')"
        values = (topic_name, data_type.__name__)
        statement = statement % values

        try:
            self._execute_insert(statement)
        except errors.IntegrityError as ie:
            raise ValueError("Attempting add an existing topic") from ie

    def update_config_file(self, filename='config.yml'):

        with open(filename, "w") as f:
            yaml.dump(self.logging_information, f)

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

    def _execute_insert(self, statement, creating_db=False):

        connection = self._get_connection()
        cursor = connection.cursor()

        if creating_db:
            cursor.execute(statement)
            connection.commit()
            connection.close()
        else:
            try:
                cursor.execute("USE " + self.database_name)
            except errors.DatabaseError as e:
                print(e)

            cursor.execute(statement)
            connection.commit()
            connection.close()

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

    def _create_tables(self):

        self._execute_insert("CREATE TABLE IF NOT EXISTS "
                             "topics(" 
                             "topic_id INT AUTO_INCREMENT, " 
                             "topic_name varchar(255) NOT NULL, " 
                             "data_type TEXT NOT NULL,"
                             "PRIMARY KEY(topic_id,topic_name),"
                             "UNIQUE(topic_name)"
                             ")"
                             )

        self._execute_insert("CREATE TABLE IF NOT EXISTS "
                             "robots(" 
                             "robot_id INT AUTO_INCREMENT,"
                             "PRIMARY KEY (robot_id)"
                             ")"
                             )

        self._execute_insert("CREATE TABLE IF NOT EXISTS " +
                             "log(" +
                             "timestamp TEXT NOT NULL," +
                             "topic_id INT NOT NULL," +
                             "data BLOB NOT NULL," +
                             "source TEXT NOT NULL," +
                             "mismatched BOOLEAN,"
                             "robot_id INT," +
                             "FOREIGN KEY (topic_id) REFERENCES topics(topic_id)" +
                             ")"
                             )

        self._execute_insert("CREATE TABLE IF NOT EXISTS " 
                             "local_log(" 
                             "timestamp TEXT NOT NULL, " 
                             "topic_id INT NOT NULL, " 
                             "data BLOB NOT NULL, "
                             "source TEXT NOT NULL, "
                             "mismatched BOOLEAN,"
                             "robot_id INT,"
                             "FOREIGN KEY (topic_id) REFERENCES topics(topic_id)" +
                             ")"
                             )

    def backup(self):

        filename = "backup_local_log_" + str(time.time()) + ".txt"
        file = open(filename, 'w+')

        topics = self._execute_query("SELECT * FROM topics;")
        log = self._execute_query("SELECT * FROM local_log;")
        file.write(str(topics))
        file.write("\n")
        file.write(str(log))
