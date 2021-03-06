#JAV Reformatter

import os, re, logging, requests, bs4, shelve, shutil, send2trash
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)
# javCodes = ['club','ssni', 'snis', 'abp', 'ipx', 'pppd', 'ebod']
javCodes = ['ssni', 'abp', 'ebod'] #shorter test list

baseFolder = r'D:\Torrents (Pre-March 2020)\pon'
shelfLocalDB = shelve.open('javActressDB')
actressLocalDB = shelfLocalDB['actressLocalDB'] if shelfLocalDB else {} # checks if local file exists, else init new dict
logging.info('Current working directory: ' + os.getcwd())

totalScannedFiles = 0
totalDetectedFiles = 0
totalProcessedFiles = 0
totalSkippedFiles = 0

def actressOnlineSearch(javCode):
    url = 'https://onejav.com/search/' + javCode
    javSearch = requests.get(url)
    javSoup = bs4.BeautifulSoup(javSearch.text, 'html.parser')
    actressSelect = javSoup.select('body > div > div:nth-child(2) > div > div > div.column.is-5 > div > div.panel > a')
    actressName = actressSelect[0].getText() if actressSelect else None
    logging.info(f'Retrieved actress name from OneJAV: {actressName}' if actressName else 'No actress match on OneJAV')
    return actressName

def actressSearch(javCode):

    if javCode in actressLocalDB.keys():
        logging.debug(f'Matched {javCode} to {actressLocalDB[javCode]}' if actressLocalDB[javCode] else 'Local null match')
        return actressLocalDB[javCode]
    else:
        logging.info(f'No local match, searching {javCode} on OneJAV')
        actressName = actressOnlineSearch(javCode)
        actressLocalDB[javCode] = actressName
        return actressName
        
def scanFolder(fileName, folderName):
    fileName, fileExt = os.path.splitext(fileName)

    for javCode in javCodes:
        javRegex = re.compile(r'(.*)((' + javCode + r')-?(\d+))', re.I)
        javDetect = javRegex.findall(fileName)

        if javDetect:
            global totalDetectedFiles
            totalDetectedFiles += 1
            renameReasons = []
            fullOldPath = folderName + '\\' + fileName + fileExt
            
            logging.info('---')
            logging.info('Scanned: ' + fullOldPath)
            logging.debug(javDetect)
            spacerRegex = re.compile(r'-')
            spacerDetect = spacerRegex.findall(javDetect[0][1])

            actressName = actressSearch(javDetect[0][2].upper() + javDetect[0][3]) # uppercase search

            if actressName:
                actressRegex = re.compile(r'.*\(' + actressName + r'\).*')
                actressDetect = actressRegex.search(fileName)
                if not actressDetect:
                    renameReasons.append('add actress name')
                else:
                    logging.debug('Regex success, actress name already present')

            if not spacerDetect:
                renameReasons.append('no dash')
                
            if javDetect[0][0]: #if there are prefixes
                renameReasons.append('prefix detected')
                
            if not javDetect[0][2].isupper(): #if JAV Code is not uppercase
                renameReasons.append('code not uppercase')
            
            if folderName != baseFolder:
                renameReasons.append('not in base folder')
                
                #shutil.move(sourcePath, baseFolder) #Crashes on duplicate file in destination folder, needs dupe check(IMPLEMENTED below)
                #logging.info(f'Moved {sourcePath} to {baseFolder}')
                #

                # logging.info(folderName + ' sent to Recycling bin')
                #send2trash.send2trash(folderName) #TODO: needs check for other video files in folder before trashing
                #TODO: (wishlist) needs to trash parent folder if parent folder is not baseFolder

            if renameReasons: #removed toRename bool, checking list is good enough. checks if any reason to rename file.
                actressNameParens = f' ({actressName})' if actressName else ''
                newFileName = f'{javDetect[0][2].upper()}-{javDetect[0][3]}{actressNameParens}{fileExt}'
                
                if newFileName not in os.listdir(baseFolder): # dupe check
                    fullNewPath = baseFolder + '\\' + newFileName
                    logging.info('Renamed/moved to: ' + fullNewPath)
                    logging.info('Reason: ' + ', '.join(renameReasons))
                    shutil.move(fullOldPath,fullNewPath)

                    global totalProcessedFiles
                    totalProcessedFiles += 1
                else:
                    logging.info('Rename/move skipped. Existing file in destination directory.')
                    global totalSkippedFiles
                    totalSkippedFiles += 1



                
            

for folderName, subList, fileList in os.walk(baseFolder):
    
    for fileName in fileList:
        totalScannedFiles += 1
        scanFolder(fileName, folderName)
        

logging.info('---')
logging.info(f'Total files scanned: {totalScannedFiles}')
logging.info(f'Total JAV files detected: {totalDetectedFiles}')
logging.info(f'Total JAV files processed: {totalProcessedFiles}')
logging.info(f'Total JAV files skipped: {totalSkippedFiles}')
shelfLocalDB['actressLocalDB'] = actressLocalDB
shelfLocalDB.close()