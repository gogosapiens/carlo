from carlo.sheet import Sheet
from carlo import drive, project, github

def create_cc_item():
    project_id_prefix = project.user_input["project_id_prefix"]
    cc_sheet = Sheet.command_center()
    cc_project_items = list(filter(lambda item: item["project_id_prefix"] == project_id_prefix, cc_sheet.items))
    cc_item = cc_sheet.insert_item({"project_id_prefix": project_id_prefix}) if len(cc_project_items) == 0 else cc_project_items[0]
    return cc_sheet, cc_item

def create_github_repos(cc_sheet, cc_item):
    platforms = project.user_input["platforms"]
    for platform in platforms.keys():
        field = f"{platform}_repo"
        if cc_item.get(field, "") == "":
            repo_name = project.project_id(platform)
            url = github.create_repo(repo_name, platforms[platform]["github_collaborators"])
            if url != None:
                cc_sheet.set_item_value(cc_item, url, key=field)


def create_drive_infrustructure():
    base_folder_id = project.keys["google_drive_root_folder_id"]
    project_id_prefix = project.user_input["project_id_prefix"]

    #Creating google drive 'projects' folder
    projects_folder_id = drive.get_folder_id("projects", parent_folder_id=base_folder_id)
    if projects_folder_id == None:
        projects_folder_id = drive.create_folder("projects", parent_folder_id=base_folder_id)

    #Creating google drive project folder
    project_folder_id = drive.get_folder_id(project_id_prefix, parent_folder_id=projects_folder_id)
    if project_folder_id == None:
        project_folder_id = drive.create_folder(project_id_prefix, parent_folder_id=projects_folder_id)


    platforms = project.user_input["platforms"]
    for platform in platforms.keys():
        #Creating google drive folder for each platform
        folder_id = drive.get_folder_id(platform, parent_folder_id=project_folder_id)
        if folder_id == None:
            drive.create_folder(platform, parent_folder_id=project_folder_id)
