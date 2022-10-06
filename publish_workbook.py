import argparse
import tableauserverclient as TSC
import json


def main(args):
    project_data_json = json.loads(args.project_data)

    try:
        # Step 1: Sign in to server.
        tableau_auth = TSC.TableauAuth(args.username, args.password)
        server = TSC.Server(args.server_url)

        with server.auth.sign_in(tableau_auth):
            for data in project_data_json:
                if data['file_path'] and data['project_path']:
                    # Step 2: Get all the projects on server, then look for the default one.
                    all_projects, pagination_item = server.projects.get()
                    project = next(
                        (project for project in all_projects if project.name == data['project_path']), None)

                    # Step 3: If default project is found, form a new workbook item and publish.
                    if project is not None:
                        new_workbook = TSC.WorkbookItem(
                            name=data['name'], project_id=project.id)
                        new_workbook = server.workbooks.publish(
                            new_workbook, data['file_path'], mode='Overwrite', hidden_views=data['hidden_views'])
                        print(
                            f"\nWorkbook :: {data['file_path']} :: published in {data['project_path']} project")
                    else:
                        error = "The project could not be found."
                        raise LookupError(error)
                        exit(1)

                else:
                    exit(1)

    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(allow_abbrev=False)

    parser.add_argument('--username', action='store',
                        type=str, required=True)
    parser.add_argument('--password', action='store',
                        type=str, required=True)
    parser.add_argument('--server_url', action='store',
                        type=str, required=True)
    parser.add_argument('--project_data', action='store',
                        type=str, required=True)

    args = parser.parse_args()
    main(args)