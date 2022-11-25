"""
Neccessory Module imports
"""
import logging
from publish import publish_wb
from helpers import sign_in, get_group_id, get_user_id
from permissions import query_permission, add_permission, delete_permission


def temp_func(data, username, password, prod_username, prod_password):
    """
    Funcrion Description
    """
    # Step: Sign In to the Tableau Server
    if data['publish_wb_data']['server_name'] == "dev":
        uname, pname, surl = username, password, data['dev_server_url']
    elif data['publish_wb_data']['server_name'] == "prod":
        uname, pname, surl = prod_username, prod_password, data['prod_server_url']

    server, auth_token, version = sign_in(
        uname, pname, surl, data['publish_wb_data'][
            'site_name'], data['publish_wb_data']['is_site_default']
    )

    # Publish Workbook Part
    try:
        # Step: Form a new workbook item and publish.
        if data['is_wb_publish']:
            wb_id = publish_wb(server, data)
    except Exception as tableu_exception:
        logging.error(
            "Something went wrong in publish workbook.\n %s", tableu_exception)
        exit(1)

    # Permissions Part
    try:
        if data['is_wb_permissions_update']:
            for permission_data in data['permissions']:
                is_group = None

                # Step: Get the User or Group ID of permission assigned
                if permission_data['permission_group_name'] and \
                        not permission_data['permission_user_name']:
                    permission_user_or_group_id = get_group_id(
                        server, permission_data['permission_group_name'])[0]
                    is_group = True
                elif not permission_data['permission_group_name'] and \
                        permission_data['permission_user_name']:
                    permission_user_or_group_id = get_user_id(
                        server, permission_data['permission_user_name'])[0]
                    is_group = False

                # get permissions of specific workbook
                user_permissions = query_permission(
                    surl, version, data['publish_wb_data']['site_id'],
                    wb_id, auth_token, permission_user_or_group_id, is_group
                )

                if user_permissions is None:
                    for permission_name, permission_mode in \
                            permission_data['permission_template'].items():
                        add_permission(
                            surl, data['publish_wb_data']['site_id'],
                            wb_id, permission_user_or_group_id, version,
                            auth_token, permission_name, permission_mode, is_group)
                        print(
                            f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")
                else:
                    existed_permissions_dict = {}
                    delete_permissions_dict = {}
                    existed_permissions_dict_key_list = []
                    all_permissions_key_list = []

                    for permission in user_permissions:
                        existed_permissions_dict.update(
                            {permission.get('name'): permission.get('mode')})

                    existed_permissions_dict_key_list = list(
                        existed_permissions_dict.keys())
                    all_permissions_key_list = list(
                        permission_data['permission_template'].keys())

                    common_permissioins_list = list(set(
                        existed_permissions_dict_key_list).intersection(set(all_permissions_key_list)))

                    for common_permissioins in common_permissioins_list:
                        delete_permissions_dict.update(
                            {common_permissioins: existed_permissions_dict.get(common_permissioins)})

                    for permission_name, permission_mode in delete_permissions_dict.items():
                        delete_permission(
                            surl, data['publish_wb_data']['site_id'], auth_token, wb_id,
                            permission_user_or_group_id, permission_name,
                            permission_mode, version, is_group)
                        print(
                            f"\tPermission {permission_name} : {permission_mode} is deleted Successfully in {wb_id}\n")

                    for permission_name, permission_mode in \
                            permission_data['permission_template'].items():
                        add_permission(
                            surl, data['publish_wb_data']['site_id'],
                            wb_id, permission_user_or_group_id, version,
                            auth_token, permission_name, permission_mode, is_group)
                        print(
                            f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")

    except Exception as tableu_exception:
        logging.error(
            "Something went wrong in update permission of workbook.\n %s", tableu_exception)
        exit(1)

    # Step: Sign Out to the Tableau Server
    server.auth.sign_out()