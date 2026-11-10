"""
doc
"""
import abc
import logging
import logging.config


class ExtractorBase(metaclass=abc.ABCMeta):
    """
    Class
    """

    def __init__(self, args, config):
        """

        :param file_to_deploy:
        """

        self.logger = logging.getLogger(__name__)
        self.args = args
        self.config = config


@abc.abstractmethod
def execute(self):
    """

    :param config:
    :return:
    """
