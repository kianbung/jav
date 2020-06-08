#JAV Reformatter

import os, re, logging, requests, bs4, shelve, shutil, send2trash
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)
# javCode = ['club','ssni', 'snis', 'abp', 'ipx', 'pppd', 'ebod']
javCodes = ['ssni', 'abp']

baseFolder = r'D:\Torrents (Pre-March 2020)\pon'
shelfLocalDB = shelve.open('javActressDB')
actressLocalDB = shelfLocalDB['actressLocalDB'] if shelfLocalDB else {} # checks if local file exists, else init new dict
logging.info('Current working directory: ' + os.getcwd())


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
        logging.info(f'Matched {javCode} to {actressLocalDB[javCode]}' if actressLocalDB[javCode] else 'Local null match')
        return actressLocalDB[javCode]
    else:
        actressName = actressOnlineSearch(javCode)
        actressLocalDB[javCode] = actressName
        return actressName
        


for folderName, subList, fileList in os.walk(baseFolder):
    
    for fileName in fileList:
        fileName, fileExt = os.path.splitext(fileName)

        for javCode in javCodes:
            javRegex = re.compile(r'(.*)((' + javCode + r')-?(\d+))', re.I)
            javDetect = javRegex.findall(fileName)

            if javDetect:
                toRename = False
                renameReasons = []
                fullOldPath = folderName + '\\' + fileName + fileExt
                
                logging.info('---')
                logging.info('Scanned: + ' + fullOldPath)
                logging.debug(javDetect)
                spacerRegex = re.compile(r'-')
                spacerDetect = spacerRegex.findall(javDetect[0][1])

                actressName = actressSearch(javDetect[0][2].upper() + javDetect[0][3]) # uppercase search

                if actressName:
                    actressRegex = re.compile(r'.*\(' + actressName + r'\).*')
                    actressDetect = actressRegex.search(fileName)
                    if not actressDetect:
                        toRename = True
                        renameReasons.append('add actress name')
                    else:
                        logging.debug('Regex success, actress name already present')

                if not spacerDetect:
                    toRename = True
                    renameReasons.append('no dash')
                    
                if javDetect[0][0]: #if there are prefixes
                    toRename = True
                    renameReasons.append('prefix detected')
                    
                if not javDetect[0][2].isupper(): #if JAV Code is not uppercase
                    toRename = True
                    renameReasons.append('code not uppercase')
                
                if toRename:
                    actressNameParens = f' ({actressName})' if actressName else ''
                    newName = f'{javDetect[0][2].upper()}-{javDetect[0][3]}{actressNameParens}{fileExt}'
                    
                    fullNewPath = folderName + '\\' + newName
                    logging.info('Renamed to: ' + fullNewPath)
                    logging.info('Reason: ' + ', '.join(renameReasons))
                    shutil.move(fullOldPath,fullNewPath)



                    
                if folderName != baseFolder:
                    logging.info('Move to base folder: ' + baseFolder)
                    if toRename:
                        logging.debug(fullNewPath)
                        sourcePath = fullNewPath
                    else:
                        logging.debug(fullOldPath)
                        sourcePath = fullOldPath
                    
                    shutil.move(sourcePath, baseFolder) #TODO: Crashes on duplicate file in destination folder
                    
                    logging.info(folderName + ' sent to Recycling bin')
                    send2trash.send2trash(folderName) #TODO: needs check for other video files in folder before transhing

shelfLocalDB['actressLocalDB'] = actressLocalDB
shelfLocalDB.close()