"""
tools.py : tool functions

* Copyright : 2019 Duranc Oy
* Authors   : Sampsa Riikonen
* Date      : 2018
* Version   : 0.1

This file is part of the duranc_gateway library

All Rights Reserved.  Unauthorized copying of this file, via any medium is strictly prohibited.  Proprietary and confidential.

This file has been derived from the MIT licensed skeleton module (copyright Sampsa Riikonen).  See: https://github.com/elsampsa/skeleton
"""

from asyncio.log import logger
import copy
import pprint
import shutil
import types
import sys
import os
import inspect
import asyncio
import logging
import logging.config
import yaml
import re
import subprocess
from lxml import etree
from io import StringIO, BytesIO
# import StringIO
import json
from datetime import datetime
import time
import logging.config

import inspect
import os.path

home = os.path.expanduser("~")

from duranc.gateway import numerical

is_py3 = (sys.version_info >= (3,0))
link_re = re.compile("-(\d\.\d\.\d)\.tar.gz$")

loglevel = logging.DEBUG # DEBUGGING : raise the global loglevel
# loglevel = logging.INFO

rec_metadataResource = os.path.join(home,".duranc","gateway","rec_metadata")
rec_upload_failed_metadataResource = os.path.join(home,".duranc","gateway","upload_failed")
rec_Resource = os.path.join(home,".duranc","gateway","rec")
# rec_metadataResource.ensureDirectory()


loggers = {}

# staging password: Val5asiaKas!"
messenger_test_data = {
    # from config file
    "ID" : "5cd00610d5bcb77a3e6ae854",  # THIS IS USED
    "TOKEN" : "1f0939231232b1ae7c60935ae08e14f6c1f5fb5524c9ab284d75faf75c62690600cd9b9981bd2459add041d9aa031a8669349ac3ea6bdb43e755e2c9a352a95cce0dfc24f683b01b1a184c02b210b6f6af9fa7ffd4c39b57500546e25b8bb8afbfd61868718ca7e79039734e34e310c2bb0f9765464bb350ab41740f784102e632ef52450c4829f7f55ba0843968aa6f5ca3a33d4fec570f32eb5323bb1142173856734c72d0aa4a3d99889436162c1867372e008f9dadf4335841d6f997d5c58d8c6ff7dd9ab5f426f62c0384278ca0b9992cc40742cbf3321babb70d",
    "NAME" : "Sampsa's Linux Box - pusher",
    # from PORTAL
    "URL" : "https://stgmessenger.duranc.com", # THIS IS USED
    '_ID': '5ad9fcb7652a984af5ae2772', 
    'MESSENGER_NAME': 'Messenger'
}


def getHtmlDirLinks(txt):
    """Give a html directory listing, get a link list
    """
    links = []
    parser = etree.HTMLParser()
    root = etree.parse(StringIO(txt), parser).getroot()
    # print(root)
    for child in root:
        #print(child.tag)
        for cc in child:
            #print(cc.tag, cc.attrib)
            #continue
            if cc.tag == "a":
                #print(">>>>", cc.attrib)
                link = cc.attrib["href"]
                #print(">>",link)
                links.append(link)
    return links


def versionFromLink(txt):
    try:
        m = next(link_re.finditer(txt))
    except StopIteration:
        return None
    version_string = txt[m.start(1):m.end(1)]
    nums = version_string.split(".")
    return int(nums[0]), int(nums[1]), int(nums[2])


def runCommand(st, prefix = ""):
  st = prefix + st
  print("> runCommand:", st)
  cmd = os.system(st)
  return os.WEXITSTATUS(cmd)


def runDurancGateway(st):
    comm = os.path.join(os.path.expanduser("~"), ".local", "bin", "duranc-gateway")
    return runCommand(comm + " " + st)


def getDurancGateway():
    return os.path.join(os.path.expanduser("~"), ".local", "bin", "duranc-gateway")


def getSystemCtlStatus(service_name): # returns i, txt
    isDocker = checkIfDocker()
    if isDocker:
        st = "ps -ef  | grep %s | grep -v grep | grep -v /bin/bash | awk '{ print $2 }'" %(service_name)
        cmd = os.system(st)
    else:
        st = "systemctl --user --no-pager status %s.service" % (service_name) # no-pager makes it non-interactive
        cmd = os.system(st)
    # print("cmd",cmd)
    # if cmd == 256: ## No systemctl running
    #   st = "ps -ef  | grep %s | grep -v grep | grep -v /bin/bash | awk '{ print $2 }'" %(service_name)
    #   cmd = os.system(st)
    i = os.WEXITSTATUS(cmd)
    dic = { # https://stackoverflow.com/questions/56719780/what-return-code-does-systemctl-status-return-for-an-error-in-systemctl-status
        0 : "program is running or service is OK",
        1 : "program is dead and /var/run pid file exists",
        2 : "program is dead and /var/lock lock file exists",
        3 : "program is not running",
        4 : "program or service status is unknown"
        }
    try:
        txt = dic[i]
    except KeyError:
        txt = "unkown error"
    return i, txt

def uninstallGateway(logger:logging.Logger):
  if checkIfDocker():
    logger.critical("uninstallGateway : Docker check True")
    runCommand('touch /root/.duranc/gateway/uninstall.txt')
    logger.critical("uninstallGateway : written file /root/.duranc/gateway/uninstall.txt")
    runCommand('supervisorctl stop all')
  else:
    logger.critical("uninstallGateway : Docker check False")
    logger.critical("uninstallGateway : uninstalling services")
    runCommand("duranc-gateway uninstall")
    logger.critical("uninstallGateway : pm2 delete gateway-streamer")
    runCommand('pm2 delete gateway-streamer')
    logger.critical("uninstallGateway : pip3 remove duranc-gateway(deleting python code from ~/.local)")
    runCommand("pip3 uninstall duranc-gateway -y")
    logger.critical("uninstallGateway : deleting ~/.localstr and ~/.duranc/gateway)")
    runCommand('rm ~/.localstr')
    runCommand('rm -r ~/.duranc/gateway')
    logger.critical("uninstallGateway : killing all duranc-gateway processes")
    runCommand("pkill -f duranc-gateway")
    logger.critical("uninstallGateway : done.")
  time.sleep(10)
  exit(1)

def countFFmpegProcesses():
    p = subprocess.Popen("ps -A -f".split(), stdout = subprocess.PIPE)
    stdout, stderr = p.communicate()
    lines = stdout.decode("utf-8").split("\n")
    cc = 0
    for line in lines:
        if "ffmpeg" in line:
            cc += 1
    return cc


def getMemProcesses(nmax = -1):
    p = subprocess.Popen("ps aux --sort=-%mem".split(), stdout = subprocess.PIPE)
    stdout, stderr = p.communicate()
    lines = stdout.decode("utf-8").split("\n")
    if nmax < 0:
        i = len(lines)
    else:
        i = min(len(lines), nmax)
    return lines[:i]
    

def parse_http_response(resp: str):
    reg = re.compile("(^\S*):(.*)")
    fields = resp.split("\r\n")
    output = {}
    for field in fields[1:]: # ignore "GET / HTTP/1.1" and the like
        # print(">", field)
        try:
            lis = reg.findall(field)[0]
            # print(">>", lis)
            key = lis[0].strip()
            value = lis[1].strip()
        except IndexError:
            pass
        else:
            output[key] = value
    return fields[0], output




def configureLogging(service):
    # this was useful: https://gist.github.com/glenfant/4358668
    from duranc.gateway import constant
    from duranc.gateway import userspace
    
    logging_resource = userspace.LoggingResource()
    logging_resource.ensureDirectory()
   




    if not logging_resource.hasFile("default.yml"):
        print("WARNING: initializing logger configuration")
        f = open(logging_resource.getFilePath("default.yml"),"w")
        f.write(constant.LOGGING_CONF_YAML_DEFAULT)
        f.close()
        
    f = open(logging_resource.getFilePath("default.yml"),"r")
    logging_str = f.read()
    f.close()
        
    # import pprint
    # logging_config = yaml.load(constant.LOGGING_CONF_YAML)
    # logging_config = yaml.load(constant.LOGGING_CONF_YAML_DEFAULT)
    try:
       
        logging_config = yaml.load(logging_str)
        logging_config['logging']['root']['handlers'].append('file')
        pprint.pprint(logging_config)
        log_folder = os.path.join(home, ".duranc", "gateway","logging","logs")
        os.makedirs(log_folder, exist_ok=True)

        

        stdout_file_handler_key = f'{service}_stdout_file_handler'
        stdout_file_handler = {
              'class':'logging.FileHandler',
              'filename':os.path.join(log_folder,f'{service}.stdout'),           
              'level':'DEBUG',
              'formatter': 'detailedFormatter'
        }
        logging_config['logging']['handlers'][stdout_file_handler_key] = stdout_file_handler
     

        for logger in logging_config['logging']['loggers'].values():
            logger['handlers'].append(stdout_file_handler_key)
          
        logging_config['logging']['handlers']['file'] = stdout_file_handler

  

        logging_config['logging']['formatters']['detailedFormatter'] = {
        'format': '%(asctime)s - %(levelname)s -%(name)s- %(filename)s:%(lineno)d - %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S'
        }
        pprint.pprint(logging_config)

        for key  in logging_config['logging']['loggers'].keys():
          print (key)           
          logging_config['logging']['loggers'][key]['handlers'].append('file')
          pprint.pprint(logging_config)

      
        logging_config['logging']['loggers'][key] = logging_config             
        logging.config.dictConfig(logging_config['logging'])
        pprint.pprint(logging_config)

    except Exception as e:
        print("FATAL : your logging configuration is broken")
        print("FATAL : failed with %s" % (str(e)))
        print("FATAL : remove it and start the program again")
        #raise SystemExit(2)

    

def getLogger(name):
    global loggers
    logger = loggers.get(name)
    if logger: return logger

    # https://docs.python.org/2/howto/logging.html
    # log levels here : https://docs.python.org/2/howto/logging.html#when-to-use-logging
    # in the future, migrate this to a logger config file
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    """ # use external config
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    """
    
    logger = logging.getLogger(name)
    loggers[name] = logger 
    
    # logger.setLevel(level) # use external config
    # logger.addHandler(ch) # use external config
    
    return logger
    
    
def setLogger(name, level):
    """Give either logger name or the logger itself
    """
    
    if (isinstance(name,str)):
        logger = getLogger(name)
    else:
        logger = name 
    
    if not logger.hasHandlers():
        formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        
        logger.setLevel(level)
        logger.addHandler(ch)
        
        
def reschedule(cofunc):
    """A simple shorthand function
    """
    asyncio.get_event_loop().create_task(cofunc)


def configToDic(fname):
    f=open(fname,"r")
    dic={}
    for line in f:
        try:
            ls = line.strip().split("=")
            key = ls[0].strip().lower()
            value = ls[1].strip()
        except Exception as e:
            print("tools: configToDic failed with '%s'" % (str(e)))
            print("tools: your line is '%s'" % line.strip())
            print("tools: key/value list is %s" % str(ls))
            # raise(e)
            continue
        try: # if value can be converted to int, do it
            value = int(value)
        except: # no int .. how about float?
            try:
                value = float(value)
            except:
                pass
        
        if (value in ["true","True"]):
            value=True
        if (value in ["false","False"]):
            value=False
        
        dic[key]=value
    f.close()

    return dic


def getModulePath():
  lis=inspect.getabsfile(inspect.currentframe()).split("/")
  st="/"
  for l in lis[:-1]:
    st=os.path.join(st,l)
  return st
  

def getTestDataPath():
  return os.path.join(getModulePath(),"test_data")


def getTestDataFile(fname):
  return os.path.join(getTestDataPath(),fname)


def getDataPath():
  return os.path.join(getModulePath(),"data")


def getDataFile(fname):
  """Return complete path to datafile fname.  Data files are in the directory duranc_gateway/duranc_gateway/data
  """
  return os.path.join(getDataPath(),fname)


def getAutoConfigPath():
  return os.path.join(getModulePath(),"auto_config")


def getAutoConfigFile(fname):
  """Return complete path to datafile fname.  Data files are in the directory duranc_gateway/duranc_gateway/data
  """
  return os.path.join(getAutoConfigPath(),fname)



def typeCheck(obj, typ):
  """Check type of obj, for example: typeCheck(x,int)
  """
  if (obj.__class__!=typ):
    raise(AttributeError("Object should be of type "+typ.__name__))
  
  
def dictionaryCheck(definitions, dic):
  """ Checks that dictionary has certain values, according to definitions
  
  :param definitions: Dictionary defining the parameters and their types (dic should have at least these params)
  :param dic:         Dictionary to be checked
  
  An example definitions dictionary:
  
  |{
  |"age"     : int,         # must have attribute age that is an integer
  |"name"    : str,         # must have attribute name that is a string            
  | }
  """
  
  for key in definitions:
    # print("dictionaryCheck: key=",key)
    required_type=definitions[key]
    try:
      attr=dic[key]
    except KeyError:
      raise(AttributeError("Dictionary missing key "+key))
    # print("dictionaryCheck:","got: ",attr,"of type",attr.__class__,"should be",required_type)
    if (attr.__class__ != required_type):
      raise(AttributeError("Wrong type of parameter "+key+" : is "+attr.__class__.__name__+" should be "+required_type.__name__))
      return False # eh.. program quits anyway
  return True
    

def objectCheck(definitions, obj):
  """ Checks that object has certain attributes, according to definitions
  
  :param definitions: Dictionary defining the parameters and their types (obj should have at least these attributes)
  :param obj:         Object to be checked
  
  An example definitions dictionary:
  
  |{
  |"age"     : int,         # must have attribute age that is an integer
  |"name"    : str,         # must have attribute name that is a string            
  | }
  """
  
  for key in definitions:
    required_type=definitions[key]
    attr=getattr(obj,key) # this raises an AttributeError of object is missing the attribute - but that is what we want
    # print("objectCheck:","got: ",attr,"of type",attr.__class__,"should be",required_type)
    if (attr.__class__ != required_type):
      raise(AttributeError("Wrong type of parameter "+key+" : should be "+required_type.__name__))
      return False # eh.. program quits anyway
  return True
    
  
def parameterInitCheck(definitions, parameters, obj):
  """ Checks that parameters are consistent with a definition
  
  :param definitions: Dictionary defining the parameters, their default values, etc.
  :param parameters:  Dictionary having the parameters to be checked
  :param obj:         Checked parameters are attached as attributes to this object
  
  An example definitions dictionary:
  
  |{
  |"age"     : (int,0),                 # parameter age defaults to 0 if not specified
  |"height"  : int,                     # parameter height **must** be defined by the user
  |"indexer" : some_module.Indexer,     # parameter indexer must of some user-defined class some_module.Indexer
  |"cleaner" : checkAttribute_cleaner,  # parameter cleaner is check by a custom function named "checkAttribute_cleaner" (that's been defined before)
  |"weird"   : None                     # parameter weird is passed without any checking - this means that your API is broken  :)
  | }
  
  """
  definitions=copy.copy(definitions)
  #print("parameterInitCheck: definitions=",definitions)
  for key in parameters:
    try:
      definition=definitions.pop(key) 
    except KeyError:
      print(obj.__class__,"Unknown parameter "+str(key))
      #raise AttributeError("Unknown parameter "+str(key))
      
    parameter =parameters[key]
    if (definition.__class__==tuple):   # a tuple defining (parameter_class, default value)
      #print("parameterInitCheck: tuple")
      required_type=definition[0]
      if (parameter.__class__ != required_type):
        raise(AttributeError("Wrong type "+parameter.__class__.__name__+" for parameter "+key+" : should be "+required_type.__name__))
      else:
        setattr(obj,key,parameter)
    elif isinstance(definition, types.FunctionType):
      # object is checked by a custom function
      #print("parameterInitCheck: callable")
      ok=definition(parameter)
      if (ok):
        setattr(obj,key,parameter)
      else:
        raise(AttributeError("Checking of parameter "+key+" failed"))
    elif (definition==None):            # this is a generic object - no checking whatsoever
      #print("parameterInitCheck: None")
      setattr(obj,key,parameter)
    elif (definition.__class__==type):  # Check the type
      #print("parameterInitCheck: type")
      required_type=definition
      if (parameter.__class__!=required_type):
        raise(AttributeError("Wrong type of parameter "+key+" : should be "+required_type.__name__))
      else:
        setattr(obj,key,parameter)
    else:
      raise(AttributeError("Check your definitions syntax"))
      
  # in definitions, there might still some leftover parameters the user did not bother to give
  for key in definitions.keys():
    definition=definitions[key]
    if (definition.__class__==tuple):   # a tuple defining (parameter_class, default value)
        setattr(obj,key,definition[1])
    elif (definition==None):
        setattr(obj,key,None)
    else:
      raise(AttributeError("Missing a mandatory parameter "+key))
    
    
def noCheck(obj):
  return True


def getrecordingsClips():
  show_recPath = os.path.join(os.path.expanduser("~"), ".duranc", "gateway", "local_rec")
  feed_dataPath = os.path.join(os.path.expanduser("~"), ".duranc", "gateway", "db","recorder_feeds")
  recordings_dict = {}
  for each_feedFolder in os.listdir(show_recPath):
    recordings_dict[each_feedFolder] = {}
    recording_feedfilepath = os.path.join(show_recPath,each_feedFolder)
    inp_feeddetailsPath = os.path.join(feed_dataPath,each_feedFolder)
    recordings_dict[each_feedFolder]["name"] = readFeedName(inp_feeddetailsPath)
    recordings_dict[each_feedFolder]["recording_name"] = []
    recordings_dict[each_feedFolder]["recording_path"] = []
    for each_recording in sorted(os.listdir(recording_feedfilepath)):
      each_recordingPath = os.path.join(recording_feedfilepath,each_recording)
      new_recordingpath = "/".join(each_recordingPath.split("/")[-3:])
      # recordings_dict[each_feedFolder]["feed_path"].append(each_recordingPath)
      # tuplevalue = (each_recordingPath,each_recording)
      covertedRecordName = convtrecordname(each_recording)
      recordings_dict[each_feedFolder]["recording_name"].append(covertedRecordName)
      recordings_dict[each_feedFolder]["recording_path"].append(new_recordingpath)

  return recordings_dict

def readFeedName(feedidFile):
  feedName = None
  try:
    with open(feedidFile) as f:
      data = json.load(f)
      feedName =  data["name"]
  except Exception as e:
    print("Failed to read feed Name")
    print(e)

  return feedName

def convtrecordname(recordname: str):
  recordname = recordname[:-4]
  starttime = covtunixtime(recordname.split("-")[0])
  endtime = covtunixtime(recordname.split("-")[1])
  timezone = time.tzname[0]
  finalcovtTime = starttime + " "+timezone+ " - " +endtime + " "+timezone 
  return finalcovtTime

def covtunixtime(unixtimstamp: str):
  
  return datetime.fromtimestamp(
        int(unixtimstamp)
    ).strftime('%b %d %Y, %I:%M %p')  
  

def getfeedrecordinglicense(feedid: str):
  feedsdir = os.path.join(os.path.expanduser("~"), ".duranc", "gateway", "db","feeds")
  feed_file = os.path.join(feedsdir,feedid)
  feedData = loadJson(feed_file)
  recordinglicense = feedData["recording"]["days"]

  return recordinglicense

def checkIfDocker():
  systemcmd = "supervisorctl status pusher"
  cmd = os.system(systemcmd)
  if cmd == 0:
    return True
  else:
    return False

def linklocalrecPath(): ## Link the backup recording for show videos clips locally
  from duranc.gateway import userspace
  localrecPath = os.path.join(os.path.expanduser("~"), ".duranc", "gateway", "local_rec")
  gatewayinstalledPath = inspect.getfile(userspace)
  staticpath = "/".join(gatewayinstalledPath.split("/")[:-1])
  localwebserverpath = os.path.join(staticpath,"www","static","local_rec")
  if os.path.isdir(localwebserverpath):
    print("Link directory is present")
  else:
    os.system("ln -s "+localrecPath+" "+ localwebserverpath)

  return


def loadJson(filename: str):
    try:
        f = open(filename, "r")
        dic = json.loads(f.read())
        f.close()
    except Exception as e:
        return None
    else:
        return dic

def createJson(data: dict, filename: str): # Creating a Json File
  try:

    with open(filename, "w") as write_file:
      json.dump(data, write_file)

    write_file.close()
  except Exception as e:
    print("Failed to create json %s, for exception %s",filename,e)

def generate_localrec_metadata(record=None,eventType=None,clip_type = None): # Generating recording metaData
  recording_clip_data = record.split("/")
  feedId = recording_clip_data[-2]
  filename = recording_clip_data[-1]
  starttime = filename[:-4].split("-")[0]
  endtime = filename[:-4].split("-")[1]
  data = {"metadata":{}}
  size_mbytes = round(os.path.getsize(record)/ 1024 / 1024)
  data["metadata"]["filesize"] = size_mbytes
  data["metadata"]["feedId"] = feedId
  data["metadata"]["filename"] = filename
  data["metadata"]["time"] = int(starttime)
  data["metadata"]["end"] = int(endtime)
  data["metadata"]["filepath"] = record
  data["metadata"]["record_entry"] = eventType
  data["metadata"]["clip_type"] = clip_type
  outputJsonfilename = feedId+"_"+filename[:-4]+"_"+eventType+".json"
  outputJsonfilename = os.path.join(rec_metadataResource,outputJsonfilename)
  createJson(data=data,filename=outputJsonfilename)

  return


# Check for netstat status and create files

def getnetstatcount():
  netstat_subprocess = subprocess.Popen("netstat -an | grep CLOSE ", shell=True, stdout=subprocess.PIPE)
  netstat_subprocess_return = netstat_subprocess.stdout.read()
  netstat_subprocess_data = netstat_subprocess_return.decode('utf-8').strip("\n")
  netstat_subprocess_data = netstat_subprocess_data.split("\ntcp")
  netstat_count = len(netstat_subprocess_data)

  return netstat_count, netstat_subprocess_data

def generate_netstat_report(netstatData):
  import datetime
  filename = os.path.join(os.path.expanduser("~"),".duranc","gateway","netstatcount.txt")
  currenttime = datetime.datetime.now()
  netstatData.insert(0,currenttime)
  if os.path.isfile(filename):
    with open(filename, 'a') as f:
      for item in netstatData:
          f.write("%s\n" % item)
    f.close()
  else:
    with open(filename, 'w') as f:
      for item in netstatData:
          f.write("%s\n" % item)
    f.close()

# Check for failed upload recordings

def check_upload_failed(record=None):
    # recording_clip_data = record.getFullPath().split("/")
    feedId = record.getFeedId()
    # filename = recording_clip_data[-1].split(".")[0]
    filename = record.getFileName().split(".")[0]
    metadata_filename = os.path.join(rec_upload_failed_metadataResource,feedId+"_"+filename+".json")
    if os.path.isfile(metadata_filename):
        failed_metadata = loadJson(metadata_filename)
        if failed_metadata is not None:            
            failed_count = failed_metadata["failed_count"]
            new_failed_count = failed_count+1
            failed_metadata["failed_count"] = new_failed_count
            createJson(data = failed_metadata,filename=metadata_filename)

    else:
        metadata = {}
        metadata["feedId"] = feedId
        metadata["recording_clip"] = filename
        metadata["failed_count"] = 1
        createJson(data = metadata, filename=metadata_filename)


    return

def rm_faileduploads(recordings_list=None):
    current_recording_list = []
    final_recording_list = []
    current_recording_list = [record.getFullPath() for record in recordings_list]
    failed_recording_list = []
    rec_path = os.path.join(home,".duranc","gateway","rec")
    for failed_file in os.listdir(rec_upload_failed_metadataResource):
        failed_metadata = loadJson(os.path.join(rec_upload_failed_metadataResource,failed_file))
        if failed_metadata is not None:
            failed_count = failed_metadata["failed_count"]
            failed_rec_filename = os.path.join(rec_path,failed_metadata["feedId"],failed_metadata["recording_clip"]+".mp4")
            if failed_rec_filename not in current_recording_list:
                metadata_filename = os.path.join(rec_upload_failed_metadataResource,failed_metadata["feedId"]+"_"+failed_metadata["recording_clip"]+".json")
                deleteJson(metadata_filename)
            elif failed_count >= numerical.upload_failed_count:
                failed_recording_list.append(failed_rec_filename)

    for record in recordings_list:
        if record.getFullPath() not in failed_recording_list:
            final_recording_list.append(record)
            
    return final_recording_list


def deleteJson(filename=None):
    if os.path.isfile(filename):
        os.remove(filename)

    else:
        print("Json metadata not found")


## Create dynamic url

def generate_http_liveStream_url():
    from duranc.gateway.system import getSystemReport__
    system_report = getSystemReport__()
    newtork_details = system_report["network"]
    ip4 = None
    wifi_ip = None
    for each_newtork in newtork_details:
        if not each_newtork["internal"] and each_newtork["ip4"] is not None:
            ip4 = each_newtork["ip4"]
        if each_newtork["iface"] == "wlan0":
            wifi_ip = each_newtork["ip4"]
        if each_newtork["iface"] == "wlo1":
            wifi_ip = each_newtork["ip4"]
    if ip4 is None:
        ip4 = wifi_ip
    # ip4 = system_report["network"][1]["ip4"]
    pusher_env_file = os.path.join(home,".duranc","gateway","env","pusher.env")
    try:
        env_data = configToDic(pusher_env_file)
        port_value = env_data["port"]
    except Exception as e:
        print("ENV file is missing so setting to default value")
        port_value = "3000"
    live_stream_url = "http://"+str(ip4)+":"+str(port_value)+"/live_view"
    # print(live_stream_url)
    return live_stream_url
    
    
# Get failed_uploads count

def get_failed_uploads_count():
    failed_uploads_dir = os.path.join(home,".duranc","gateway","upload_failed")
    try:
        failed_uploads_count = len(os.listdir(failed_uploads_dir))
    except Exception as e:
        print("Cannot retrieve failed upload count",e)
        failed_uploads_count = 0

    return failed_uploads_count


# Check if link is present for rec file:

def check_link_condition(record=None):
  record_filename = record.getFileName()
  feedId = record.getFeedId()
  link_path = os.path.join(rec_Resource,feedId,record_filename)
  return os.path.islink(link_path)

def delete_rec_link(record=None):
  if check_link_condition(record):
    record_filename = record.getFileName()
    feedId = record.getFeedId()
    link_path = os.path.join(rec_Resource,feedId,record_filename)
    os.unlink(link_path)

def move_recording(record=None):
  feedId = record.getFeedId()
  rec_path = os.path.join(home,".duranc","gateway","rec",feedId,record.getFileName())
  shutil.copy(record.getFullPath(),rec_path)

## Filtering Streamer URL
def filter_streamer_url(url):
  # check for http or https:
  httpstatus = url.split(":")[0]
  if httpstatus == "http":
    streamerurl = url.split("//")[1].split(":")[0]
    
  else:
    streamerurl = url.split("//")[1]
    
  return streamerurl



