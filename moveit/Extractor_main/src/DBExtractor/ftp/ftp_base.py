import abc
import logging


class FtpBase(metaclass=abc.ABCMeta):
    # generate initialisation method
    def __init__(self, args, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.args = args
        self.connection = None

    @abc.abstractmethod
    def connect(self):
        pass

    def upload_file(self, local_filepath, remote_filepath):
        try:
            self.check_connection()
            self.connection.put(local_filepath, remote_filepath)
        except Exception as e:
            self.logger.error(e)
            raise
        else:
            self.logger.info(f"File {local_filepath} uploaded successfully")
        finally:
            self.disconnect()

    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                self.logger.error(e)
            else:
                self.logger.info("FTP Connection closed successfully")
            finally:
                self.connection = None

    def check_connection(self):

        if not self.connection:
            try:
                self.connect()
            except Exception as e:
                self.logger.error(e)
                raise

            self.logger.info("FTP connection OK")
