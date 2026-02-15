# room.py
# Functions to add/modify/delete a room
import json
from scheduler import load_config_from_file, scheduler
from scheduler.config import CombinedConfig

def deleteRoom(config_path: str):
    # Load configuration
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config
    
    # Check if any rooms exist
    if not scheduler_config.rooms:
        print("There are no rooms in the configuration.")
        return
    
    # Display existing rooms
    print("\nExisting Rooms:")
    for i, room in enumerate(scheduler_config.rooms, 1):
        print(f"{i}. {room}")
    
    # Prompt for room name
    while True:
        room_name = input("\nEnter the room name to delete: ").strip()
        if room_name != "":
            break
    
    # Find the room
    room_exists = any(r == room_name for r in scheduler_config.rooms)
    if not room_exists:
        print(f"\nError: No room '{room_name}' found. No changes were made.")
        return
    
    # Confirm deletion
    while True:
        confirm = input(f"Are you sure you want to delete room '{room_name}'? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break
    
    if confirm == 'n':
        print("Deletion canceled.")
        return
    
    # IMPORTANT: Remove room from all references BEFORE removing from rooms list
    # This avoids Pydantic validation errors
    
    # 1. Remove room from all courses first
    for course in scheduler_config.courses:
        course.room = [r for r in course.room if r != room_name]
    
    # 2. Remove room from faculty preferences
    for faculty in scheduler_config.faculty:
        if room_name in faculty.room_preferences:
            del faculty.room_preferences[room_name]
    
    # 3. NOW remove room from rooms list (do this LAST)
    scheduler_config.rooms = [r for r in scheduler_config.rooms if r != room_name]
    
    # Save back to file
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(mode="json"), f, indent=2)
        print(f"\nRoom '{room_name}' has been successfully deleted.")
    except Exception as e:
        print(f"\nError: Failed to save configuration: {e}")
        import traceback
        traceback.print_exc()

#get CombinedConfig file, get the config field(SchedulerConfig type), to add room to
configFile = "example.json"
loadedConfig = scheduler.load_config_from_file(scheduler.CombinedConfig, configFile)

def main():
    modRoom("Roddy 140")

#adds room to list in config
#you can pass a room in the parameter to add the object instead of prompting user input
def addRoom(room = None):
    print("addRoom called with: ", room)
    #non interactive section, allows us to skip user prompt
    if room is not None:
        print("within non interactive")
        if not room:   # prevent blank string
            return False

        if not existCheck(room):
            with loadedConfig.edit_mode() as editableConfig:
                editableConfig.config.rooms.append(room)
            saveRoomsToFile()
            return True
        else:
            return False
    else:
    #creates a loop so we can prompt to add more than one room
        while True:
            newRoom = genRoom()
            print("within interactive")
        #double checks that room is not blank
            if not newRoom.strip():
                print("Room cannot be blank")
                continue

            #checks if room already exists, adds to config if it does not exist in config
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
                print(f"room: {room} already exists within {loadedConfig.config.rooms}, do not add")
            #prompts user to add another room, if not then break
            if not promptAddRoom():
                break
                

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
def existCheck(room: str):
    return room in loadedConfig.config.rooms

#prompts the user to add a room
#returns true if input is y, false otherwise
def promptAddRoom():
    answer = input("Add another room?(y/n)")
    return answer.lower() == "y"

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
        if answer.lower() == "n":
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
    with open(configFile,"r") as f:
        data = json.load(f)

    data["config"]["rooms"] = loadedConfig.config.rooms

    with open(configFile,"w") as f:
        json.dump(data,f,indent=4)
if __name__ == "__main__":
    main()
