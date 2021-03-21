import os, sys
import shutil
import datetime
from time import sleep
from plyer import notification


icon_path = "backup.ico"


# You know, get back?
def back_up(sources, listings, destination_raw):

    global icon_path

    date = datetime.date.today().strftime("%Y.%m.%d")
    destination = destination_raw + "\\" + date

    # Some duplicate shit is going on
    if os.path.exists(destination):
        notification.notify(title="BACK-UP FILE ALREADY EXISTS",
                            message=destination, app_icon=icon_path)
        return
                           
    os.makedirs(destination)

    with open(destination + "\\ListingContents.txt", "w") as lists:
        for listing in listings:
            print(listing, "\n", file=lists)
            print("\n".join(list(os.listdir(listing))), file=lists)
            print("\n\n", file=lists)

    # remove older stuff than one day
    for i in range(2, 50):
        old_date = (datetime.date.today() - datetime.timedelta(days=i)).strftime("%Y.%m.%d")
        if os.path.exists(destination_raw + "\\" + old_date):
            shutil.rmtree(destination_raw + "\\" + old_date, onerror=onerror)

    # copy paste all files to destination
    for file in sources:

        try:
            user_profile = os.getenv("USERPROFILE")
            shutil.copytree(file, destination + "\\" + file.split("\\")[-1],
                                  ignore=shutil.ignore_patterns("*.ini", "My *"))
            
        except (FileNotFoundError, shutil.Error) as error:
            notification.notify(title="BACK-UP ERROR", message=str(error), app_icon=icon_path)


# Fix weird windows stuff (missing permissions ...)
def onerror(func, path, exc_info):

    os.chmod(path, 128)
    func(path)


def main():

    global icon_path

    os.environ['USERNAME']

    notification.notify(title="BACK-UP", message="Running", app_icon=icon_path)

    # Looooop
    while True:

        if datetime.datetime.now().hour != 19:
            sleep(60)
            continue

        sources = []
        lists = []
        destination = ""

        # Load source files
        with open("sources", "r") as file:
            for line in file:
                if line:
                    if os.path.isdir(line.strip()):
                        sources.append(line.strip())
                    else:
                        notification.notify(title="BACK-UP ERROR, SOURCE PATH DOESN'T EXIST",
                                            message=line.strip(), app_icon=icon_path)

        # Load list files
        with open("lists", "r") as file:
            for line in file:
                if line:
                    if os.path.isdir(line.strip()):
                        lists.append(line.strip())
                    else:
                        notification.notify(title="BACK-UP ERROR, LIST PATH DOESN'T EXIST",
                                            message=line.strip(), app_icon=icon_path)

        # Load destination folder
        with open("destination", "r") as file:
            line = file.readline()
            if os.path.isdir(line.strip()):
                destination = line.strip()
            else:
                notification.notify(title="BACK-UP ERROR, DESTINATION PATH DOESN'T EXIST",
                                    message=line.strip(), app_icon=icon_path)

        if not sources:
            notification.notify(title="BACK-UP ERROR", message="MISSING SOURCE PATHS",
                                app_icon=icon_path)

        if not destination:
            notification.notify(title="BACK-UP ERROR", message="MISSING DESTINATION PATH",
                                app_icon=icon_path)

        # Do back-up
        if sources and destination:
            back_up(sources, lists, destination)
            notification.notify(title="BACK-UP", message="Successfully finished back-up",
                                app_icon=icon_path)

        sleep(60 * 60 * 23)


# Fancy way to catch any error, hehehe
try:
    main()
    
except:
    e = sys.exc_info()[0]
    notification.notify(title="BACK-UP ERROR", message=str(e), app_icon=icon_path)
