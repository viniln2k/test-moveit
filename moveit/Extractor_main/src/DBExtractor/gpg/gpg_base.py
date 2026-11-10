import abc
import logging


class GpgBase(metaclass=abc.ABCMeta):
    # generate initialisation method    
    def __init__(self, args, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.args = args

    @abc.abstractmethod
    def encrypt(self, file_path):
        pass
