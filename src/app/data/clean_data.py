from os import path,listdir
import pandas as pd
import utils

def getData():
    for element in listdir(utils.DIRTY_PATH):
        filePath = utils.DIRTY_PATH / element
        if (path.isfile(filePath)):
            cleanData(filePath,element)
    return

def cleanData(filePath,fileName):
    df = pd.read_csv(filePath, usecols=utils.BASE_COLUMNS)
    df.to_csv(f"{utils.CLEAN_PATH}/{fileName}")
    print(f"Saved in: {utils.CLEAN_PATH}")
    return

if __name__ == "__main__":
    getData()