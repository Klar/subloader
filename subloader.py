import struct, os

#arguments
from sys import argv

from xmlrpclib import ServerProxy

#for getting the file
import urllib

#unzip file
import zipfile

#folder with movies in it - passed as argument
rootdir = argv[1]

#add more...
video_formats = ['mkv','mp4','avi']

#generates the hash of the file - got it from opensubtitles - thanks
def hashFile(name): 
      try: 
                 
                longlongformat = '<q'  # little-endian long long
                bytesize = struct.calcsize(longlongformat) 
                    
                f = open(name, "rb") 
                    
                filesize = os.path.getsize(name) 
                hash = filesize 
                    
                if filesize < 65536 * 2: 
                       return "SizeError" 
                 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
                f.seek(max(0,filesize-65536),0) 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
                f.close() 
                returnedhash =  "%016x" % hash 
                return returnedhash 
    
      except(IOError): 
                return "IOError"

def getFileNames(rootdir):
    #loop trough filenames
    filepath = {}
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            filepath[file] = subdir
    return filepath


#api connection
server = ServerProxy('http://api.opensubtitles.org/xml-rpc')

#Sub Language
SubLanguageID = 'eng'

# Connection to opensubtitles.org server
session = server.LogIn('', '', 'en', 'subloader')

#get the filenames with path
FileNameList = getFileNames(rootdir)

for filename, subdir in FileNameList.iteritems():
    if filename.endswith(tuple(video_formats)):
        # file has a vide_formats ending  
        
        FullPath = subdir + filename

        print FullPath

        # get video info
        videoHash = hashFile(FullPath)
        videoSize = os.path.getsize(FullPath)

        #creates and "resets" the list
        searchList = []
        searchList.append({'sublanguageid':SubLanguageID, 'moviehash':videoHash, 'moviebytesize':str(videoSize)})
        searchList.append({'sublanguageid':SubLanguageID, 'query':filename})

        subtitlesList = server.SearchSubtitles(session['token'], searchList)

        #print subtitlesList['data'][0]['MatchedBy']  # --> moviehash

        #FileUrl = subtitlesList['data'][0]['SubDownloadLink'] --> .gz
        FileUrl = subtitlesList['data'][0]['ZipDownloadLink'] # --> zip

        #.srt name
        SubFileName = subtitlesList['data'][0]['SubFileName']
        SubFileNameZip = SubFileName + '.zip'

        #download & unzip it
        myZipFile = urllib.urlretrieve(FileUrl,subdir + SubFileNameZip)
        fh = open(subdir + SubFileNameZip, 'rb')
        zipfile.ZipFile(fh).extract(SubFileName,subdir)
        fh.close()

        #rename as file + .srt
        os.rename(subdir + SubFileName,FullPath +".srt")

        #remove .zip file
        os.remove(subdir + SubFileNameZip)
