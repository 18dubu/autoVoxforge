#basic operations for files
#original author: rm3086 (at) columbia (dot) edu
#added and modified by Handong Ma: hm2588 (at) columbia (dot) edu

import csv, shutil, os, glob, cPickle
import re
import sys
import inspect
import shlex, subprocess
import difflib

def numToWords(num,join=True):
    '''words = {} convert an integer number into words'''
    units = ['','one','two','three','four','five','six','seven','eight','nine']
    teens = ['','eleven','twelve','thirteen','fourteen','fifteen','sixteen', \
             'seventeen','eighteen','nineteen']
    tens = ['','ten','twenty','thirty','forty','fifty','sixty','seventy', \
            'eighty','ninety']
    thousands = ['','thousand','million','billion','trillion','quadrillion', \
                 'quintillion','sextillion','septillion','octillion', \
                 'nonillion','decillion','undecillion','duodecillion', \
                 'tredecillion','quattuordecillion','sexdecillion', \
                 'septendecillion','octodecillion','novemdecillion', \
                 'vigintillion']
    words = []
    if num==0: words.append('zero')
    else:
        numStr = '%d'%num
        numStrLen = len(numStr)
        groups = (numStrLen+2)/3
        numStr = numStr.zfill(groups*3)
        for i in range(0,groups*3,3):
            h,t,u = int(numStr[i]),int(numStr[i+1]),int(numStr[i+2])
            g = groups-(i/3+1)
            if h>=1:
                words.append(units[h])
                words.append('hundred')
            if t>1:
                words.append(tens[t])
                if u>=1: words.append(units[u])
            elif t==1:
                if u>=1: words.append(teens[u])
                else: words.append(tens[t])
            else:
                if u>=1: words.append(units[u])
            if (g>=1) and ((h+t+u)>0): words.append(thousands[g]+',')
    if join: return ' '.join(words)
    return words


def read_file_as_2D_dict(file, separater=' '):
    with open(file, 'r') as fhIn:
        all = fhIn.readlines()
        if all:
            dict1 = dict()
            array = [re.split(separater, x.rstrip()) for x in all]
            for i in range(len(array)):
                tmp = {}
                for j in range(len(array[i])):
                    tmp[j] = array[i][j]
                dict1[i] = tmp
            return dict1
        else:
            return False


def getWordCountEachLine(file):
    with open(file,'r') as fhIn:
        all = fhIn.readlines()
        if all:
            count = []
            for i in all:
                count.append(len(i.rstrip().split(' ')))
            return count
        else:
            return False


def removeMHatInFile(inputFile):
    with open(inputFile, 'r') as fhIn:
        lines = fhIn.read()
    lines_new = lines.replace('\r','')
    fhOut = open(inputFile,'wb')
    fhOut.write(lines_new)
    fhOut.close()


def excludeNamesStartWith(listOfNames, customizeSymbolSpaceSeparated = ''):
    defaultSymbols = ['.','_']
    if customizeSymbolSpaceSeparated:
        defaultSymbols.extend(customizeSymbolSpaceSeparated)
    cleanFiles = listOfNames
    for currSymbols in defaultSymbols:
        cleanFiles = [x for x in cleanFiles if not x.startswith(currSymbols)]
    return cleanFiles

def getDirNamesInCurrDir(currDir):
    currDir = check_dir(currDir)
    files = os.listdir(currDir)
    files = excludeNamesStartWith(files)
    paths = [currDir + x for x in files]
    dirs = [x for x in paths if os.path.isdir(x)]
    return dirs

def unzipDir(dirPath, mode='s', reName=True):
    #not finished
    methods = {
        'tgz': 'tar zxvf ',
        'tar': 'tar -xvf ',
        'bz2': 'tar -xjvf',
        'gz': 'tar -xzvf',
        'zip': 'unzip ',
        '7z': '7za x'
    }
    files = os.listdir(dirPath)
    cleanFiles = [x for x in files if not x.startswith('.')]  # remove files start with .

    if mode == 's':
        # check all zip files are known type
        namesList = [x.split('.').pop(0) for x in cleanFiles]
        extensionsList = [x.split('.')[1:] for x in cleanFiles]
        maxZipDepth = max([len(x.split('.')[1:]) for x in cleanFiles])
        extensions = set([item for sublist in extensionsList for item in sublist])
        if extensions <= set(methods.keys()):  # all known
            ifContinue()
    else:
        print 'unknown mode at this stage'
        return False

def removeEmptyLinesInFile(fileName):
    command0 = 'cp ' + fileName + ' ' + fileName + '_backup'
    command1 = 'sed \'/^$/d\' ' + fileName + ' > tmp'
    command2 = 'mv tmp ' + fileName
    command3 = 'rm ' + fileName + '_backup'
    try:
        os.system(command0)
    except Exception as e:
        print e
        print 'Input error'
        return False
    try:
        os.system(command1)
        os.system(command2)
        os.system(command3)
    except Exception:
        print Exception
        print 'backup file created *_backup'
        return False

def addBlankLineAtFileEnd(fileName):
    try:
        fhOut = open(fileName, 'a')
        fhOut.write('\n')
        fhOut.close()
    except Exception as e:
        print e
        return False

def sed(lineContent, sourceFile, targetFile):

    if isinstance(lineContent, str):
        command_line1 = 'sed /^' + lineContent + '$/d ' + sourceFile + ' > ./tmp'  # remove the short-pause "sp" entry
        command_line2 = 'mv ./tmp ' + targetFile
        try:
            os.system(command_line1)
        except Exception as e:
            print 'sed wrong: command line1', str(e)
        try:
            os.system(command_line2)
        except Exception as e:
            print 'sed wrong: command line2', str(e)
    if isinstance(lineContent, list):
        for i in lineContent:
            command_line1 = 'sed /^' + i + '$/d ' + sourceFile + ' > ./tmp'  # remove the short-pause "sp" entry
            command_line2 = 'mv ./tmp ' + targetFile
            try:
                os.system(command_line1)
            except Exception as e:
                print 'sed wrong: command line1', str(e)
            try:
                os.system(command_line2)
            except Exception as e:
                print 'sed wrong: command line2', str(e)

def sed_replace(contentToFind, contentChangeTo, sourceFile, targetFile):
    if isinstance(contentToFind, str):
        command_line1 = 'sed -e s/' + contentToFind+'/'+contentChangeTo + '/g ' + sourceFile + ' > ./tmp'  # remove the short-pause "sp" entry
        command_line2 = 'mv ./tmp ' + targetFile
        try:
            os.system(command_line1)
        except Exception as e:
            print 'sed wrong: command line1', str(e)
        try:
            os.system(command_line2)
        except Exception as e:
            print 'sed wrong: command line2', str(e)


def searchFileWithSimilarNameMotif_returnBest(pathToSearch, motif, caseSensitive = False):
    oriFiles = os.listdir(pathToSearch)
    oriFiles = excludeNamesStartWith(oriFiles)
    return searchMostSimilarStringInList(oriFiles,motif)

#partial string matching
def searchMostSimilarStringInList(listToSearch, motif, caseSensitive=False):
    oriFiles = listToSearch
    mapFiles = []
    if not caseSensitive:
        mapFiles = [x.upper() for x in oriFiles]
        motif = motif.upper()
    bestScore = 0
    bestMatch = None
    for i in range(len(oriFiles)):
        currFile = oriFiles[i]
        if difflib.SequenceMatcher(None, mapFiles[i], motif).ratio() > bestScore:
            bestMatch = currFile
            bestScore = difflib.SequenceMatcher(None, mapFiles[i], motif).ratio()
    return bestMatch

def cmd(command_line):
    try:
        args = shlex.split(command_line)
        p = subprocess.call(args)
    except Exception:
        print "integrate PROMPTS file error"
        exit()

def cmd_stdout2file(command_line, outfile):
    logfile = open(outfile, 'w')
    args = shlex.split(command_line)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) #open('/dev/null', 'w')
    for line in proc.stdout:
        sys.stdout.write(line)
        logfile.write(line)
    proc.wait()


def cat(outFilePath, filenamesList):
    with open(outFilePath, 'w') as outfile:
        for fname in filenamesList:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line)


def vi(fileName):
    try:
        open(fileName, 'a')
        return True
    except:
        return False

def rm(fileName):
    try:
        command = ''
        if os.path.isfile(fileName):
            command = 'rm -f ' + fileName
        if os.path.isdir(fileName):
            command = 'rm -rf ' + fileName
        if not command =='':
            os.system(command)
        else:
            return 'unknow input'
    except Exception as e:
        print e
        return False


#$$$$$$$$$#
def ifContinue():
    decision = raw_input('Wait for your command: continue(c) or stop(any key)')
    if decision == 'c':
        return True
    else:
        sys.exit(0)

#$$$$$$$# check if a file exist
def file_exist (fname):
    try:
        open(fname,'r')
        return True
    except IOError:
        return False


#$$$$$$$$#
def mkdir(dirname):
    if not dirname:
        return False
    try:
        os.makedirs(dirname)
    except OSError:
        pass
    except Exception as e:
        print(e)
        return False
    return True

#$$$$$$$$$#
def backup(affectedFileList):
    total_length = len(affectedFileList)
    wait = 0
    while len(affectedFileList) > 0:
        file = affectedFileList.pop(0)
        if file_exist(file):
            path = os.path.dirname(file)
            name = os.path.basename(file)
            new_path = path+'/backup/'
            mkdir(new_path)
            if file_exist(new_path+name):
                try:
                    if wait <= total_length:
                        wait += 1
                        affectedFileList.append(file)
                        continue
                    else:
                        print "whether want to overwrite earlier backed file: " + str(file)
                        ifContinue()
                        shutil.copyfile(file,new_path+name)
                        print "successfully update old backup" + str(file)
                except Exception as e:
                    print 'error when backup'
            else:
                shutil.copyfile(file,new_path+name)
                print "successfully new backups: " + str(file)


#check the dir name whether is standard with a '/' in the end
def check_dir(dirName):
    if re.findall('/$',dirName):
        return str(dirName)
    else:
        return str(dirName + '/')


#$$$$$$$$$$$$#return and print variable name
def varName(p):
  for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
    m = re.search(r'\bvarName\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
    if m:
      return m.group(1)

###
def continueOrNot():
    decision = raw_input('File exists! Wait for your decision: continue(c) or stop(any key)')
    if decision == 'c':
        return True
    else:
        sys.exit("stopped")

#$$$$$$$$$#
def checkFileIfContinue(affectedFileList):
    call = 0
    for file in affectedFileList:
        if file_exist(file):
            call = 1
            break
    if call==1:
        decision = raw_input('File exists! Wait for your decision: continue(c) or stop(any key)')
        if decision == 'c':
            return True
        else:
            sys.exit("stopped")



# create directory if not existing
#$$$$$$$$$$$$$#
#mkdir(above)

# create directory (delete if one with the same name already exists)
def mk_new_dir (dirname):
    try:
        os.makedirs (dirname)
    except OSError:
        shutil.rmtree(dirname)
        os.makedirs (dirname)
    except Exception as e:
        print (e)
        return False
    return True


# copy a file from "source" to "destination"
def fcopy (source, destination):
    try:
        shutil.copy2 (source, destination)
    except Exception as e:
        print(e)
        return False
    return True


# return the files of a directory with extension "ext"
def flist (directory, ext):
    try:
        os.chdir(directory)
        if ext[0:2] != '*.':
            ext = '*.' + ext
        data = []
        for f in glob.glob(ext):
            data.append(f.strip())
        return data
    except Exception as e:
        print(e)
        return None


### read operations ###

# read a text file
# @param struct: save data to (1) list, (2) set
def read_file (filename, struct = 1, logout = True):
    try:
        fid = open(filename, 'r')
        if struct == 2:
            # set
            data = set()
            for line in fid:
                if len(line) > 0:
                    data.add (line.strip())
        else:
            # default - list
            data = []
            for line in fid:
                if len(line) > 0:
                    data.append (line.strip())
        fid.close()
        return data
    except Exception as e:
        if logout is True:
            print(e)
        return None

# read a text file, break lines according to skip
# @param skip: character to skip (default ' ')
def read_file_tokenized (filename, skip = ' ', logout = True):
    try:
        data = []
        fid = open (filename, 'r')
        for line in fid:
            line = line.strip()
            data.append (line.split(skip))
        fid.close()
        return data
    except Exception as e:
        if logout is True:
            print(e)
        return None

# read text
def read_text (filename, logout = True):
    try:
        fid = open (filename,'r')
        data = fid.read ()
        data = data.replace ('\n',' ').replace('\t',' ')
        data = ' '.join(data.split()).strip()
        fid.close()
        return data
    except Exception as e:
        if logout is True:
            print(e)
        return None


# read data from a csv file
def read_csv(filename, header='T', logout=True):
    try:
        fhIn = open(filename, "rU")
        name = []
        reader = csv.reader(fhIn)
        data = []
        firstLine = 'T'
        for r in reader:
            if header == 'T' and firstLine == 'T':
                name = r
                firstLine = 'F'
                continue
            if not len(str(r)) or str(r).startswith('#'):
                print 'skipped line:' + r
                continue
            if (len(r) != len(name)):
                print "Warning: line length differs with name(%s) in line:" % len(name) + r
            data.append(r)
        return data, name
    except Exception as e:
        if logout is True:
            print(e)
        return None

# read a dictionary from a csv file
# @param iKey: column to consider as key (default 0)
# @param iData: column to consider as data (default 1)
def read_csv_as_dict (filename, iKey = 0, iData = 1, logout = True):
    try:
        reader = csv.reader (open(filename, "r"))
        data = {}
        for r in reader:
            data[r[iKey].strip()] = r[iData].strip()
        return data
    except Exception as e:
        if logout is True:
            print(e)
        return None

# read a dictionary from a csv file (column '0' is the keys)
def read_csv_as_dict_with_multiple_items (filename, logout = True):
    try:
        reader = csv.reader (open(filename, "r"))
        data = {}
        for r in reader:
            data[r[0].strip()] = r[1:len(data)]
        return data
    except Exception as e:
        if logout is True:
            print(e)
        return None

# read an object (list, dictionary, set) from a serialized file
def read_obj (filename, logout = True):
    try:
        data = cPickle.load (open(filename, 'rb'))
        return data
    except Exception as e:
        if logout is True:
            print(e)
        return None


### write operations ###

# write data to a csv file
def write_csv (filename, data, logout = True):
    try:
        doc = csv.writer (open(filename, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for d in data:
            doc.writerow (d)
        return True
    except Exception as e:
        if logout is True:
            print(e)
        return False

# write data to a text file
def write_file (filename, data, logout = True):
    try:
        fid = open (filename,'w')
        for d in data:
            fid.write('%s\n' % d.encode('utf-8'))
        fid.close()
        return True
    except Exception as e:
        if logout is True:
            print(e)
        return False

# write text
def write_text (filename, data, logout = True):
    try:
        fid = open (filename,'w')
        fid.write('%s' % data.encode('utf-8'))
        fid.close()
        return True
    except Exception as e:
        if logout is True:
            print(e)
        return False


# write an object (list, set, dictionary) to a serialized file
def write_obj (filename, data, logout = True):
    try:
        cPickle.dump(data, open(filename, 'wb'))
        return True
    except Exception as e:
        if logout is True:
            print(e)
        return False


def readCol(fileName, colNum, sep='\t', header='F'):
    """

    :param fileName:
    :param colNum: from 1~
    :param sep: default as \t
    :param header: default as F
    """
    try:
        fh = open(fileName,'r')
        if header == 'T':
            fh.readline()
        lines = fh.readlines()
        col = [i.replace('\n', '').split(sep)[colNum-1] for i in lines]
        fh.close()
        return col
    except IOError:
        return False


#readCol('../data/preparation/allCDE', 1)





