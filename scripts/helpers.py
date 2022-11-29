"""
Neccessory Module imports
"""
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
xmlns = {'t': 'http://tableau.com/api'}


class ApiCallError(Exception):
    """
    api caller class for excepiton
    """
    pass


def _encode_for_display(text):
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


def _check_status(server_response, success_code):
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)
        error_element = parsed_response.find('t:error', namespaces=xmlns)
        summary_element = parsed_response.find(
            './/t:summary', namespaces=xmlns)
        detail_element = parsed_response.find('.//t:detail', namespaces=xmlns)
        code = error_element.get(
            'code', 'unknown') if error_element is not None else 'unknown code'
        summary = summary_element.text if summary_element is not None else 'unknown summary'
        detail = detail_element.text if detail_element is not None else 'unknown detail'
        error_message = f'{code}: {summary} - {detail}'
        raise ApiCallError(error_message)
    return


def sign_in(username, password, server_url, site_name, is_site_default):
    """
    This funciton sign in to server
    """
    tableau_auth = TSC.TableauAuth(
        username, password, None if is_site_default else site_name)
    server = TSC.Server(server_url, use_server_version=True)
    server.auth.sign_in(tableau_auth)
    server_response = vars(server)
    auth_token = server_response.get('_auth_token')
    version = server_response.get('version')
    return server, auth_token, version


def get_project_id(server, project_path, file_path):
    """
    This funciton get project id from the server
    """
    all_projects, pagination_item = server.projects.get()
    project = next(
        (project for project in all_projects if project.name == project_path), None)
    if project.id is not None:
        return project.id
    else:
        raise LookupError(
            f"The project for {file_path} workbook could not be found.")


def get_group_id(server, permission_group_name):
    """
    This funciton get group id from the server
    """
    all_groups, pagination_item = server.groups.get()
    group_id_list = [
        group.id for group in all_groups if group.name == permission_group_name]
    return group_id_list


def get_user_id(server, permission_user_name):
    """
    This funciton get user id from the server
    """
    all_users, pagination_item = server.users.get()
    user_id_list = [
        user.id for user in all_users if user.name == permission_user_name]
    return user_id_list
