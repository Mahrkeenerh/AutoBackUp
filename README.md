# AUTO BACK-UP APP

A program that can be used as a one tap back-up, or can frequently copy files without any input.


# INSTALLATION

App requires some python, some libraries (yeah, I didn't yet bother to work out auto installation), latest should work just fine, just the .pyw, config.txt and backup.ico files.

Before you run the app, make sure to set up config.txt

To have the app run with the start of the pc, make a shortcut into startup folder


# FREQUENT BACK-UP

If you want to use the frequent back-ups, the config file must have 'repeat' set to true

'time_format' must be something that datetime.strftime() can chew through.
If you don't know what that means, pick one from this list:

| time_format | meaning                                                 | examples      |
| ----------- | :-----:                                                 | --------      |
| '%H'        | 24 hours - used for daily back-up at specific hour      | '00' ... '24' |
| '%d'        | day of month - used for monthly back-up at specific day | '01' ... '31' |
| '%w'        | weekday - used for weekly back-up at specific day       | '1' ... '7'   |


# config.txt

This file is used for setting up the program.
It's a json style, if you don't know what that means, just don't mess up with the formatting.
On left, there is a name, that has to stay the same, on right, there is your value to edit.


## Contents

sources - where to copy all files from (everything inside the folder, all subfolders)

lists - where to list contents of a folder from (everything inside the folder, no subfolders)

destination - where to save everything that was copied

destination_format - format for creating back-up folders (strftime() again)

repeat - should the program run more than once

time_format - what to compare time_value with

time_value - at what specific value should the program make a back-up

sleep - time in seconds to sleep after back-up (to prevent duplicates)

keep_copies - how many copies should be kept at any time (1, 2 ...)

paths can be either relative or absolute


## Values

[] -> multiple values available, split with ,

repeat -> either true or false

Every value needs to be wrapped between "" but repeat and keep_copies

Numbers should be without extra zeroes at the beginning: 0, 1 ...


# DISCLAIMER

If you mess up anything, I take no responsibility for your actions.

If you need some help or found a bug, feel free to message me over at: samuelbuban@gmail.com
