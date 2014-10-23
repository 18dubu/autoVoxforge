__author__ = 'mahandong'

import os, errno, re
from lib.file import *
from lib.string import *
import shlex, subprocess

###########################################################################
dataDir = check_dir('/Volumes/1/data/')  # './data/'

createdDir = ['./manual', './lexicon', './train']
defaultZipFileExtension = '.tgz'
defaultWavFileExtension = '.wav'
promptsSubDir = 'etc/'  # dir that within each data zip file and contain PROMPTS file
wavSubDir = 'wav/'  # dir that within each data zip file and contain wav files
mfcSubDir = 'mfc/'
integratedPROMPTSFilePath = "./manual/prompts"

wlistFullPath = './manual/wlist'
dlogFullPath = './manual/dlog'

cmd_list = []
###########################################################################
def init(createdDir):
    for currDir in createdDir:
        if not os.path.exists(currDir):
            mkdir(currDir)
init(createdDir)

#create create a prompts file - which is the list of words we will record in the next Step;
targetDataFolder = []  # all folders that has a defaultZipFileExtension file
def unzipFolders(dataDir):
    dataFiles = os.listdir(dataDir)
    for i in dataFiles:
        if os.path.splitext(i)[-1] == defaultZipFileExtension:  # all zip files
            if os.path.splitext(i)[0] not in targetDataFolder:
                targetDataFolder.append(os.path.splitext(i)[0])  # 23yipikaye-20100807-ujm
            if 1:#not os.path.isdir(dataDir + os.path.splitext(i)[0]):
                command_line = 'tar -zxf ' + dataDir + i + ' -C ' + dataDir
                cmd_list.append(command_line)
                cmd(command_line)
    print str(len(targetDataFolder)) + ' data folders in data source'
unzipFolders(dataDir)

#check: each dir must have PROMPTS file /WAV folder to be included
#long time
passDir = []
def checkDataQuality(targetDataFolder, modifyPrompts=0):
    length1 = len(targetDataFolder)
    totalModifiedNumber = 0
    for i in targetDataFolder:
        promptsName = dataDir + check_dir(i) + promptsSubDir + 'PROMPTS'
        wavDir = dataDir + check_dir(i) + wavSubDir
        if (not file_exist(promptsName)) or (not os.path.isdir(wavDir)):
            targetDataFolder.remove(i)
            passDir.append(i)
        else:
            if modifyPrompts == 1:
                modify = 0
                with open(promptsName) as p:
                    content = p.read()
                    last = content.rsplit('\n')[-1]
                    ### all the modifications needed for the prompts file
                    ###list of changes
                    replacedText = content
                    #replacedText = content.replace(' & ', ' AND ')
                    #replacedText = replacedText.replace(' 2000 ', ' TWO THOUSAND ')
                    #replacedText = replacedText.replace("\'EM", "THEM")
                    if replacedText != content:
                        modify = 1
                        with open(promptsName, 'w') as newFile:
                            newFile.write(replacedText)
                        newFile.close()
                    ###
                    if not last.strip() == '':
                        modify = 1
                        addBlankLineAtFileEnd(promptsName)
                if modify == 1:
                    totalModifiedNumber += 1
    print str(length1 - len(targetDataFolder)) + ' dir do not contain PROMPTS file or WAV folder, ' + str(len(targetDataFolder)) + ' left usable'
    targetDataFolder.sort()
checkDataQuality(targetDataFolder, 0)

existing = os.listdir(dataDir)
targetDataFolder_existing = list(set(existing) & set(targetDataFolder))
dataPROMPTSPathList = [dataDir + check_dir(i) + promptsSubDir + 'PROMPTS' for i in targetDataFolder_existing]
passDir.extend(list(set(targetDataFolder)-set(targetDataFolder_existing)))
#generate integratedPROMPTSFile
# LONG
def getPrompts(integratedPROMPTSFilePath, dataPROMPTSPathList, dataDir):
    if file_exist(integratedPROMPTSFilePath):
        rm(integratedPROMPTSFilePath)
        vi(integratedPROMPTSFilePath)
    [addBlankLineAtFileEnd(x) for x in dataPROMPTSPathList]
    cat(integratedPROMPTSFilePath, dataPROMPTSPathList)
    removeEmptyLinesInFile(integratedPROMPTSFilePath)

    #modify current prompts file to contain the full path in the first col
    ###fast
    fhOut = open(integratedPROMPTSFilePath + '_tmp', 'wb')
    with open(integratedPROMPTSFilePath, 'r') as prompts:
        lines = prompts.readlines()
    prompts.close()
    for i in lines:
        fhOut.write(check_dir(dataDir) + i)
    fhOut.close()
    command_line = 'mv ' + integratedPROMPTSFilePath + '_tmp ' + integratedPROMPTSFilePath
    os.system(command_line)
    removeEmptyLinesInFile(integratedPROMPTSFilePath)
    ###
    print 'Integrated prompts file generated'
getPrompts(integratedPROMPTSFilePath, dataPROMPTSPathList, dataDir)
#########################################################################
#generate wlist file
"""
The HTK Perl script prompts2wlist can take the prompts file you just created,
and remove the file name in the first column and print each word on one line into a word list file (wlist).
"""
def getWlist(wlistFullPath, integratedPROMPTSFilePath):
    try:
        command_line = 'perl ./lib/HTK_scripts/prompts2wlist ' + integratedPROMPTSFilePath + ' ' + wlistFullPath
        cmd_list.append(command_line)
        cmd(command_line)
        print 'wlist generated'
    except Exception as e:
        print 'wlist generation error' + str(e)
        ifContinue()

    # wlist contains non-alphabetical characters:  ERROR [+5013]  ReadString: String too long
    #normalize wlist file by Handong Ma
    command_lines = ['cp ' + wlistFullPath + ' ' + wlistFullPath + '_ori',
        'sed \'/[\\"\,\:\;\&\.\\\/\!\s*]/d\' '+ wlistFullPath + ' > ./tmp1',
        'tr \'[:lower:]\' \'[:upper:]\' < ./tmp1 > ./tmp2', # TO UPPER CASE
        'sed \'/^-/d\' ./tmp2 > tmp1',
        'sed "/^\'/d" tmp1 > tmp2',
        'sed -e \'s/[0-9]*//g\' tmp2 > tmp1', # DELETE NUMBERS
        'sed \'/^$/d\' tmp1 > tmp2',  # DELETE EMPTY LINE
        'awk \'!x[$0]++\' tmp2 > ' + wlistFullPath,
        'rm tmp1 tmp2']

    for command_line in command_lines:
        os.system(command_line)

    #manually add the following entries to your wlist file (in sorted order):
    try:
        fhOut = open(wlistFullPath, 'a')
        fhOut.write('SENT-END\nSENT-START')
        fhOut.close()
        command_line = 'sort ' + wlistFullPath + ' -o ' + wlistFullPath
        cmd_list.append(command_line)
        os.system(command_line)
        print "wlist file edited and sorted"
    except:
        print "edit wlist file error"
        ifContinue()
getWlist(wlistFullPath, integratedPROMPTSFilePath)

# add pronunciation dictionary
'''
The next step is to add pronunciation information (i.e. the phonemes that make up the word) to each of the words in the wlist file,
thus creating a Pronunciation Dictionnary.  HTK uses the HDMan command to go through the wlist file,
and look up the pronunciation for each word in a separate lexicon file,
and output the result in a Pronunciation Dictionnary.
'''
def runHDManGetMonophone(wlistFullPath,dictPath='./manual/dict',mono0Path='./manual/monophones0',mono1Path='./manual/monophones1',dlogPath='./manual/dlog'):
    fhOut = open('./manual/global.ded', 'w')
    fhOut.write(
        'AS sp\nRS cmu\nMP sil sil sp')  # This is mainly used to convert all the words in the dict file to uppercase
    fhOut.close()

    command_line = 'cp ./lib/support_data/VoxForge/VoxForgeDict ./lexicon/'
    cmd_list.append(command_line)
    cmd(command_line)

    #this step requires that HTK is successfully installed on the machine and HDMan is executable
    try:
        #run HDMan
        command_line = "HDMan -A -D -T 1 -m -w "+wlistFullPath+" -n "+mono1Path+" -i -l "+dlogPath+" "+dictPath+" ./lexicon/VoxForgeDict"
        cmd_list.append(command_line)
        cmd(command_line)

        #create monophones0

        command_line = 'sed /^sp$/d '+mono1Path+' > '+mono0Path  # remove the short-pause "sp" entry
        cmd_list.append(command_line)
        os.system(command_line)
        ##method 2, with stdout
        #command_line = 'sed /^ax$/d ./manual/monophones1'
        #cmd_stdout2file(command_line, './manual/monophones0')
        print 'HDMan program run and monophones1/dict/monophones0 files created'
    except Exception as e:
        print 'HDMan running error' + str(e)
        ifContinue()
runHDManGetMonophone(wlistFullPath)

#create a Master Label File (MLF)
def getMLF():
    try:
        command_line = 'perl ./lib/HTK_scripts/prompts2mlf ./manual/words.mlf ./manual/prompts'
        cmd_list.append(command_line)
        cmd(command_line)
    except Exception as e:
        print 'mlf file creating error: ', str(e)
        ifContinue()

    ####modify mlf file
    os.system('sed -e \'s/^2000$/TWO THOUSAND/g\' ./manual/words.mlf > ./manual/words.mlf_new')
    os.system('sed -e \'s/^&$/AND/g\' ./manual/words.mlf_new > ./manual/words.mlf')
    os.system('sed -e \"s/^\'EM$/THEM/g\" ./manual/words.mlf > ./manual/words.mlf_new')
    os.system('mv ./manual/words.mlf_new ./manual/words.mlf')
getMLF()
#Phone Level Transcriptions
"""
Next you need to execute the HLEd command to expand the Word Level Transcriptions to Phone Level Transcriptions - i.e.
replace each word with its phonemes, and put the result in a new Phone Level Master Label File
This is done by reviewing each word in the MLF file,
and looking up the phones that make up that word in the dict file you created earlier,
and outputing the result in a file called phones0.mlf (which will not have short pauses ("sp"s) after each word phone group).
"""

#######missing words
'''
unmatched = []
with open(dlogFullPath, 'r') as dlog:
    lines = dlog.readlines()
    for line in lines:
        if line.rstrip().isupper():
            unmatched.append(line.rstrip())

sed(unmatched, './manual/words.mlf', './manual/words.mlf')
'''
#######
########## ERROR:ERROR [+6550]  LoadHTKList: Label Name Expected {NO NUMBER SHOULD BE INCLUDED IN prompts FILE, CHANGE TO ENGLISH REPRESENTATION}
fhOut = open('./manual/mkphones0.led', 'w')
fhOut.write("EX\nIS sil sil\nDE sp\n")  # remember to include a blank line at the end of this script)
fhOut.close()
command_line = 'HLEd -A -D -T 1 -l \'*\' -d ./manual/dict -i ./manual/phones0.mlf ./manual/mkphones0.led ./manual/words.mlf '
cmd_list.append(command_line)
cmd(command_line)

fhOut = open('./manual/mkphones1.led', 'w')
fhOut.write("EX\nIS sil sil\n")  # remember to include a blank line at the end of this script)
fhOut.close()
command_line = 'HLEd -A -D -T 1 -l \'*\' -d ./manual/dict -i ./manual/phones1.mlf ./manual/mkphones1.led ./manual/words.mlf '
cmd_list.append(command_line)
cmd(command_line)


#############
#step 5
fhOut = open('./manual/wav_config', 'w')
fhOut.write("SOURCEFORMAT = WAV\n\
TARGETKIND = MFCC_0_D\n\
TARGETRATE = 100000.0\n\
SAVECOMPRESSED = T\n\
SAVEWITHCRC = T\n\
WINDOWSIZE = 250000.0\n\
USEHAMMING = T\n\
PREEMCOEF = 0.97\n\
NUMCHANS = 26\n\
CEPLIFTER = 22\n\
NUMCEPS = 12\n")  # remember to include a blank line at the end of this script)
fhOut.close()

codetrainContent = []
trainScpContent = []
noWavDir = []
for dirs in targetDataFolder_existing:
    fullDir = dataDir + check_dir(dirs) + wavSubDir  # './data/Aaron-20080318-lbk/wav/'
    newMfcDir = dataDir + check_dir(dirs) + mfcSubDir
    if os.path.isdir(fullDir):
        wavFiles = os.listdir(fullDir)
        for currWav in wavFiles:
            if os.path.splitext(currWav)[-1] == defaultWavFileExtension:
                currWavFullPath = fullDir + currWav
                currMfcFullPath = newMfcDir + os.path.splitext(currWav)[0] + '.mfc'
                trainScpContent.append(currMfcFullPath)
                if not file_exist(fullDir + os.path.splitext(currWav)[0] + '.mfc') or not os.path.isdir(check_dir(newMfcDir)) or len(os.listdir(check_dir(newMfcDir)))==0:
                    codetrainContent.append(currWavFullPath + ' ' + currMfcFullPath)
                    mkdir(check_dir(newMfcDir))
    else:
        noWavDir.append(dir)
        print str(dir) + 'still contains no wav file'
        if dir in targetDataFolder_existing:
            targetDataFolder_existing.remove(dir)



fhOut = open('./manual/codetrain.scp', 'w')
for i in codetrainContent:
    fhOut.write(i+'\n')
fhOut.close()

#LONG if codetrainContent is big
if len(codetrainContent) >0:
    command_line = 'HCopy -A -D -T 1 -C ./manual/wav_config -S ./manual/codetrain.scp '
    cmd_list.append(command_line)
    cmd(command_line)

#end of data pre-processing
######################################################################
#start of Monophones

cmd('cp ./lib/support_data/proto ./manual/')
cmd('cp ./lib/support_data/config ./manual/')
#Note: the target kind in you proto file (the "MFCC_0_D_N_Z" on the first line),
# needs to match the TARGETKIND in your config file.

fhOut = open('./manual/train.scp', 'w')

excludePattenInWavFiles = ['-old1', '-original']

for i in trainScpContent:
    passWav = 0
    for ex in excludePattenInWavFiles:
        if ex in i:
            passWav = 1
    if passWav == 0:
        fhOut.write(i+"\n")
fhOut.close()


mk_new_dir('./manual/hmm0')
command_line = 'HCompV -A -D -T 1 -C ./manual/config -f 0.01 -m -S ./manual/train.scp -M ./manual/hmm0 ./manual/proto'
cmd_list.append(command_line)
cmd(command_line)

#Flat Start Monophones
cmd('cp ./manual/monophones0 ./manual/hmm0/')
cmd('mv ./manual/hmm0/monophones0 ./manual/hmm0/hmmdefs')

#modify hmmdefs
'''
put the phone in double quotes;
add '~h ' before the phone (note the space after the '~h'); and
copy from line 5 onwards (i.e. starting from "<BEGINHMM>" to "<ENDHMM>") of the hmm0/proto file and paste it after each phone.
Leave one blank line at the end of your file.
'''

os.system('sed -e \'1,4d\' ./manual/hmm0/proto > ./manual/hmm0/proto_prune')

with open('./manual/hmm0/hmmdefs','r') as hmmdefs:
    defsLines = hmmdefs.readlines()
hmmdefs.close()
with open('./manual/hmm0/proto_prune','r') as proto:
    protoPart = proto.readlines()
proto.close()

fhOut = open('./manual/hmm0/hmmdefs_new', 'w')
for defsLine in defsLines:
    newLine = '~h '+ '\"' + defsLine.rstrip() + '\"\n'
    fhOut.write(newLine)
    for j in protoPart:
        fhOut.write(j)
fhOut.write('\n')  # Leave one blank line at the end of your file.
fhOut.close()
cmd('mv ./manual/hmm0/hmmdefs_new ./manual/hmm0/hmmdefs')

#Create macros File
os.system('head -3 ./manual/hmm0/proto > ./manual/hmm0/proto_head')
os.system('cat ./manual/hmm0/proto_head ./manual/hmm0/vFloors > ./manual/hmm0/macros')

#Re-estimate Monophones
for i in range(15):
    j = i+1
    mkdir('./manual/hmm'+str(j))

command_line = 'HERest -A -D -T 1 -C ./manual/config -I ./manual/phones0.mlf -t 250.0 150.0 1000.0 -S ./manual/train.scp -H ./manual/hmm0/macros -H ./manual/hmm0/hmmdefs -M ./manual/hmm1 ./manual/monophones0'
cmd_list.append(command_line)
cmd(command_line)

command_line = 'HERest -A -D -T 1 -C ./manual/config -I ./manual/phones0.mlf -t 250.0 150.0 1000.0 -S ./manual/train.scp -H ./manual/hmm1/macros -H ./manual/hmm1/hmmdefs -M ./manual/hmm2 ./manual/monophones0'
cmd_list.append(command_line)
cmd(command_line)

command_line = 'HERest -A -D -T 1 -C ./manual/config -I ./manual/phones0.mlf -t 250.0 150.0 1000.0 -S ./manual/train.scp -H ./manual/hmm2/macros -H ./manual/hmm2/hmmdefs -M ./manual/hmm3 ./manual/monophones0'
cmd_list.append(command_line)
cmd(command_line)

#step 7
#####################################################################################################################
existFiles = os.listdir('./manual/hmm4/')
if len(existFiles) == 0:
    os.system('cp ./manual/hmm3/* ./manual/hmm4/')

    ############################
    print 'need manual correction for ./manual/hmm4/hmmdefs here'
    ############################
else:
    print 'file exists in ./manual/hmm4/hmmdefs, whether continue?'
    ifContinue()


fhOut = open('./manual/sil.hed', 'w')
fhOut.write('AT 2 4 0.2 {sil.transP}\n\
AT 4 2 0.2 {sil.transP}\n\
AT 1 3 0.3 {sp.transP}\n\
TI silst {sil.state[3],sp.state[2]}\n')
fhOut.close()

command_line = 'HHEd -A -D -T 1 -H ./manual/hmm4/macros -H ./manual/hmm4/hmmdefs -M ./manual/hmm5/ ./manual/sil.hed ./manual/monophones1'
cmd_list.append(command_line)
cmd(command_line)


command_line = 'HERest -A -D -T 1 -C ./manual/config  -I ./manual/phones1.mlf -t 250.0 150.0 3000.0 -S ./manual/train.scp -H ./manual/hmm5/macros -H  ./manual/hmm5/hmmdefs -M ./manual/hmm6 ./manual/monophones1'
cmd_list.append(command_line)
cmd(command_line)

command_line = 'HERest -A -D -T 1 -C ./manual/config  -I ./manual/phones1.mlf -t 250.0 150.0 3000.0 -S ./manual/train.scp -H ./manual/hmm6/macros -H  ./manual/hmm6/hmmdefs -M ./manual/hmm7 ./manual/monophones1'
cmd_list.append(command_line)
cmd(command_line)

###step 8

command_line = 'HVite -A -D -T 1 -l \'*\' -o SWT -b SENT-END -C ./manual/config -H ./manual/hmm7/macros -H ./manual/hmm7/hmmdefs -i ./manual/aligned.mlf -m -t 250.0 150.0 1000.0 -y lab -a -I ./manual/words.mlf -S ./manual/train.scp ./manual/dict ./manual/monophones1'

cmd_list.append(command_line)
cmd(command_line)

command_line = 'HERest -A -D -T 1 -C ./manual/config -I ./manual/aligned.mlf -t 250.0 150.0 3000.0 -S ./manual/train.scp -H ./manual/hmm7/macros -H ./manual/hmm7/hmmdefs -M ./manual/hmm8 ./manual/monophones1'
cmd_list.append(command_line)
cmd(command_line)

command_line = 'HERest -A -D -T 1 -C ./manual/config -I ./manual/aligned.mlf -t 250.0 150.0 3000.0 -S ./manual/train.scp -H ./manual/hmm8/macros -H ./manual/hmm8/hmmdefs -M ./manual/hmm9 ./manual/monophones1'
cmd_list.append(command_line)
cmd(command_line)

#step 9
fhOut = open('./manual/mktri.led', 'w')
fhOut.write('WB sp\nWB sil\nTC\n')
fhOut.close()

#This creates 2 files: wintri.mlf triphones1
command_line = 'HLEd -A -D -T 1 -n ./manual/triphones1 -l \'*\' -i ./manual/wintri.mlf ./manual/mktri.led ./manual/aligned.mlf'
cmd_list.append(command_line)
cmd(command_line)

# create the mktri.hed file
command_line = 'perl ./lib/HTK_scripts/maketrihed ./manual/monophones1 ./manual/triphones1'
cmd_list.append(command_line)
cmd(command_line)
os.system('mv ./mktri.hed ./manual/')

#
command_line = 'HHEd -A -D -T 1 -H ./manual/hmm9/macros -H ./manual/hmm9/hmmdefs -M ./manual/hmm10 ./manual/mktri.hed ./manual/monophones1'
cmd_list.append(command_line)
cmd(command_line)

command_line = 'HERest  -A -D -T 1 -C ./manual/config -I ./manual/wintri.mlf -t 250.0 150.0 3000.0 -S ./manual/train.scp -H ./manual/hmm10/macros -H ./manual/hmm10/hmmdefs -M ./manual/hmm11 ./manual/triphones1 '
cmd_list.append(command_line)
cmd(command_line)

command_line = 'HERest  -A -D -T 1 -C ./manual/config -I ./manual/wintri.mlf -t 250.0 150.0 3000.0 -s ./manual/stats -S ./manual/train.scp -H ./manual/hmm11/macros -H ./manual/hmm11/hmmdefs -M ./manual/hmm12 ./manual/triphones1'
cmd_list.append(command_line)
cmd(command_line)

#step 10
command_line = 'HDMan -A -D -T 1 -b sp -n ./manual/fulllist -g ./manual/global.ded -l ./manual/flog ./manual/dict-tri ./lexicon/VoxForgeDict'
cmd_list.append(command_line)
cmd(command_line)

vi('./manual/fulllist1')
os.system('cat ./manual/fulllist  ./manual/triphones1 > ./manual/fulllist1')
os.system('perl ./lib/HTK_scripts/fixfulllist_pl ./manual/fulllist1 ./manual/fulllist')


########tree.hed modification
os.system('cp ./lib/support_data/tree.hed ./manual/')

command_line = 'perl ./lib/HTK_scripts/mkclscript.prl TB 350 ./manual/monophones0 >> ./manual/tree.hed'
cmd_list.append(command_line)
os.system(command_line)

###coutious append file
fhOut = open('./manual/tree.hed', 'a')
fhOut.write('\nTR 1\n\n\
AU "fulllist"\n\
CO "tiedlist"\n\n\
ST "trees"\n')
fhOut.close()
########

#ERROR [+2662]  FindProtoModel: no proto for sp in hSet
# fix by delete the sp line in ./manual/fulllist file and run through ./manual dir
"""
os.system('./manual/HHEd -A -D -T 1 -H ./hmm12/macros -H ./hmm12/hmmdefs -M ./hmm13 ./tree.hed ./triphones1')
command_line = 'HHEd -A -D -T 1 -H ./manual/hmm12/macros -H ./manual/hmm12/hmmdefs -M ./manual/hmm13 ./manual/tree.hed ./manual/triphones1 '
cmd_list.append(command_line)
cmd(command_line)
"""
sed('sp', './manual/fulllist', './manual/fulllist')
command_line = 'cd ./manual && HHEd -A -D -T 1 -H ./hmm12/macros -H ./hmm12/hmmdefs -M ./hmm13 ./tree.hed ./triphones1'
cmd_list.append(command_line)
os.system(command_line)

#create hmm14
command_line = 'cd ./manual/ && HERest -A -D -T 1 -T 1 -C config -I wintri.mlf -s stats -t 250.0 150.0 3000.0 -S train.scp -H hmm13/macros -H hmm13/hmmdefs -M hmm14 tiedlist'
cmd_list.append(command_line)
os.system(command_line)
os.system('say "hmm14 has finished"')

#create hmm15
command_line = 'cd ./manual/ && HERest -A -D -T 1 -T 1 -C config -I wintri.mlf -s stats -t 250.0 150.0 3000.0 -S train.scp -H hmm14/macros -H hmm14/hmmdefs -M hmm15 tiedlist'
cmd_list.append(command_line)
os.system(command_line)
os.system('say "your hmm15 has finished"')
#####
# The hmmdefs file in the hmm15 folder,
# along with the tiedlist file,
# can now be used with Julian to recognize your speech!
#####

###############################################################################################
#GMM splits
fhOut = open('./manual/split.hed','w')
fhOut.write('MU 2 {*.state[2-4].mix}\n')
fhOut.close()

for i in range(16,21):
    mkdir('./manual/hmm'+str(i))

#os.system('cd ./manual/ && HLEd -A -D -T 1 -n triphones1 -l \'*\' -i wintri.mlf mktri.led aligned.mlf')

command_line = 'cd ./manual/ && HHEd -A -D -T 1 -H hmm15/macros -H hmm15/hmmdefs -M hmm16 split.hed tiedlist'
cmd_list.append(command_line)
os.system(command_line)

command_line = 'cd ./manual/ && HERest  -A -D -T 1 -C config -I wintri.mlf -t 250.0 150.0 3000.0 -S train.scp -H hmm16/macros -H hmm16/hmmdefs -M hmm17 tiedlist'
cmd_list.append(command_line)
os.system(command_line)
os.system('say "your hmm17 has finished"')

command_line = 'cd ./manual/ && HERest  -A -D -T 1 -C config -I wintri.mlf -t 250.0 150.0 3000.0 -s stats -S train.scp -H hmm17/macros -H hmm17/hmmdefs -M hmm18 tiedlist'
cmd_list.append(command_line)
os.system(command_line)
os.system('say "hmm18 has finished"')

#ERROR [+2663]  ChkTreeObject: TB only valid for 1 mix diagonal covar models
#solve1: http://www.voxforge.org/home/dev/acousticmodels/linux/create/htkjulius/tutorial/triphones/step-10/comments/getting-error-in-tree-clustering
#ERROR [+7036]  NewMacro: macro or model name ST_ax_2_1 already exists
# solve should use split.hed instead of tree.hed
#os.system('sed -e \'s/^TB/TC/g\' ./manual/tree.hed > tmp')
#os.system('mv ./tmp ./manual/tree2.hed')

# ERROR [+5010]  InitSource: Cannot open source file t+ow
command_line = 'cd ./manual/ && HHEd -A -D -T 1 -H hmm18/macros -H hmm18/hmmdefs -M hmm19 split.hed tiedlist'
cmd_list.append(command_line)
os.system(command_line)
os.system('say "hmm19 has finished"')

command_line = 'cd ./manual/ && HERest -A -D -T 1 -T 1 -C config -I wintri.mlf -s stats -t 250.0 150.0 3000.0 -S train.scp -H hmm19/macros -H hmm19/hmmdefs -M hmm20 tiedlist'
cmd_list.append(command_line)
os.system(command_line)
os.system('say "hmm20 has finished"')

command_line = 'cd ./manual/ && HERest -A -D -T 1 -T 1 -C config -I wintri.mlf -s stats -t 250.0 150.0 3000.0 -S train.scp -H hmm20/macros -H hmm20/hmmdefs -M hmm21 tiedlist'
cmd_list.append(command_line)
os.system(command_line)
os.system('say "hmm21 has finished"')
os.system('say "Splitting Hidden Markov Model task has finished"')

###############################################################################################
#Running Julian Live
#cp julian config
testDataDir = '/Volumes/1/E6998_testing'
motif = 'prompts'
integratedPROMPTSFilePath_testing = './manual/prompts_testing'
wlistFullPath_testing = './manual/wlist_testing'
dictPath = './manual/dict_testing'
dictTriPath = './manual/dict-tri'
grammarFilePath = './manual/fixed.grammar'
vocaFilePath = './manual/fixed.voca'
configFilePath = './manual/julian.jconf'
wavsFilePath = './manual/wavPath_testing'
mfcsFilePath = './manual/mfcPath_testing'
scpFilePath = './manual/testing.scp'
validationPath = './manual/validation_testing'


####
####* optional
#change files in CUE6998_2014_09-20140929 folder to the same name as in prompts
if 0:
    for i in excludeNamesStartWith(os.listdir('/Volumes/1/E6998_testing/CUE6998_2014_09-20140929')):
        if re.search('vf5',i):
            j = i.replace('5','9')
            os.system('mv '+check_dir('/Volumes/1/E6998_testing/CUE6998_2014_09-20140929') + i + ' ' +check_dir('/Volumes/1/E6998_testing/CUE6998_2014_09-20140929')+ j)



targetDirs = getDirNamesInCurrDir(testDataDir)
targetPrompts = [check_dir(x)+searchFileWithSimilarNameMotif_returnBest(x, motif) for x in targetDirs]
targetWavs = [check_dir(x)+y for x in targetDirs for y in excludeNamesStartWith(os.listdir(x)) ]
targetWavs = [x for x in targetWavs if x.endswith('.wav')]
targetMfcs = [x.replace('wav','mfc') for x in targetWavs]
getPrompts(integratedPROMPTSFilePath_testing,targetPrompts,testDataDir)
removeMHatInFile(integratedPROMPTSFilePath_testing)  #no ^M symbol allowed

getWlist(wlistFullPath_testing, integratedPROMPTSFilePath_testing)
runHDManGetMonophone(wlistFullPath_testing,dictPath)

#generate wav list file
fhIn = open(wavsFilePath,'w')
fhIn.write('\n'.join(targetWavs))
fhIn.close()
#generate mfc list file
fhIn = open(mfcsFilePath,'w')
fhIn.write('\n'.join(targetMfcs))
fhIn.close()
#generate scp file for HCopy
fhIn = open(scpFilePath,'w')
for i in range(len(targetWavs)):
    fhIn.write(targetWavs[i] + ' ' + targetMfcs[i]+ '\n')
fhIn.close()

command_line = 'HCopy -A -D -T 1 -C ./manual/wav_config -S '+scpFilePath
cmd_list.append(command_line)
cmd(command_line)

########analysis of prompts file
#max sentence length
count = getWordCountEachLine(integratedPROMPTSFilePath_testing)
sentenceLength = [x-1 for x in count]
print "the max sentence length is: "
print max(sentenceLength)
#voca Table (vocab words)
#rerun point 614
voca2D = read_file_as_2D_dict(integratedPROMPTSFilePath_testing)
#dicrt table from HDMan (with phone)
dict2D = read_file_as_2D_dict(dictTriPath,'\s\s+')  # dictPath!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

######writing .grammar file
if not file_exist(grammarFilePath):
    vi(grammarFilePath)
fhIn = open(grammarFilePath,'w')
firstLine = 'S: NS_B '
otherLines = ''
vocaGroup = []
for i in range(1, max(sentenceLength)+1):
    firstLine += numToWords(i).upper() + "_LOOP "
    otherLines += numToWords(i).upper() + "_LOOP: "+numToWords(i).upper()+'_WORD\n'
    vocaGroup.append(numToWords(i).upper()+'_WORD')
firstLine += "NS_E\n"
allContent = firstLine + otherLines
fhIn.write(allContent)
fhIn.close()
######writing voca file
vi(vocaFilePath+'_tmp')
fhIn = open(vocaFilePath+'_tmp','w')
otherLines = ''
for i in range(len(vocaGroup)):
    occurred = []
    flag = "% " + vocaGroup[i]
    otherLines += flag +'\n'
    for line in range(len(voca2D)):
        if i+1 in voca2D[line].keys():  # first column is the address, negelect it
            currWord = voca2D[line][i+1]  # first column is the address, negelect it
            if not currWord in occurred:
                occurred.append(voca2D[line][i+1])
                otherLines += currWord + '\n'
    otherLines += '\n'
fhIn.write(otherLines)
fhIn.close()
######
#NORMALIZE vocab to map with dict
command_lines = ['cp ' + vocaFilePath+'_tmp' + ' ' + vocaFilePath+'_tmp' + '_ori',
        'sed \'/[\\"\,\:\;\&\.\\\/\!\s*]/d\' '+ vocaFilePath+'_tmp' + ' > ./tmp1',
        'tr \'[:lower:]\' \'[:upper:]\' < ./tmp1 > ./tmp2', # TO UPPER CASE
        'sed \'/^-/d\' ./tmp2 > tmp1',
        'sed "/^\'/d" tmp1 > tmp2',
        'sed -e \'s/[0-9]*//g\' tmp2 > tmp1', # DELETE NUMBERS
        'sed \'/^$/d\' tmp1 > '+vocaFilePath+'_tmp',  # DELETE EMPTY LINE
        #'awk \'!x[$0]++\' tmp2 > ' + vocaFilePath+'_tmp', #delete duplicate line
        'rm tmp1 tmp2']
for command_line in command_lines:
    os.system(command_line)

#mapping dict_testing to fixed.voca
fhIn = open(vocaFilePath+'_tmp', 'r')
allVocab = fhIn.readlines()
fhIn.close()
totalNotFind = []
for i in range(len(allVocab)):
    vocab = allVocab[i].rstrip()
    if not vocab.startswith('%'):
        find = 0
        for j in range(len(dict2D)):
            if dict2D[j][0].upper() == vocab.upper():
                find = 1
                try:
                    allVocab[i] = vocab + '\t' + dict2D[j][1] + '\n'  # dict2D[j][1] for dictTriPath [2] for dictPath
                    break
                except KeyError:
                    print 'The following lines are not correctly aligned, please make sure that phones have separate keys'
                    print "modify the corresponding line in dict file and add an extra space (make there two) between the second andthird column"
                    print dict2D[j]
                    print 'rerun from <#rerun point 614>'
                    ifContinue()
        if find==0:
            totalNotFind.append(vocab)
os.system('say "mapping phones finished"')

fhIn = open(vocaFilePath,'w')
fhIn.write('% NS_B\n<s>\tsil\n\n% NS_E\n</s>\tsil\n')
fhIn.write(''.join(allVocab))
fhIn.close()

# delete sp in the end of each line
sed_replace('sp$','',vocaFilePath,vocaFilePath)
#sed -e s/'SP'$/''/g fixed.voca

###error running mkdfa.pl
#Warning: dfa_minimize not found in the same place as mkdfa.pl
#solution: make sure mkfa/dfa_minimize is in the same folder with mkdfa.pl (if .dSYM is listed as extension, see next line of comment)
#solution: change mkfa->mkfa.dSYM [in line 15] and dfa_minimize -> dfa_minimize.dSYM [in line 18] in mkdfa.pl file
command_line  = 'cd ./manual/ && perl ../lib/HTK_scripts/mkdfa.pl fixed'
os.system(command_line)

if not file_exist(configFilePath):
    os.system('cp ./lib/support_data/julian.jconf ./manual/')
    print 'need to manually change the parameters'
    ifContinue()

#test grammar
command_line = 'cd ./manual/ && generate.dSYM fixed'
os.system(command_line)
##manually change any line that error occurs in fixed.dict
#Error: voca_load_htkdict: line 920: corrupted data:


command_line = 'cd ./manual/ && julius.dSYM -input mic -C ./julian.jconf'
os.system(command_line)

##error:ERROR: Error while setup work area for recognition
#comment the following lines
#-iwsp                  # append a skippable sp model at all word ends
#-iwsppenalty -70.0     # transition penalty for the appenede sp models

#run with result (list of files input)
command_line = 'julius.dSYM -filelist ./mfcPath_testing -C ./julian.jconf -outfile'
os.system(command_line)

#########################################################
#Evaluation, sentence alignment
#get the sentence from prompts into 2D dict
promptSentence2D = {}
for i in targetPrompts:
    if file_exist(i):
        dirName = os.path.dirname(i).split('/')[-1]
        with open(i,'r') as fhIn:
            content = fhIn.readlines()
            tmp = {}
            for line in content:
                if line:
                    ele = line.rstrip().split(' ')
                    first = ele.pop(0)
                    if first != '':
                        tmp[first] = ' '.join(ele)
            promptSentence2D[dirName] = tmp


#how many search are failed
outFilePath = open(mfcsFilePath,'r').readlines()
outFilePath = [x.replace('.mfc','.out').rstrip() for x in outFilePath]
failedNum = 0
totalNum = 0
predictedSentence2D = {}
preDir = ''#os.path.dirname(outFilePath[0]).split('/')[-1]
tmp = {}
for i in outFilePath:
    dirName = os.path.dirname(i).split('/')[-1]
    if preDir == '':
        preDir = dirName
    currTargetTrack = os.path.basename(i).split('.')[0]
    if file_exist(i):
        content = open(i, 'r').read()
        if dirName == preDir:
            if re.search('<search failed>', content):
                targetSentence = '<search failed>'
            else:
                targetSentence = re.search(re.escape('<s> ')+"(.*?)"+re.escape(' </s>'),content).group(1)
            tmp[currTargetTrack] = targetSentence
        if dirName != preDir or i == outFilePath[-1]:
            predictedSentence2D[preDir] = tmp
            preDir = dirName
            tmp = {}
            if re.search('<search failed>', content):
                targetSentence = '<search failed>'
            else:
                targetSentence = re.search(re.escape('<s> ')+"(.*?)"+re.escape(' </s>'),content).group(1)
            tmp[currTargetTrack] = targetSentence
        totalNum += 1
        if re.search('<search failed>', content):
            failedNum += 1
print 'out of ' + str(totalNum) + ' of processed files, '+ str(failedNum) + ' are failed'


#global alignment for two sentences
#in this case, it aligns the prompts sentence and the predict sentence

# Create sequences to be aligned.
fhIn = open(validationPath,'w')
totalInsertion = 0
totalDeletion = 0
totalReplacement = 0
totalMatch = 0
totalLength = 0
for dir in predictedSentence2D.keys():
    for track in predictedSentence2D[dir].keys():
        prom = promptSentence2D[dir][track].lower()
        pred = predictedSentence2D[dir][track].lower()
        if not predictedSentence2D[dir][track] == '<search failed>':
            matched = stringMatching(prom.split(), pred.split())

            #calculate statistics
            insert = [x for x in matched[2] if x == 'I']
            delete = [x for x in matched[2] if x == 'D']
            replace = [x for x in matched[2] if x == 'R']
            match = [x for x in matched[2] if x == 'M']
            totalInsertion += len(insert)
            totalDeletion += len(delete)
            totalReplacement += len(replace)
            totalLength += len(prom.split())
            totalMatch += len(match)
            #calculate statistics
            line1 = 'PROMPT: ' + dir + '\t' + track + '\t' + prom #+ '\t' + ' '.join(matched[0]) + '\t' + ' '.join(matched[2])
            line2 = 'RESULT: ' + dir + '\t' + track + '\t' + pred #+ '\t' + ' '.join(matched[1])
            fhIn.write(line1 + '\n')
            fhIn.write(line2 + '\n')
fhIn.close()
totalError = totalReplacement + totalInsertion + totalDeletion
print 'Total Match: '+str(totalMatch)+'\t'+str(float(totalMatch)/totalLength*100)+'%'
print 'Total Insertion: '+str(totalInsertion)+'\t'+str(float(totalInsertion)/totalLength*100)+'%'
print 'Total Deletion: '+str(totalDeletion)+'\t'+str(float(totalDeletion)/totalLength*100)+'%'
print 'Total Replacement: '+str(totalReplacement)+'\t'+str(float(totalReplacement)/totalLength*100)+'%'
print 'Total No. Errors: '+str(totalError)+'\t'+str(float(totalError)/totalLength*100)+'%'

