import scheduler

#get CombinedConfig file, get the config field(SchedulerConfig type), to add room to
loadedConfig = scheduler.load_config_from_file(scheduler.CombinedConfig, "example.json").config

def main():
    addRoom()

#adds room to list in config
def addRoom():
    #creates room
    newRoom = genRoom()
    #checks existing, adds to config if it does not exist already
    if not(existCheck(newRoom)):
        with loadedConfig.edit_mode() as editableConfig:
            try:
                editableConfig.rooms.append(newRoom)
                print("Room added")
            except ValueError:
                print("failed to add room, try again")
                addRoom()

#combines the prompts to create the Room string
def genRoom():
    
    return promptRoomBuilding() + " " + promptRoomNumber()

#prompts the room number
#returns string
def promptRoomNumber():
    return input("roomNum?: ")
#prompts the room building
#make sure building is capitalized
#returns string
def promptRoomBuilding():
    return input("building?: ").capitalize()

#checks if room already exists
#returns true if it already exists
#returns false if it does not exist
def existCheck(room: scheduler.Room):
    for element in loadedConfig.rooms:
        print("checking element: " + element)
        print("does match: " + room +"?")
        if(element == room):
            print("yes match")
            return True
        print("no match")
    return False
if __name__ == "__main__":
    main()