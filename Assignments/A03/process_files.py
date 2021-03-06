"""
Course: cmps 4883
Assignemt: A03
Date: 2/13/19
Github username: JakobLopez
Repo url: https://github.com/JakobLopez/4883-SWTools-Lopez
Name: Jakob Lopez
Description: 
    Run nfl_scrape.py before running executing.
    This program ASSUMES gameid.json data is stored in a folder called
    game_data. This program is ran before calculate_stats.py because it
    builds a dictionary of paths to game data and writes it to files.txt,
    which calculate_stats.py uses to build its data structures. The function
    openFileJson is imported into calculate_stats.py to open up a valid
    json file, which is how the game data is stored.
"""
import json
import os,sys

"""
Name: getFiles
Description: 
    Returns a list of files in given directory
Params:
    path - folder that we want to get files from
Returns:
    List of files 
"""
def getFiles(path):
    files = []
    for dirname, dirnames, filenames in os.walk(path):
        # print path to all subdirectories first.
        # for subdirname in dirnames:
        #     print(os.path.join(dirname, subdirname))

        # print path to all filenames.
        for filename in filenames:
            #print(os.path.join(dirname, filename))
            files.append(os.path.join(dirname, filename))

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')
    return files


"""
Name: is_json
Description: 
    Determines if data from file is JSON
Params:
    myjson - data read from a JSON file
Returns:
    true if file is JSON, false otherwise 
"""
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError:
        return False
    return True


"""
Name: openFileJson
Description: 
    Opens file for reading.
    Convert JSON file to dictionary.
    Errors if path is not JSON.
Params:
    path - path to a JSON file
Returns:
    Dictionary if path is JSON
"""
def openFileJson(path):
    try:
      f = open(path, 'r')
      data = f.read()
      if is_json(data):
          return json.loads(data)
      else:
          print('Error: Not json.')
          return {}
    except IOError:
        print('Error: Game file doesn\'t exist.')
        return {}

#Path to folder with game data
path = './game_data/'

#Put all files in path inside a list
files = getFiles(path)
#Sorts list in numerical order
files = sorted(files)

with open('files.txt', mode='w') as myfile:
    myfile.write('\n'.join(files))