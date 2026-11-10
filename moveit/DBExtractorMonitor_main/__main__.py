# This is a sample Python script.
import argparse
import configparser
import logging.config
import os

from src.git.api import GitHubOps

logging.config.fileConfig(os.path.join(os.path.dirname(__file__), '', 'logger.conf'))


def main():
    # Use a breakpoint in the code line below to debug your script.

    logger = logging.getLogger(__name__)
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '', 'app.conf'))

    git_config = configparser.ConfigParser()
    git_config.read(os.path.join(os.path.dirname(__file__), '', 'git.conf'))

    try:

        parser = argparse.ArgumentParser()
        parser.add_argument('--branch', help='Enter branch containing target workflow')
        parser.add_argument('--workflow', help='Enter workflow yaml file name')
        args = parser.parse_args()

        if args.workflow is None or args.branch is None:
            raise Exception("--workflow and --branch are required parameters")

        fileh = logging.FileHandler(f"{config.get('Settings', 'log_file_path')}/{args.workflow}.log", 'a')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s - %(pathname)s - %(funcName)s - %(lineno)d')
        fileh.setFormatter(formatter)

        logger = logging.getLogger()  # root logger
        logger.addHandler(fileh)  # set the new handler

        GitHubOps.initialize(git_config)
        GitHubOps.run_workflow(args.branch, args.workflow)
        logger.info("Execution Completed")

    except Exception as e:
        logger.error(e)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
