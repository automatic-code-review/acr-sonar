from src.sonar_client import SonarClient


def review(config):
    path_target = config['path_target']
    path_source = config['path_source']

    merge = config['merge']
    project_id = merge['project_id']
    merge_request_id = merge['merge_request_id']

    sonar_client = SonarClient(
        sonar_token=config['token'],
        sonar_url=config['url'],
        auth_type=config['auth_type'],
        login_password=config['auth_password'],
        login_username=config['auth_username'],
    )

    comments = sonar_client.get_comments(
        scanner_home=config['scanner_home'],
        path_source=path_source,
        path_target=path_target,
        project_id=project_id,
        merge_request_id=merge_request_id,
        rules=config['rules'],
    )

    return comments
