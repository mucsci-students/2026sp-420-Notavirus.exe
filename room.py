import scheduler
import json

#get CombinedConfig file, get the config field(SchedulerConfig type), to add room to
loadedConfig = scheduler.load_config_from_file(scheduler.CombinedConfig, "example.json")

def main():
    addRoom()

#adds room to list in config
#you can pass a room in the parameter to add the object instead of prompting user input
def addRoom(newRoom = None):
    #creates room if none was passed into parameter
    if newRoom is None:
        newRoom = genRoom()
    #checks existing, adds to config if it does not exist already
    if not(existCheck(newRoom)):
        try:
            with loadedConfig.edit_mode() as editableConfig:
                #saves to the config loaded in memory
                editableConfig.config.rooms.append(newRoom)
            #writes to the actual config file, saving for later use
            with open("example.json","r") as f:
                data = json.load(f)
            data["config"]["rooms"] = loadedConfig.config.rooms
            with open("example.json","w") as f:
                json.dump(data,f,indent=4)
            #feedback
            print("Room added")
        except ValueError:
            print("failed to add room ")
    else:
        print("room already exists, do not add")
    if(promptAddRoom()):
        addRoom()
            

#combines the prompts to create the Room string
def genRoom():
    
    return promptRoomBuilding() + " " + promptRoomNumber()

#prompts the room number
#will only return if it is a number
#returns string
def promptRoomNumber():
    roomNum = input("roomNum?: ").strip()
    if (roomNum.isdigit()):
        return roomNum
    else:
        print("not a number, try again")
        return promptRoomNumber()
    
#prompts the room building
#make sure building is capitalized and no extra whitespace
#returns string
def promptRoomBuilding():
    return input("building?: ").strip().capitalize()

#checks if room already exists
#returns true if it already exists
#returns false if it does not exist
def existCheck(room: scheduler.Room):
    for element in loadedConfig.config.rooms:
        #print("checking element: " + element)
        #print("matches: " + room +"?")
        if(element == room):
            #print("yes match")
            return True
        #print("no match")
    return False

def promptAddRoom():
    answer = input("Add another room?(y/n)")
    if (answer == "y"):
        return True
    return False
if __name__ == "__main__":
    main()