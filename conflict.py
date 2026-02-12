from scheduler import *


def modifyconflict_input(config: CombinedConfig):
    conflictNum = 1
    for course in config.config.courses:
        for conflict in course.conflicts:
            print(conflictNum + ": " + course + " conflicts with " + conflict)

    modifyNum = input("Which config would you like to modify? [1 - " + conflictNum + "]: ")