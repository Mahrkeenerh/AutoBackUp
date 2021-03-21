import os, sys
import shutil
import datetime
import json
from dateutil.parser import parse
from time import sleep
from plyer import notification


icon_path = "backup.ico"


# You know, get back?
def back_up(json_data):

    global icon_path

    sources = json_data['sources']
    listings = json_data['lists']
    destination_raw = json_data['destination']

    date = datetime.date.today().strftime(json_data['destination_format'])
    destination = destination_raw + "\\" + date

    # Some duplicate shit is going on
    if os.path.exists(destination):
        notification.notify(title="BACK-UP FILE ALREADY EXISTS",
                message=destination, app_icon=icon_path)
        return 1

    # Remove older stuff than keep_old
    for i in os.listdir(destination_raw):
        if datetime.datetime.now() - parse(i) > datetime.timedelta(days=json_data['keep_old']):
            shutil.rmtree(destination_raw + "\\" + i, onerror=onerror)

    os.makedirs(destination)

    # List stuff
    with open(destination + "\\ListingContents.txt", 'w') as lists:
        for listing in listings:
            print("\n" + listing, file=lists)
            print("\n" + "\n".join(list(os.listdir(listing))), file=lists)
            print(file=lists)

    # Copy paste all files to destination
    for source in sources:
        try:
            os.getenv("USERPROFILE")
            shutil.copytree(source, destination + "\\" + source.split("\\")[-1],
                    ignore=shutil.ignore_patterns("*.ini", "My *"))
        except (FileNotFoundError, shutil.Error) as error:
            notification.notify(title="BACK-UP ERROR", message=str(error), app_icon=icon_path)

    return 0


# Fix weird windows stuff (missing permissions ...)
def onerror(func, path, exc_info):

    os.chmod(path, 128)
    func(path)


# Check config.txt for any errors
def check_errors(json_data):

    global icon_path

    all_right = True

    # .ico
    if not os.path.isfile('backup.ico'):
        notification.notify(title="BACK-UP ERROR, ICON DOESN'T EXIST", message='backup.ico')

        return False

    # Sources
    try:
        for source in json_data['sources']:
            if not os.path.isdir(source):
                notification.notify(title="BACK-UP ERROR, SOURCE PATH DOESN'T EXIST",
                        message=source, app_icon=icon_path)

                all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, SOURCES DON'T EXIST",
                message='config.txt', app_icon=icon_path)

        all_right = False
    
    # Lists
    try:
        for listing in json_data['lists']:
            if not os.path.isdir(listing):
                notification.notify(title="BACK-UP ERROR, LIST PATH DOESN'T EXIST",
                        message=listing, app_icon=icon_path)

                all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, LISTS DON'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False

    # Sources or Lists
    if not json_data['sources'] and not json_data['lists']:
        notification.notify(title="BACK-UP ERROR", message="MISSING SOURCE OR LIST PATHS",
                app_icon=icon_path)

        all_right = False

    # Destinations
    try:
        if not json_data['destination']:
            notification.notify(title="BACK-UP ERROR", message="MISSING DESTINATION PATH",
                    app_icon=icon_path)

            all_right = False

        if not os.path.isdir(json_data['destination']):
            notification.notify(title="BACK-UP ERROR, DESTINATION PATH DOESN'T EXIST",
                    message=listing, app_icon=icon_path)
        
            all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, DESTINATION DOESN'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False

    # destination_format
    try:
        json_data['destination_format']

        try:
            datetime.datetime.now().strftime(json_data['destination_format'])
        except:
            notification.notify(title="BACK-UP ERROR, DESTINATION FORMAT INVALID VALUE",
                    message='config.txt', app_icon=icon_path)
        
            all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, DESTINATION FORMAT DOESN'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False

    # repeat
    try:
        if json_data['repeat'] != True and json_data['repeat'] != False:
            notification.notify(title="BACK-UP ERROR, REPEAT INVALID VALUE",
                    message=listing, app_icon=icon_path)
        
            all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, REPEAT DOESN'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False

    # time_format
    try:
        json_data['time_format']

        try:
            datetime.datetime.now().strftime(json_data['time_format'])
        except:
            notification.notify(title="BACK-UP ERROR, TIME FORMAT INVALID VALUE",
                    message='config.txt', app_icon=icon_path)
        
            all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, TIME FORMAT DOESN'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False

    # time_value
    try:
        json_data['time_value']
    except:
        notification.notify(title="BACK-UP ERROR, TIME VALUE DOESN'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False

    # sleep
    try:
        json_data['sleep']

        try:
            int(json_data['sleep'])
        except:
            notification.notify(title="BACK-UP ERROR, SLEEP INVALID VALUE",
                    message='config.txt', app_icon=icon_path)
        
            all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, SLEEP DOESN'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False


    # keep_old
    try:
        json_data['keep_old']

        try:
            int(json_data['keep_old'])
        except:
            notification.notify(title="BACK-UP ERROR, KEEP OLD INVALID VALUE",
                    message='config.txt', app_icon=icon_path)
        
            all_right = False
    except:
        notification.notify(title="BACK-UP ERROR, KEEP OLD DOESN'T EXIST",
                message='config.txt', app_icon=icon_path)
        
        all_right = False

    return all_right


def main():

    global icon_path

    os.environ['USERNAME']
    json_data = {}

    # Check files
    try:
        with open('config.txt') as json_config:
            json_data = json.load(json_config)

            if check_errors(json_data):
                notification.notify(title='BACK-UP', 
                        message='Running without any errors', app_icon=icon_path)
            else:
                return
    except:
        notification.notify(title="BACK-UP ERROR, LOADING CONFIG FILE FAILED",
                message='config.txt', app_icon=icon_path)     
    
    # Looooop
    while True:

        if json_data['repeat']:

            if datetime.datetime.now().strftime(json_data['time_format']) != json_data['time_value']:
                sleep(60)
                continue

        # Check again
        try:
            with open('config.txt') as json_config:
                json_data = json.load(json_config)

                if not check_errors(json_data):
                    return
        except:
            notification.notify(title="BACK-UP ERROR, LOADING CONFIG FILE FAILED",
                    message='config.txt', app_icon=icon_path)        

        # Initiate back-up
        return_code = back_up(json_data)
        if return_code == 0:
            notification.notify(title="BACK-UP", message="Successfully finished back-up",
                    app_icon=icon_path)

        if not json_data['repeat']:
            break
    
        sleep(json_data['sleep'])


# Fancy way to catch any error, hehehe
try:
    main()
except:
    e = sys.exc_info()[0]
    notification.notify(title="BACK-UP ERROR", message=str(e))
    sleep(10)
