import scheduler


#vars
#these are set when prompted in other functions, but saved for use when the scheduler will be ran
formatChoice = False
outputFile = ""
scheduleLimit = 0
configFileName = ""

def main(): #Mainly part of display/run scheduler
    global configFileName
    promptConfigFile()
    print(configFileName)
    runScheduler(scheduler.load_config_from_file(scheduler.CombinedConfig, configFileName))


def runScheduler(config: scheduler.CombinedConfig):
    specifyLimit()
    promptOutputFileName()
    
    config.limit = scheduleLimit
    generateSchedule(config,outputFile)

#Func to generate schedules
#parameter: config will be a CombinedConfig type, this contains everything the schedule needs to run
#this function does NOT do any prompts, just generates the schedule and outputs
#will output to output file AND console, 
def generateSchedule(config: scheduler.CombinedConfig, outputFile: str):

    #Runs the scheduler, becomes a Generator of classInstance models
    schedulerGen = scheduler.Scheduler(config)
    with open(outputFile, "w+") as f:

        #prints the generated schedules in csv format
        if(formatChoice):
            for model in schedulerGen.get_models():
                for course in model:
                    f.write(course.as_csv() + "\n")
                    print(course.as_csv())
                f.write("\n")
                print("\n")
        else:
            #output in json
            #does not work, need to convert the model into a json object, no built in function unlike csv
            for model in schedulerGen.get_models():
                for course in model:
                    #f.write(course.model_dump_json() + "\n")
                    print(course.model_dump_json() + "\n")
                f.write("\n")
                print("\n")

        

#function for prompting the output format, returns true for csv, false for json
#currently defaulting to json if anything other than "csv" is inputted
def promptFormat():
    formatInput = input("What output file format do you prefer? (csv or json)")
    if(formatInput == "csv"):
        return True
    return False

#function to specify output file, will prompt the user
#create file if it doesnt exist, if already exists, it will be over written
#sets the file name and format
def promptOutputFileName():
    global formatChoice 
    global outputFile
    fileName = input("What do you want to call the output file?: ")
    formatChoice = promptFormat()
    if formatChoice:
        outputFile = fileName + ".csv"
        return
    outputFile = fileName + ".json"

#prompt user to specify the limit
# will recall itself if a number was not inputted
def specifyLimit():
    try:
        global scheduleLimit
        scheduleLimit = int(input("What is the max number of schedules you want generated?"))
        return
    except ValueError:
        print("Not a number try again")
        specifyLimit()  
#Prompts the name of the config file
def promptConfigFile():
    global configFileName
    configFileName = input("Which config file do you want to use(Must be a CombinedConfig)")

if __name__ == "__main__":
    main()
