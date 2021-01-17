"""
291 - Mini project 2

phase 1:
connect to database
drop/create collections
add data (create documents)


"""

import time
import string
import json
from pymongo import UpdateOne
from pymongo import MongoClient
import re

######## start timer
start = time.time()


# Connect to the port on localhost for the mongodb server.
#port_num = int(input("Please enter a port number to connect to: "))
port_num = 27017
client = MongoClient('localhost', port_num)


# Create or open the video_store database on server.
db = client["291db"]


# List collection names.
collist = db.list_collection_names()

#drop Posts, Tags, Votes collections if exists
if "Posts" in collist:
    if db.drop_collection("Posts"):
        print("Posts collection dropped!")
    else:
        print("Error! Could not drop Posts collection!")
if "Tags" in collist:
    if db.drop_collection("Tags"):
        print("Tags collection dropped!")
    else:
        print("Error! Could not drop Tags collection!")
if "Votes" in collist:
    if db.drop_collection("Votes"):
        print("Votes collection dropped!")
    else:
        print("Error! Could not drop Votes collection!")


# Create collections in the db
posts_collection = db["Posts"]
tags_collection = db["Tags"]
votes_collection = db["Votes"]


#read in json files
with open("Posts.json") as posts_file, open("Tags.json") as tags_file, open("Votes.json") as votes_file:
    #get data from files
    posts_data = json.load(posts_file)
    tags_data = json.load(tags_file)
    votes_data = json.load(votes_file)

    posts_data = posts_data["posts"]["row"]
    tags_data = tags_data["tags"]["row"]
    votes_data = votes_data["votes"]["row"]


# Insert values into collections
#checks if there is 1< entry for data,
#then uses appropriate insertion function
if isinstance(posts_data, list):
    posts_collection.insert_many(posts_data)
else:
    posts_collection.insert_one(posts_data)
if isinstance(tags_data, list):
    tags_collection.insert_many(tags_data)
else:
    tags_collection.insert_one(tags_data)
if isinstance(votes_data, list):
    votes_collection.insert_many(votes_data)
else:
    votes_collection.insert_one(votes_data)

print("done inserting data")
######end time
end = time.time()
hours, rem = divmod(end-start, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


#create index of all keywords length 3<=
#in posts title and body

## TODO: FIND terms
#        ADD TERMS AS AN ARRAY CALLED TERMS TO POSTS COLLECTION
#        CREATE INDEX
print("tring to create index")


#remove all special characters
#only keep alphanumeric characters
pattern = re.compile(r'\W+')

requests = []
#get all distinct terms in title and body of posts
for doc in posts_collection.find({}, {"_id":1, "Title":1, "Body":1, "Tags":1}):
    terms = set()

    #get post title and body
    post = doc.get('Title', "") + doc.get('Body', "")
    #get tags
    tags = doc.get('Tags', "")

    #split the string
    words = pattern.split(post)
    tags = tags[:-1].replace("<", "").split(">")
    words += tags

    #only add to terms if length >=3
    for word in words:
        if len(word) >= 3:
            terms.add(word.lower())

    #add new array field to document
    requests.append(UpdateOne({'_id':doc['_id']}, {'$set': {'terms':list(terms)}}))

posts_collection.bulk_write(requests)


######end time
end = time.time()
hours, rem = divmod(end-start, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))


#create index
posts_collection.create_index('terms')

######end time
end = time.time()
hours, rem = divmod(end-start, 3600)
minutes, seconds = divmod(rem, 60)
print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
