"""
Neccessory Module imports
"""
import os
from helpers import get_project_id
import tableauserverclient as TSC


def publish_wb(server, data):
    """
    Funcrion Description
    """
    project_id = get_project_id(
        server, data['publish_wb_data']['project_path'], data['publish_wb_data']['file_path'])
    wb_path = os.path.dirname(os.path.realpath(__file__)).rsplit(
        '/', 1)[0] + "/workbooks/" + data['publish_wb_data']['file_path']

    new_workbook = TSC.WorkbookItem(
        name=data['publish_wb_data']['wb_name'],
        project_id=project_id,
        show_tabs=data['publish_wb_data']['show_tabs'])
    new_workbook = server.workbooks.publish(
        new_workbook, wb_path, "Overwrite", hidden_views=data['publish_wb_data']['hidden_views']
        if len(data['publish_wb_data']['hidden_views']) > 0 else None)

    print(
        f"\nSuccessfully published {data['publish_wb_data']['file_path']} Workbook in {data['publish_wb_data']['project_path']} project in {data['publish_wb_data']['site_name']} site.")

    # Update Workbook and set tags
    if len(data['publish_wb_data']['tags']) > 0:
        new_workbook.tags = set(data['publish_wb_data']['tags'])
        new_workbook = server.workbooks.update(
            new_workbook)
        print("\nUpdate Workbook Successfully and set Tags.")

    return new_workbook._id
