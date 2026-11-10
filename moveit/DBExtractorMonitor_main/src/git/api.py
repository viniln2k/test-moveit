"""
doc
"""
import configparser
import inspect
import os
import time

import requests


class GitHubOps:
    """
    doc
    """

    # secret_response = get_secret("Git")
    # _github_token = get_secret_value(secret_response, "token")

    # __token = get_secret_value("Git", "token")

    _config = None

    @classmethod
    def initialize(cls, config):
        cls._config = config

    @classmethod
    def get_team_repositories(cls, team_name):
        """

        :param team_name:
        :return:
        """
        data = []

        uri_val = (
            f"{cls._config.get('Settings', 'GitHubAPIBaseUrl')}/orgs/"
            f"{cls._config.get('Settings', 'organization')}"
            f"/teams/{team_name}/repos"
        )

        headers = {
            "Accept": cls._config.get('Settings', 'GitHubAPILevel'),
            "Authorization": "Bearer " + cls._config.get('Settings', 'git_fine_grain_token'),
            "X-GitHub-Api-Version": cls._config.get('Settings', 'GitHubAPIVersion')
        }

        return cls.__get_data_recursive(None, uri_val, status_codes=[200], status_codes_error=[404],
                                        request_type="GET", headers=headers, data=data, post_data=None)

    @classmethod
    def run_workflow(cls, branch, workflow_name):
        """ doc """
        data = []

        uri_val = (
            f"{cls._config.get('Settings', 'GitHubAPIBaseUrl')}/repos/"
            f"{cls._config.get('Settings', 'repo_owner')}/"
            f"{cls._config.get('Settings', 'repo')}/actions/workflows/"
            f"{workflow_name}/dispatches"
        )

        headers = {
            "Accept": cls._config.get('Settings', 'GitHubAPILevel'),
            "Authorization": "Bearer " + cls._config.get('Settings', 'git_fine_grain_token'),
            "X-GitHub-Api-Version": cls._config.get('Settings', 'GitHubAPIVersion')
        }

        post_data = {"ref": branch}
        return cls.__get_data_recursive(None, uri_val, status_codes=[200, 204], status_codes_error=[404],
                                        request_type="POST", headers=headers, data=data, post_data=post_data)

    @classmethod
    def get_file(cls, repo, branch, file_path):
        """
        doc
        """

        data = []

        uri_val = (
            f"{cls._config.get('Settings', 'GitHubAPIBaseUrl')}/repos/"
            f"{cls._config.get('Settings', 'organization')}/{repo}/contents/"
            f"{file_path}?ref={branch}"
        )

        headers = {
            "Accept": cls._config.get('Settings', 'GitHubAPILevel'),
            "Authorization": "Bearer " + cls._config.get('Settings', 'git_fine_grain_token'),
            "X-GitHub-Api-Version": cls._config.get('Settings', 'GitHubAPIVersion')
        }

        return cls.__get_data_recursive(None, uri_val, status_codes=[200], status_codes_error=[403, 404],
                                        request_type="GET", headers=headers, data=data, post_data=None)

    @classmethod
    def get_branches(cls, repo_name):
        """
        docs
        """

        data = []

        uri_val = (
            f"{cls._config.get('Settings', 'GitHubAPIBaseUrl')}/repos/"
            f"{cls._config.get('Settings', 'organization')}/{repo_name}/branches"
        )

        headers = {
            "Accept": cls._config.get('Settings', 'GitHubAPILevel'),
            "Authorization": "Bearer " + cls._config.get('Settings', 'git_fine_grain_token'),
            "X-GitHub-Api-Version": cls._config.get('Settings', 'GitHubAPIVersion')
        }

        return cls.__get_data_recursive(None, uri_val, status_codes=[200], status_codes_error=[404],
                                        request_type="GET", headers=headers, data=data, post_data=None)

    @classmethod
    def list_commits(cls, repo_name):
        """

        :param repo_name:
        :return:
        """

        data = []

        uri_val = (
            f"{cls._config.get('Settings', 'GitHubAPIBaseUrl')}/repos/"
            f"{cls._config.get('Settings', 'organization')}/{repo_name}/commits"
        )

        headers = {
            "Accept": cls._config.get('Settings', 'GitHubAPILevel'),
            "Authorization": "Bearer " + cls._config.get('Settings', 'git_fine_grain_token'),
            "X-GitHub-Api-Version": cls._config.get('Settings', 'GitHubAPIVersion')
        }

        return cls.__get_data_recursive(None, uri_val,
                                        status_codes=[200], status_codes_error=[404, 409, 500, 400], request_type="GET",
                                        headers=headers, data=data, post_data=None)

    @classmethod
    def list_pull_requests(cls, repo_name):
        """
        docs
        :param repo_name:
        :return:
        """

        data = []

        try:

            uri_val = (
                f"{cls._config.get('Settings', 'GitHubAPIBaseUrl')}/repos/"
                f"{cls._config.get('Settings', 'organization')}/{repo_name}/pulls?state=all"
            )

            headers = {
                "Accept": cls._config.get('Settings', 'GitHubAPILevel'),
                "Authorization": "Bearer " + cls._config.get('Settings', 'git_fine_grain_token'),
                "X-GitHub-Api-Version": cls._config.get('Settings', 'GitHubAPIVersion')
            }


        except Exception as e:
            raise

        return cls.__get_data_recursive(None, uri_val,
                                        status_codes=[200], status_codes_error=[404, 422, 304], request_type="GET",
                                        headers=headers, data=data, post_data=None)

    @classmethod
    def list_workflow_runs(cls, repo_name):
        """
        docs
        :param repo_name:
        :return:
        """

        data = []

        uri_val = (
            f"{cls._config.get('Settings', 'GitHubAPIBaseUrl')}/repos/"
            f"{cls._config.get('Settings', 'organization')}/{repo_name}/"
            f"actions/runs?exclude_pull_requests=true"
        )

        headers = {
            "Accept": cls._config.get('Settings', 'GitHubAPILevel'),
            "Authorization": "Bearer " + cls._config.get('Settings', 'git_fine_grain_token'),
            "X-GitHub-Api-Version": cls._config.get('Settings', 'GitHubAPIVersion')
        }

        return cls.__get_data_recursive(None, uri_val,
                                        status_codes=[200], status_codes_error=[404], request_type="GET",
                                        headers=headers, data=data, post_data=None)

    @classmethod
    def __get_data_recursive(cls, navigation_link, uri_val, status_codes, status_codes_error, request_type, headers,
                             data, post_data):
        """

        :param status_codes:
        :return:
        """

        repeat = True
        repeat_count = 0
        retry_limit = int(cls._config.get('Settings', 'APIRetryLimit'))
        api_call_delay = float(cls._config.get('Settings', 'APICallDelay'))

        if navigation_link:
            uri = navigation_link
        else:
            uri = uri_val

        try:

            response = None
            while repeat and repeat_count < retry_limit:
                if request_type == "GET":
                    response = requests.get(uri, headers=headers)
                elif request_type == "POST":
                    response = requests.post(uri, headers=headers, json=post_data)

                success = cls.__check_status_codes(status_codes, response.status_code)

                if response.status_code == 204:
                    break
                elif success:
                    result = response.json()
                    if type(result) is list:
                        for item in result:
                            data.append(item)
                    elif type(result) is dict:
                        data.append(result)
                    break
                elif cls.__check_status_codes(status_codes_error, response.status_code):
                    cur_frame = inspect.currentframe()
                    raise Exception(f'GitHub API Error, {__name__}, {cur_frame.f_back.f_code.co_name}',
                                    f'{cur_frame.f_code.co_name}, {response.status_code}')

                repeat_count += 1
                time.sleep(api_call_delay)

            if repeat_count == retry_limit:
                cur_frame = inspect.currentframe()
                raise Exception(f'GitHub Retry Limit Reached Error, {__name__}, {cur_frame.f_back.f_code.co_name}',
                                f'{cur_frame.f_code.co_name}, {response.status_code}')

            next_link = cls.__get_next_link(response.links)
            if next_link is not None:
                cls.__get_data_recursive(next_link, uri_val, status_codes, status_codes_error, request_type,
                                         headers, data, post_data)

            return data

        except Exception as e:
            raise

    @classmethod
    def __get_next_link(cls, links):
        """
        doc
        :return:
        """

        next_link = None

        for key, value in links.items():
            if key == "next":
                next_link = value.get("url")
                break

        return next_link

    @classmethod
    def __check_status_codes(cls, codes_to_look_for, status_code):
        """

        :param codes_to_look_for:
        :param status_code:
        :return:
        """

        b_found = False
        for code in codes_to_look_for:
            if status_code == code:
                b_found = True
                break

        return b_found
