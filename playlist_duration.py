from googleapiclient.discovery import build
import re
from datetime import timedelta
import argparse 
import json

ap = argparse.ArgumentParser()
ap.add_argument("-l", "--link", required=True)
args = vars(ap.parse_args())

#retrieve api key from secrets.json
def get_api_key(json_file):

    try: 
        with open(json_file) as file:
            file = json.load(file)
            
        return file["api-key"]

    except: 
        print("Unable to retrieve api key")
        exit()

api_key = get_api_key("secrets.json")

#Create a service object
service = build('youtube','v3',developerKey = api_key)

#regex to parse hours, minutes and seconds
hours_pattern = re.compile(r'(\d+)H')
minutes_pattern = re.compile(r'(\d+)M')
seconds_pattern = re.compile(r'(\d+)S')

total_seconds = 0

#get the playlist ID
playlistId = args["link"]
playlistId = re.findall('=(\S+)',playlistId)[0]

#To iterate over pages
nextPageToken = None

while True:
    #Request data of playlist. 
    request = service.playlistItems().list(
        part = 'contentDetails',
        playlistId = playlistId,
        maxResults = 50,
        pageToken= nextPageToken
    )
    response = request.execute()

    #list of 50 video ids
    vid_id = [item['contentDetails']['videoId'] for item in response['items'] ] 

    #Requesting data of video
    vid_request = service.videos().list(
        part = 'contentDetails',
        id = ','.join(vid_id)
    )

    vid_response = vid_request.execute()

    #iterate over each data of each video
    for item in vid_response['items']:
        duration = item['contentDetails']['duration'] # duration of a video

        #parsing time of video using above regex
        hours = hours_pattern.search(duration)
        minutes = minutes_pattern.search(duration)
        seconds = seconds_pattern.search(duration)

        #if some value is not present it changes it to 0
        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0
        
        #convert duration to seconds and sums it
        video_secs= timedelta(
            hours = hours,
            minutes=minutes,
            seconds=seconds
        ).total_seconds()
        
        #sum of videos
        total_seconds += int(video_secs)

    #Increase pagetoken
    nextPageToken = response.get('nextPageToken')

    #Checks if next page is present, if not, breaks while loop
    if not nextPageToken:
        break
    
#find minutes, seconds and hours
minutes, seconds = divmod(total_seconds, 60)
hours, minutes = divmod(minutes, 60)

print(f'{hours} hours {minutes} minutes {seconds} seconds')
