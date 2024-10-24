import hashlib
import os
from time import sleep

import requests


class SonarClient:

    def __init__(self, sonar_url, sonar_token, auth_type, login_username, login_password):
        self.sonar_url = sonar_url
        self.sonar_token = sonar_token
        self.auth_type = auth_type
        self.login_username = login_username
        self.login_password = login_password

    def delete_project(self, project_key):
        endpoint = f"{self.sonar_url}/api/projects/delete"
        params = {"project": project_key}
        requests.post(endpoint, params=params, headers=self._get_headers(), auth=self._get_auth())

    def create_project(self, project_key, project_name):
        endpoint = f"{self.sonar_url}/api/projects/create"
        data = {"project": project_key, "name": project_name}
        response = requests.post(endpoint, params=data, headers=self._get_headers(), auth=self._get_auth())
        response.raise_for_status()

    def run_scanner(self, project_key, scanner_home, source_path, changes, sonar_extra_args):
        inclusions = []
        for change in changes:
            inclusions.append(change['new_path'])
        inclusions = ",".join(inclusions)
        params = [
            f"cd {source_path} &&",
            f"{scanner_home}/bin/sonar-scanner",
            f"-Dsonar.projectKey={project_key}",
            f"-Dsonar.inclusions={inclusions}",
            f"-Dsonar.host.url={self.sonar_url}",
            f"-Dsonar.login={self.sonar_token}",
            f"-Dsonar.scm.exclusions.disabled=true",
        ]
        if len(sonar_extra_args) > 0:
            params.append(sonar_extra_args)
        command = " ".join(params)
        retorno = os.system(command)
        if retorno != 0:
            raise OSError("Failed to run sonar scanner")

    def is_queue_empty(self):
        endpoint = f"{self.sonar_url}/api/analysis_reports/is_queue_empty"
        response = requests.get(endpoint, headers=self._get_headers(), auth=self._get_auth())
        return response.status_code == 200 and response.json()

    def list_issues(self, project_key):
        endpoint = f"{self.sonar_url}/api/issues/search"
        params = {"componentKeys": project_key, "statuses": "OPEN"}
        response = requests.get(endpoint, params=params, headers=self._get_headers(), auth=self._get_auth())
        response.raise_for_status()
        return response.json()["issues"]

    def _get_headers(self):
        if self.auth_type != 'BEARER_TOKEN':
            return None

        return {"Authorization": f"Bearer {self.sonar_token}"}

    def _get_auth(self):
        if self.auth_type != 'BASIC_AUTH':
            return None

        auth = (self.login_username, self.login_password)
        return auth

    @staticmethod
    def is_path_presente_in_changes(path, changes):
        for change in changes:
            if change['new_path'] == path:
                return True

        return False

    def get_comments(
            self,
            scanner_home,
            path_source,
            project_id,
            merge_request_id,
            rules,
            changes,
            rules_deny,
            sonar_extra_args,
            sonar_scanner_pre_command
    ):
        __PROJECT_KEY = f"code-review-{project_id}-{merge_request_id}"

        self.delete_project(__PROJECT_KEY)
        self.create_project(__PROJECT_KEY, __PROJECT_KEY)

        if os.path.exists(path_source):
            if len(sonar_scanner_pre_command) > 0:
                os.system(f"cd {path_source} && {sonar_scanner_pre_command}")
            self.run_scanner(__PROJECT_KEY, scanner_home, path_source, changes, sonar_extra_args)

        while not self.is_queue_empty():
            sleep(1)

        issues_source = self.list_issues(__PROJECT_KEY)

        comments = []

        for issue_source in issues_source:
            issue_rule = issue_source['rule']

            if len(rules) > 0 and issue_rule not in rules:
                continue

            if issue_rule in rules_deny:
                continue

            if 'hash' not in issue_source:
                continue

            issue_message = issue_source['message']
            issue_hash = issue_source['hash']
            issue_path = issue_source['component']
            issue_path = issue_path[issue_path.index(":") + 1:]
            issue_start_line = issue_source['textRange']['startLine']
            issue_end_line = issue_source['textRange']['endLine']
            issue_line = issue_source['line']

            if not self.is_path_presente_in_changes(issue_path, changes):
                continue

            details = [
                f"Type: {issue_rule}<br>",
                f"<b>Message: {issue_message}</b><br>",
                f"Arquivo: {issue_path}",
                f"Linha inicial: {issue_start_line}",
                f"Linha final: {issue_end_line}",
            ]
            comments.append({
                'id': self.__generate_md5(f"{issue_hash}{issue_line}{issue_message}{issue_path}"),
                'comment': '<br>'.join(details),
                'position': {
                    'language': 'c++',
                    'path': issue_path,
                    'startInLine': issue_start_line,
                    'endInLine': issue_end_line,
                }
            })

        self.delete_project(__PROJECT_KEY)

        return comments

    @staticmethod
    def __generate_md5(string):
        md5_hash = hashlib.md5()
        md5_hash.update(string.encode('utf-8'))

        return md5_hash.hexdigest()
