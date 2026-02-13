# room.py
# Functions to add/modify/delete a room
import json
from scheduler import load_config_from_file
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