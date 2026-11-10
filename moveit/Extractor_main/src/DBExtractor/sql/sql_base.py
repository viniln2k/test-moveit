import abc
import logging


class SqlBase(metaclass=abc.ABCMeta):
    """
    Class
    """

    def __init__(self, args, config):

        self.logger = logging.getLogger(__name__)
        self.config = config
        self.args = args
        self.connection = None
        self.cursor = None

    @abc.abstractmethod
    def connect(self):
        """

        :param config:
        :return:
        """

    def execute_query_fetchall(self, query, name):
        """
        query
        """

        results = None
        try:
            self.check_connection()
            self.cursor.execute(query)
            results = self.cursor.fetchall()
        except Exception as e:
            self.logger.error(e)
            raise
        else:
            self.logger.info(f"{name} query executed successfully")
        finally:
            self.close_cursor()
            return results

    def check_connection(self):

        if not self.connection:
            try:
                self.connect()
            except Exception as e:
                self.logger.error(e)
                raise

        if not self.cursor:
            try:
                self.cursor = self.connection.cursor()
            except Exception as e:
                self.logger.error(e)
                raise

        self.logger.info("Database connection and cursor OK")

    def disconnect(self):
        """
        Disconnect from the database
        :return:
        """
        self.close_cursor()
        self.close_connection()

    def close_cursor(self):
        """
        Close cursor
        :return:
        """
        if self.cursor:
            try:
                self.cursor.close()
            except Exception as e:
                self.logger.error(e)
            else:
                self.logger.info("Cursor closed successfully")
            finally:
                self.cursor = None

    def close_connection(self):
        """
        Close connection
        :return:
        """
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                self.logger.error(e)
            else:
                self.logger.info("Database Connection closed successfully")
            finally:
                self.connection = None
