"""
doc
"""
import argparse
import configparser
import importlib
import logging.config
import os


logging.config.fileConfig(os.path.join(os.path.dirname(__file__), '..', 'logger.conf'))


def main():
    """
    Func 1

    """
    logger = logging.getLogger(__name__)
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '', 'DBExtractor.conf'))

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--domain', help='Enter Web Site Domain')
        parser.add_argument('--env', help='Enter running environment: dev/qa/prod')
        args = parser.parse_args()

        if args.domain is None or args.env is None:
            raise Exception("--domain, --env are required parameters")

        modulename = args.domain.replace(".", "_")
        module = importlib.import_module("DBExtractor.targets." + modulename)
        _class = getattr(module, config.get(args.domain, "class_name"))

        _class(args, config).execute()

    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    main()
