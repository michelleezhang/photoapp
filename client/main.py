#
# Client-side python app for photoapp
#

import requests  # calling web service
import jsons  # relational-object mapping

import uuid
import pathlib
import logging
import sys
import os
import base64

from configparser import ConfigParser

import matplotlib.pyplot as plt
import matplotlib.image as img


###################################################################
#
# classes
#
class User:
  userid: int  # these must match columns from DB table
  email: str
  lastname: str
  firstname: str
  bucketfolder: str


class Asset:
  assetid: int  # these must match columns from DB table
  userid: int
  assetname: str
  bucketkey: str


class BucketItem:
  Key: str      # these must match columns from DB table
  LastModified: str
  ETag: str
  Size: int
  StorageClass: str


###################################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number
  
  Parameters
  ----------
  None
  
  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  print()
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => stats")
  print("   2 => users")
  print("   3 => assets")
  print("   4 => download")
  print("   5 => download and display")
  print("   6 => bucket contents")

  cmd = int(input())
  return cmd


###################################################################
#
# stats
#
def stats(baseurl):
  """
  Prints out S3 and RDS info: bucket status, # of users and 
  assets in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/stats'
    url = baseurl + api

    res = requests.get(url)
    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract stats:
    #
    body = res.json()
    #
    print("bucket status:", body["message"])
    print("# of users:", body["db_numUsers"])
    print("# of assets:", body["db_numAssets"])

  except Exception as e:
    logging.error("stats() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


###################################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database
  
  Parameters
  ----------
  baseurl: baseurl for web service
  
  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/users'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()
    #
    # let's map each dictionary into a User object:
    #
    users = []
    for row in body["data"]:
      user = jsons.load(row, User)
      users.append(user)
    #
    # Now we can think OOP:
    #
    for user in users:
      print(user.userid)
      print(" ", user.email)
      print(" ", user.lastname, ",", user.firstname)
      print(" ", user.bucketfolder)

  except Exception as e:
    logging.error("users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def assets(baseurl):
  """
  Prints out all the assets in the database
  """
  try:
    #
    # call the web service:
    #
    api = '/assets'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return

    #
    # deserialize and extract assets:
    #
    body = res.json()
    #
    # let's map each dictionary into a Asset object:
    #
    assets = []
    for row in body["data"]:
      asset = jsons.load(row, Asset)
      assets.append(asset)
    #
    # Now we can think OOP:
    #
    for asset in assets:
      print(asset.assetid)
      print(" ", asset.userid)
      print(" ", asset.assetname)
      print(" ", asset.bucketkey)

  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def download(baseurl, display):
  """
  Downloads a given asset
  """
  try:
    # take asset id from user and pass to API function /download
    input_id = input("Enter asset id>\n")
    api = '/download'
    url = baseurl + api + '/' + input_id 
    
    res = requests.get(url)

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      return
      
    # deserialize and extract assets
  
    # return if the asset id is invalid
    body = res.json()
    if (body["user_id"] == -1):
      print("No such asset...")
      return

    # name of file should be the asset name from the response

    # decode the base64-encoded string
    decoded_data = base64.b64decode(body["data"])

    # write the data to the file system as a binary file
    file_name = body["asset_name"]
    outfile = open(file_name, "wb") # wb => write binary
    outfile.write(decoded_data)

    print("userid:", body["user_id"])
    print("asset name:", body["asset_name"])
    print("bucket key:", body["bucket_key"])
    print("Downloaded from S3 and saved as '", file_name, "'")
    
    if display:
      image = img.imread(file_name)
      plt.imshow(image)
      plt.show()
      
  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def buckets(baseurl):
  """
  Prints out information about each bucket asset
  """

  def bucket_helper(startafter=""):
    try:
      # call API function /bucket
      api = '/bucket'
      
      url = baseurl + api
      if (startafter != ""):
        url = url + "?startafter=" + startafter
      
      res = requests.get(url)
  
      if res.status_code != 200:
        # failed:
        print("Failed with status code:", res.status_code)
        print("url: " + url)
        if res.status_code == 400:  # error message
          body = res.json()
          print("Error message:", body["message"])
        return
        
      # deserialize and extract bucket info
      body = res.json()

      # map each dictionary to BucketItem object
      buckets = []
      for row in body["data"]:
        bucket = jsons.load(row, BucketItem)
        buckets.append(bucket)

      # special case: web service returns 0 assets
      if len(body["data"]) == 0:
        return -1
        
      for i in range(len(buckets)):
        bucket = buckets[i]
        print(bucket.Key)
        print(" ", bucket.LastModified)
        print(" ", bucket.Size) # int
        if i == len(buckets) - 1:
          last_key = bucket.Key

      return last_key
      
    except Exception as e:
      logging.error("assets() failed:")
      logging.error("url: " + url)
      logging.error(e)
      return

  last_key = bucket_helper()
  # if last_key == -1:
  #   return
  
  while last_key != -1:
    input_id = input("another page? [y/n] \n")
    if input_id == 'y':
      last_key = bucket_helper(last_key)
    else:
      return
  return

def add_user(baseurl):
  """
  Adds a user to the database
  """
  try:
    api = '/user'
    url = baseurl + api
    input_email = input("Enter user email>\n")
    input_lastname = input("Enter user last name>\n")
    input_firstname = input("Enter user first name>\n")
    input_bucketfolder = input("Enter user bucket folder>\n")
  
    data = {
      'email': input_email,
      'lastname': input_lastname,
      'firstname': input_firstname,
      'bucketfolder': input_bucketfolder
      }
  
    res = requests.put(url, json=data)
    
    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return
      
    # deserialize and extract assets:
    body = res.json()
    print(body)

  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return

def add_image(baseurl):
  """
  Adds a user to the database
  """
  try:
    api = '/image'
  
    input_userid = input("Enter user id>\n")
    url = baseurl + api + "/" + input_userid

    input_assetname = input("Enter asset name>\n")
    
    input_dataname = input("Enter data>\n")

    filename = input_dataname + '.jpg'

    with open(filename, 'rb') as file:
      input_data = bytearray(file.read()) 
    # open image as binary (returns array of bytes)
    
    input_data = base64.b64encode(input_data) # encode as base64
    
    input_data = input_data.decode()
    # convert to string

    data = {
      'assetname': input_assetname,
      'data': input_data
      }
  
    res = requests.post(url, json=data)
    
    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:  # we'll have an error message
        body = res.json()
        print("Error message:", body["message"])
      #
      return
      
    # deserialize and extract assets:
    body = res.json()
    print(body)

  except Exception as e:
    logging.error("assets() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  

#########################################################################
# main
#
print('** Welcome to PhotoApp v2 **')
print()

# eliminate traceback so we just get error message:
sys.tracebacklimit = 0

#
# what config file should we use for this session?
#
config_file = 'photoapp-client-config'

print("What config file to use for this session?")
print("Press ENTER to use default (photoapp-config),")
print("otherwise enter name of config file>")
s = input()

if s == "":  # use default
  pass  # already set
else:
  config_file = s

#
# does config file exist?
#
if not pathlib.Path(config_file).is_file():
  print("**ERROR: config file '", config_file, "' does not exist, exiting")
  sys.exit(0)

#
# setup base URL to web service:
#
configur = ConfigParser()
configur.read(config_file)
baseurl = configur.get('client', 'webservice')

# print(baseurl)

#
# main processing loop:
#
cmd = prompt()

while cmd != 0:
  #
  if cmd == 1:
    stats(baseurl)
  elif cmd == 2:
    users(baseurl)

  #
  elif cmd == 3:
    assets(baseurl)
  elif cmd == 4:
    download(baseurl, False)
  elif cmd == 5:
    download(baseurl, True)
  elif cmd == 6:
    buckets(baseurl)
  elif cmd == 7:
    add_user(baseurl)
  elif cmd == 8:
    add_image(baseurl)
  else:
    print("** Unknown command, try again...")
  #
  cmd = prompt()

#
# done
#
print()
print('** done **')
