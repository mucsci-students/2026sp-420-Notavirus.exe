import scheduler
import json

#get CombinedConfig file, get the config field(SchedulerConfig type), to add room to
loadedConfig = scheduler.load_config_from_file(scheduler.CombinedConfig, "example.json")

def main():
    modRoom("Roddy 140")

#adds room to list in config
#you can pass a room in the parameter to add the object instead of prompting user input
def addRoom(room = None):
    #creates a loop so we can add more than one room
    while True:
        #creates room if none was passed into parameter
        if room is None:
            newRoom = genRoom()
        #checks existing, adds to config if it does not exist already
        if not existCheck(newRoom):
            try:
                with loadedConfig.edit_mode() as editableConfig:
                    #saves to the config loaded in memory
                    editableConfig.config.rooms.append(newRoom)
                #writes to the actual config file, saving for later use
                saveRoomsToFile()
                #feedback
                print("Room added")
            except ValueError:
                print("failed to add room")
        else:
            print("room already exists, do not add")
        #break the loop if we call with params, allows us to call without any user input
        #if we created a room, we will prompt the user if they want to add another room
        if room != None or not promptAddRoom():
            break
        newRoom = None
                

#combines the prompts to create the Room string
#can pass in the building and number to create a room with said building or number
#capitalizes building name when generatinh room
def genRoom(roomBuilding = None, roomNumber = None):
    #if roomBuilding was not passed in, prompt for the building
    if roomBuilding is None:
        roomBuilding = promptRoomBuilding()
    #if roomNumber was not passed in, prompt for the number
    if roomNumber is None:
        roomNumber = promptRoomNumber()
    #returns the string representing the room
    return roomBuilding.capitalize() + " " + roomNumber

#prompts the room number
#will only return if it is a number
#returns string containing the roomNumber
def promptRoomNumber():
    while True:
        roomNum = input("roomNum?: ").strip()
        if roomNum.isdigit():
            return roomNum
        print("not a number, try again")
    
#prompts the room building
#make sure building has no white space, and no two word building names(Science Hall)
#returns string
def promptRoomBuilding():
    while True:
        building = input("building?: ").strip()
        #we dont want a building name with spaces, will mess with modify
        if " " in building:
            print("building name cannot contain spaces")
            continue
        #we dont want an empty building name
        if building == "":
            print("building name cannot be empty")
            continue
        return building

#checks if room already exists
#returns true if it already exists
#returns false if it does not exist
def existCheck(room: scheduler.Room):
    return room in loadedConfig.config.rooms

#prompts the user to add a room
#returns true if input is y, false otherwise
def promptAddRoom():
    answer = input("Add another room?(y/n)")
    return answer == "y"

#modify the room function
#calling modRoom() will prompt the user for the building and number of the room, then information to modify
#calling modRoom("BuildingName RoomNumber") will check if that is a room in the config, and prompt the user for information to modify if it exists
#note: assuming modifying the room will leave the config valid, replaceRoom(oldRoom,newRoom) will skip all user input
def modRoom(room = None):
    if room == None:
        room = genRoom()
    #check to make sure the room already exists
    #must exist in order to modify, otherwise add new room
    while True:
        if existCheck(room):
            match modifyPrompt():
                case "building":
                    newBuilding = promptRoomBuilding()
                    #seperate the string on the space, save the number to use in the genRoom() call
                    roomNumber = splitRoomString(room)[2]
                    #replaces the old room with the modified room, created using genRoom with params
                    replaceRoom(room,genRoom(newBuilding,roomNumber) )
                case "number":
                    newNumber = promptRoomNumber()
                    #seperates the room string on the space, saves the building name
                    roomBuilding = splitRoomString(room)[0]
                    #replace old room with modified room
                    replaceRoom(room,genRoom(roomBuilding,newNumber))
                case _:
                    print("match failed, input should be building or number only, this is a fallback")
        #prompts the user to modify another room
        answer = input("Modify another room?(y/n)")
        if answer == "n":
            break
        #if the user wants to modify another room, prompt for the info
        room = genRoom()
#will replace the room passed in with the new room
#returns early if the room cannot be modified due to config validity or the new room already exists
def replaceRoom(oldRoom, newRoom):
    #checks if the modified room exists, cannot modify if it does
    try:
        if existCheck(newRoom):
            print("cannot update to this value, the modified value already exists")
            raise ValueError("room already exists")
        #validates the config file after edits were made,
        #throws ValueError if changes would make the file invalid, reverts any changes
        with loadedConfig.edit_mode() as editableConfig:
            rooms = editableConfig.config.rooms
            index = rooms.index(oldRoom)
            rooms[index] = newRoom
        saveRoomsToFile()
    except ValueError as e:
        print(f"error modifying room: {e}")
        return




#will split the room string passed in on the space, returns a tuple in the form [building, " ", number]
def splitRoomString(room: str):
    return room.partition(" ")

#Prompts the user to which part of the room do they want to modify
#can modify the building the room is in or the room number in the building
def modifyPrompt():
    while(True):
        answer = input("what part do you want to modify(building/number)").strip()
        if(answer == "building"):
            return answer
        elif(answer == "number"):
            return answer
        print("not a valid answer")

#saves the changes made from the loaded config(in memory) to the config file
def saveRoomsToFile():
    with open("example.json","r") as f:
        data = json.load(f)

    data["config"]["rooms"] = loadedConfig.config.rooms

    with open("example.json","w") as f:
        json.dump(data,f,indent=4)
if __name__ == "__main__":
    main()