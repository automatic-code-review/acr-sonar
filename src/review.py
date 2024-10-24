import os

from src.sonar_client import SonarClient


def review(config):
    path_source = config['path_source_v2']

    merge = config['merge']
    project_id = merge['project_id']
    merge_request_id = merge['merge_request_id']

    sonar_client = SonarClient(
        sonar_token=__get_by_config_or_enviroment(config, 'token', 'SONAR_TOKEN'),
        sonar_url=config['url'],
        auth_type=config['auth_type'],
        login_password=__get_or_default(config, 'auth_password'),
        login_username=__get_or_default(config, 'auth_username'),
    )

    comments = sonar_client.get_comments(
        scanner_home=config['scanner_home'],
        path_source=path_source,
        changes=merge['changes'],
        project_id=project_id,
        merge_request_id=merge_request_id,
        rules=config['rules'],
        rules_deny=config.get("rulesDeny", []),
        sonar_extra_args=config.get("sonarExtraArgs", ""),
        sonar_scanner_pre_command=config.get("sonarScannerPreCommand", ""),
    )

    return comments


def __get_or_default(obj, name, default=None):
    if name in obj:
        return obj[name]

    return default


def __get_by_config_or_enviroment(obj, name, name_enviroment):
    retorno = __get_or_default(obj, name)

    if retorno is None:
        retorno = os.environ.get(name_enviroment)

    return retorno
