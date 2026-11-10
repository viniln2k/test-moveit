import os
import subprocess

from .gpg_base import GpgBase


class Commitment2care(GpgBase):
    # generate initialisation method
    def __init__(self, args, config):
        super().__init__(args, config)

    def encrypt(self, file_path):
        result = subprocess.run(["gpg",
                                 "--recipient",
                                 os.getenv(f"GPG_KEY"),
                                 "--encrypt",
                                 "--trust-model",
                                 "always",
                                 file_path,
                                 ], check=False, capture_output=True, text=True)
        print(result)
