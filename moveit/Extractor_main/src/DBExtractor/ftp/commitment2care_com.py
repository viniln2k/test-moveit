import os

import pysftp

from .ftp_base import FtpBase


class Commitment2care(FtpBase):
    # generate initialisation method
    def __init__(self, args, config):
        super().__init__(args, config)

    def connect(self):
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        self.connection = pysftp.Connection(host=os.getenv("FTP_HOST"),
                                            username=os.getenv("FTP_USER"),
                                            password=os.getenv("FTP_PASSWORD"),
                                            cnopts=cnopts)

