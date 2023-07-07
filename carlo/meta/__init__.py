from carlo.sheet import Sheet
from carlo import drive, project, github
from datetime import datetime
from itertools import groupby

def create_project_app_item(platform):
    app_id = project.app_id(platform)
    projects_sheet = Sheet.projects_sheet()
    project_app_item = projects_sheet.get_item(lambda item: item["app_id"] == app_id)
    if project_app_item == None:
        data = {
            "project_title": project.user_input()["project_title"],
            "project_id": project.user_input()["project_id"],
            "app_id": app_id,
            "platform": platform,
            "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        }
        return projects_sheet.insert_item(data)
    else:
        return project_app_item

def create_github_repo(projects_sheet, project_app_item):
    if project_app_item["github_repo_url"] != "":
        return
    platforms = project.user_input()["platforms"]
    repo_name = project_app_item["app_id"]
    collaborators = platforms[project_app_item["platform"]]["github_collaborators"]
    url = github.create_repo(repo_name, collaborators)
    if url != None:
        projects_sheet.set_item_value(project_app_item, url, key="github_repo_url")

def create_app_sheet(project_app_item, folder_id):
    template_id = project.keys()["app_sheet_template_id"]
    sheet_name = f"{project_app_item['project_title']} ({project_app_item['platform']}) - {project_app_item['app_id']}"
    return Sheet.duplicate_sheet(sheet_name, template_sheet_id=template_id, folder_id=folder_id, users=[])

def create_aso_drive_infrustructure():
    platform = "ios"
    base_folder_id = project.keys()["google_drive_root_folder_id"]
    project_id = project.user_input()["project_id"]
    ios_folder_id = drive.get_folder_id(f"projects/{project_id}/{platform}", parent_folder_id=base_folder_id)
    aso_folder_id = drive.get_folder_id("aso", parent_folder_id=ios_folder_id)
    if aso_folder_id == None:
        aso_folder_id = drive.create_folder("aso", parent_folder_id=ios_folder_id)

    screenshots_folder_id = drive.get_folder_id("screenshots", parent_folder_id=aso_folder_id)
    if screenshots_folder_id == None:
        screenshots_folder_id = drive.create_folder("screenshots", parent_folder_id=aso_folder_id)

    images_sheet = Sheet.app_sheet(platform, page="images")
    sorted_by_variation = sorted(images_sheet.items, key=lambda x: x['variation'])
    grouped_by_variation = groupby(sorted_by_variation, key=lambda x: x['variation'])
    for variation, image_items_of_variation in grouped_by_variation:
        print(variation, list(image_items_of_variation))
        variation_folder_id = drive.get_folder_id(variation, parent_folder_id=screenshots_folder_id)
        if variation_folder_id == None:
            variation_folder_id = drive.create_folder(variation, parent_folder_id=screenshots_folder_id)
        sorted_by_locale = sorted(image_items_of_variation, key=lambda x: x['locale'])
        grouped_by_locale = groupby(sorted_by_locale, key=lambda x: x['locale'])
        for locale, image_items_of_locale in grouped_by_locale:
            print(locale, list(image_items_of_locale))
            locale_folder_id = drive.get_folder_id(locale, parent_folder_id=variation_folder_id)
            if locale_folder_id == None:
                locale_folder_id = drive.create_folder(locale, parent_folder_id=variation_folder_id)
            for image_item in image_items_of_locale:
                print(image_item)


    

def create_drive_infrustructure():
    base_folder_id = project.keys()["google_drive_root_folder_id"]
    project_id_prefix = project.user_input()["project_id_prefix"]

    #Creating google drive 'projects' folder
    projects_folder_id = drive.get_folder_id("projects", parent_folder_id=base_folder_id)
    if projects_folder_id == None:
        projects_folder_id = drive.create_folder("projects", parent_folder_id=base_folder_id)

    #Creating google drive project folder
    project_folder_id = drive.get_folder_id(project_id_prefix, parent_folder_id=projects_folder_id)
    if project_folder_id == None:
        project_folder_id = drive.create_folder(project_id_prefix, parent_folder_id=projects_folder_id)


    platforms = project.user_input()["platforms"]
    projects_sheet = Sheet.projects_sheet()
    for platform in platforms.keys():
        #Creating google drive folder for each platform
        folder_id = drive.get_folder_id(platform, parent_folder_id=project_folder_id)
        if folder_id == None:
            folder_id = drive.create_folder(platform, parent_folder_id=project_folder_id)
        app_id = project.app_id(platform)
        project_app_item = projects_sheet.get_item(lambda item: item["app_id"] == app_id)
        if project_app_item["app_sheet_url"] == "":
            _, app_sheet_link = create_app_sheet(project_app_item, folder_id)
            projects_sheet.set_item_value(project_app_item, app_sheet_link, key="app_sheet_url")
