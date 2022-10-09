# This is windows only script
import ctypes 
import deviantart
import random
import requests
import os



# Generating a tag for DA request
if random.randrange (1,3) == 1:
    mytag="anime"
else:
    mytag="animeart"
    
# getting data from Deviantart

#create an API object with your client credentials (look up instructions at https://www.deviantart.com/developers/)
da = deviantart.Api("xxxxx", "yyyyyyyyyyyyyyyyyyyyyyyyyy")

#fetch daily deviations
# dailydeviations = da.browse_dailydeviations()
# .. 2days deviations with specific tags
dailydeviations = da.browse(endpoint='tags', category_path='', seed='', q='', timerange='24hr', tag=mytag, offset=0, limit=50)

# Choosing one random image from the collection
max=len(dailydeviations["results"])
result=random.randrange (0,max+1)
image_url=dailydeviations["results"][result].content["src"]

#Finding out our TMP path
temp=os.environ['TMP']
# Downloading picture
myfile = requests.get(image_url)
picPath=temp+'\da_image'
open(picPath, 'wb').write(myfile.content)

ctypes.windll.user32.SystemParametersInfoW(20,0,picPath,0)
