"""
291 - Mini project 2

phase 2:
login (optional)
post question
search question
    select question
    answer question
    list answers
        vote answer
    vote question

"""

import time
import string
import numbers
import re
from datetime import datetime
from datetime import date
from pymongo import MongoClient
from statistics import mean



class Post:

    def __init__(self, number, Id, AcceptedAnswerId, CreationDate, Score, ViewCount, Body,
    OwnerUserId, LastEditDate, LastActivityDate,Title,Tags,AnswerCount,CommentCount,
    FavoriteCount,ContentLicense, parent_id):
        self.post_number = number    #just to make displaing and selecting a post easier

        self.Id = Id
        self.AcceptedAnswerId = AcceptedAnswerId
        self.CreationDate = CreationDate
        self.Score = Score
        self.ViewCount = ViewCount
        self.Body = Body
        self.OwnerUserId = OwnerUserId
        self.LastEditDate = LastEditDate
        self.LastActivityDate = LastActivityDate
        self.Title = Title
        self.Tags = Tags
        self.AnswerCount = AnswerCount
        self.CommentCount = CommentCount
        self.FavoriteCount = FavoriteCount
        self.ContentLicense = ContentLicense
        self.parent_id = parent_id  #for answer posts

    def get_post_number(self):
        return self.post_number
    def get_Id(self):
        return self.Id
    def get_AcceptedAnswerId(self):
        return self.AcceptedAnswerId
    def get_CreationDate(self):
        return self.CreationDate
    def get_Score(self):
        return self.Score
    def get_ViewCount(self):
        return self.ViewCount
    def get_Body(self):
        return self.Body
    def get_OwnerUserId(self):
        return self.OwnerUserId
    def get_LastEditDate(self):
        return self.LastEditDate
    def get_LastActivityDate(self):
        return self.LastActivityDate
    def get_Title(self):
        return self.Title
    def get_Tags(self):
        return self.Tags
    def get_AnswerCount(self):
        return self.AnswerCount
    def get_CommentCount(self):
        return self.CommentCount
    def get_FavoriteCount(self):
        return self.FavoriteCount
    def get_ContentLicense(self):
        return self.ContentLicense
    def get_post_data(self):
        data = [self.Id, self.OwnerUserId, self.ViewCount, self.Score,
        self.FavoriteCount, self.CommentCount, self.AnswerCount,
        self.CreationDate, self.Title, self.Body, self.Tags,
        self.AcceptedAnswerId, self.LastActivityDate,
        self.LastEditDate, self.ContentLicense]
        data = [str(x) for x in data]
        return data


class User:
    def __init__(self, uid):
        self.uid = uid

    def get_uid(self):
        return self.uid

    def getuser_report(self):
        #shows report on the user id provided:
        # - number of questions owned & avg score of those questions
        # - number of answers owned & avg score of those answers
        # - number of votes registered for user

        global db

        #variables to store info
        questions = {}
        answers = {}
        votes = 0

        posts = db["Posts"]
        votes = db["Votes"]

        for post in posts.find({"OwnerUserId": self.uid},{"_id":1, "PostTypeId":1, "Score":1}):
            if post["PostTypeId"] == "1":
                #is a question
                questions[post["_id"]] = int(post["Score"])

            elif post["PostTypeId"] == "2":
                #is an answer
                answers[post["_id"]] = int(post["Score"])

        #get all votes registered under user
        total_votes = 0
        for vote in votes.find({"UserId": self.uid}, {"_id":1}):
            total_votes += 1


        #display report
        border = "-"*31
        print("\n", border)
        print("Showing report of user ", self.uid)
        print(border)
        col_names = ["Category", "Count", "Avg Score"]
        print("|{:^10}|{:^7}|{:^10}|".format(*col_names))

        # - questions
        q_count = len(questions)
        scores_q = questions.values()
        avg_q_score = round(mean(scores_q), 2)
        print("|{:^10}|{:^7}|{:^10}|".format("Questions", q_count, avg_q_score))

        # - answers
        a_count = len(answers)
        scores_a = answers.values()
        avg_a_score = round(mean(scores_a), 2)
        print("|{:^10}|{:^7}|{:^10}|".format("Answers", a_count, avg_a_score))

        # - votes
        print("|{:^10}|{:^7}|{:^10}|".format("Votes", total_votes, "N/A"))

    def postQuestion(self):
        #creates a question post
        #gets: title, body. tag(option)
        #auto gen: id, CreationDate, OwnerUserId,quantities Score, ViewCount, AnswerCount,
        #CommentCount, and FavoriteCount,content license
        #returns True when completed

        print("Type 'back' to return to the previous page")

        posts = db["Posts"]

        #get max post id in system

        max_id = int(posts.find_one(sort = [("Id", -1)])["Id"])

        #generate a unqie id
        newId = max_id +1

        #ask for title
        Title = input("Enter a title for your post: ")
        if Title.lower() == 'back':
            return False

        #ask for body text
        Body = input("Enter a question:\n")
        if Body.lower() == 'back':
            return False

        #ask for tags
        Tags=[]
        stop=1
        while stop:
            tag = input("Enter a tag for your post, if no press N: ")
            if tag.lower() == 'back':
                return False
                #for safety reason
                break
            elif tag.lower() == 'n':
                stop = 0
                break
            else:
                Tags.append(tag)
                stop = 0

        #create terms list
        terms = set()
        #process title and body for terms
        #remove all special characters
        pattern = re.compile(r'\W+')
        #split the string
        words = pattern.split(Title)
        words.extend(pattern.split(Body))
        #add tags
        words.extend(Tags)
        #only add to terms if length >=3
        for word in words:
            if len(word) >= 3:
                terms.add(word.lower())

        #insert question post to collection:
        new_question={"Id": newId,"PostTypeId": "1", "CreationDate":datetime.today().strftime('%Y-%m-%d'),
        "Score": 0, "ViewCount": 0,"Body": Body,"OwnerUserId": self.uid, "Title":Title,"Tags": tag,
        "AnswerCount": 0, "CommentCount": 0, "FavoriteCount": 0, "ContentLicense": "CC BY-SA 2.5",
        "terms": list(terms)}
        x=posts.insert_one(new_question)
        print("You just post a question!")

        return True


    def postAnswer(self, id):
        #creates an answer post
        #gets:  body
        #auto gen: id, ParentId, CreationDate, OwnerUserId, Score,
        #CommentCount, content license
        #returns True when completed

        print("Type 'back' to return to the previous page")

        posts = db["Posts"]

        #get max post id in system
        max_id = int(posts.find_one(sort = [("Id", -1)])["Id"])

        #generate a unqie id
        newId = max_id +1

        #ask for body text
        Body = input("Enter an answer:\n")
        if Body.lower() == 'back':
            return False

        #create terms list
        terms = set()
        #process title and body for terms
        #remove all special characters
        pattern = re.compile(r'\W+')
        #split the string
        words = pattern.split(Body)
        #only add to terms if length >=3
        for word in words:
            if len(word) >= 3:
                terms.add(word.lower())

        #insert question post to collection:
        new_answer={"Id": newId,"PostTypeId": "2", "CreationDate":datetime.today().strftime('%Y-%m-%d'),
        "Score": 0, "Body": Body,"OwnerUserId": self.uid,  "CommentCount": 0,
        "ContentLicense": "CC BY-SA 2.5", "terms": list(terms)}
        x=posts.insert_one(new_answer)
        print("You just post an answer!")

        return True



    def listAnswer (self, qid):
        border = "-"*50
        print(border)

        #queries answers
        matching_answers = query_for_answers(qid)

        #if no answer found,  return to main signed in block
        if len(matching_answers) == 0:
            print("No posts found")
            return

        #show answers and allow selection
        selected_post = select_post(matching_answers, "answers")

        #if user enters 'back', return
        if selected_post == 'back':
            return

        print("selected answer post: ", selected_post.get_Id())

        show_post(selected_post)
        print("")

        return selected_post

    def vote(self, pid):
        votes = db["Votes"]
        posts = db["Posts"]
        if self.uid:
            user_votes = votes.find({"$and": [{"UserId": self.uid}, {"PostId": pid}]})
            uvotes = []
            for each in user_votes:
                # print(each["UserId"])
                uvotes.append(each["UserId"])
            if uvotes:
                print("You have already voted on this post!")
                return
            else:
                vote_id = []
                votes_id_ = votes.find({"PostId": pid})
                for each in votes_id_:
                    # print(each)
                    id = int(each["Id"])
                    vote_id.append(id)
                # print(vote_id)
                max_id = 0
                if vote_id:
                    max_id = max(vote_id)
                new_id = max_id + 1
                crdate = str(date.today())
                new_vote = {"Id": new_id, "PostId": pid, "VoteTypeId": "1", "UserId": self.uid, "CreationDate": crdate}
                votes.insert_one(new_vote)
                score = int(posts.find_one({"Id": pid})["Score"])
                posts.update_one({"Id": pid}, {"$set": {"Score": score + 1}})
                print("You have voted successfully!\n")
        else:
            vote_id = []
            votes_id_ = votes.find({"PostId": pid})
            for each in votes_id_:
                # print(each)
                id = int(each["Id"])
                vote_id.append(id)
            # print(vote_id)
            max_id = 0
            if vote_id:
                max_id = max(vote_id)
            new_id = max_id + 1
            crdate = str(date.today())
            new_vote = {"Id": new_id, "PostId": pid, "VoteTypeId": "1", "CreationDate": crdate}
            votes.insert_one(new_vote)
            score = int(posts.find_one({"Id": pid})["Score"])
            posts.update_one({"Id": pid}, {"$set": {"Score": score + 1}})
            print("You have voted successfully!\n")
        return

#LOGIN PAGE: SIGN IN (optinal), SHOW REPORT
#########################################################################


def intro():
    #print intro
    #asks if user wants to login or sign up
    print("Hello!")

    #until user has successfully logged in (either
    #anonymously or with a valid uid) keep asking for input
    login_done = False
    while not login_done:

        print("To close the program, type 'exit'")
        uid = input("Please enter your user id, otherwise press enter to continue:\n")

        if uid.lower() == "exit":
            #end program
            print("... adios :)")
            quit()

        elif len(uid) != 0:
            #login with uid
            user = sign_in(uid)

            if user == None:
                #uid doesn't exist
                print("Error! User doesn't exist!\n")

            else:
                #show report of user
                user.getuser_report()
                login_done = True

        else:
            #anonymous login
            user = User(None)
            login_done = True

    return user


def sign_in(uid):
    #verify if user exists

    global db
    posts = db["Posts"]

    #search for user
    exists = posts.find_one({"OwnerUserId": uid})

    if exists == None:
        #return None if user doesn't exist
        return None
    else:
        #return User class object if exists
        return User(uid)



#MAIN PAGE: INSTRUCTIONS, MAIN MENU NAVIGATION
########################################################################

def instructions():
    #prints menu instructions

    print("""
        -----------------------------------------------------
         help       show instructions
         postq      post a question
         search     search for question posts
         exit       exits program

         The following are post-search actions:
         answer     post an answer to a selected question post
         list       lists all answers of the selected question
         vote       upvote a selected post
         -----------------------------------------------------
      """)

def main_menu(user):
    #allows user to post questions, search or exit

    border = "-"*50
    print(border)
    instructions()

    ps_actions = ["answer", "list", "vote"]
    selected_q = None
    selected_a = None

    is_done = False
    while not is_done:
        print("\nEnter 'help' for instructions")
        action = input("What would you like to do? ")

        if action.lower() == "exit":
            #end the program
            print("... adios :)")
            quit()

        elif action.lower() == "help":
            #print instructions
            instructions()

        elif action.lower() == "postq":
            #post a question
            user.postQuestion()

        elif action.lower() == "search":
            #search for questions
            selected_q = search()

        elif action.lower() in ps_actions:

            if isinstance(selected_q, Post) or isinstance(selected_a, Post):
                #if selected post is a Post object

                if action.lower() == "answer":
                    #post an answer to the question
                    user.postAnswer(selected_q.get_Id())

                elif action.lower() == "list":
                    #list all answers of the question
                    #also allow user to select one
                    selected_a = user.listAnswer(selected_q.get_Id())

                elif action.lower() == "vote":
                    #vote on a selected post

                    if selected_a == None:
                        #if on question post selected
                        user.vote(selected_q.get_Id())

                    else:
                        #a question post and an answer post have been selected

                        #ask user which one they want to vote on
                        print("Which post do you want to vote on?")
                        post_to_vote = input("Enter q for question, or a for answer: ")

                        if post_to_vote.lower() == "q":
                            user.vote(selected_q.get_Id())
                        elif post_to_vote.lower() == "a":
                            user.vote(selected_a.get_Id())
                        else:
                            print("Invalid input! Please try again!\n")
            else:
                #no post selected
                print("Error! Please first select a post through search! \n")
        else:
            print("Invalid! Please try again! \n")




#SEACH BLOCK: SEARCH USING KEYWORDS, DISPLAY RESULTS, SELECT POST
#######################################################################
def get_keywords():
    #get keywords and split them
    #if nothing was entered, raise error and ask again
    key_length = 0
    while key_length == 0:
        keywords = input("Enter a keyword or keywords separated by ',' to search: \n")
        keywords_lst = keywords.split(',')
        keywords_lst = [each.lower() for each in keywords_lst]
        key_length = len(keywords_lst)

        if key_length == 0:
            print("Cannot search without entering a keyword!")

    return keywords_lst


def display_results(post_list):
    #display results
    #show:
    #- question number (1-n for easier selecting)
    #- title, creation date, score, answer count

    #post_list needs to be in format:
    # [[post number, title, date, score, number of answers], ...,[post n]]

    border = '-'*39
    print("\nSearch results:")
    print(border)
    #maybe we can get this from cursor.description
    col_names = ["#", "title", "date created", "score", "answers"]
    print("|{:^3}|{:^10}|{:^12}|{:^5}|{:^5}|".format(*col_names))
    print(border)

    #print each post
    for post in post_list:
        post_data = [post.get_post_number(), post.get_Title(),
        post.get_CreationDate(), post.get_Score(), post.get_AnswerCount()]
        post_data = [str(x) for x in post_data]

        if len(post_data[1]) > 10:
            #long title
            print("|{:^3}|{:^7.7}...|{:^12.10}|{:^5}|{:^5}|".format(*post_data))

        else:
            print("|{:^3}|{:^10}|{:^12.10}|{:^5}|{:^5}|".format(*post_data))
    print(border)


def select_post(matching_posts, type):
    #processes list of posts obtained from query for displaying
    #asks user to select a post

    #print instructions
    instructions = ("\nTo select a post, type a number from 1-5 corresponding to its order.\n",
                    "Eg. To select the second post, type '2'. \n",
                    "To navigate between pages or posts, type 'next' or 'prev'.\n",
                    "To return to main page, type 'back'.\n")
    print("".join(instructions))

    post_selected = False

    #display and let user select a post
    if type == "answers":
        display_answers(matching_posts)
    elif type == "questions":
        display_results(matching_posts)
    while not post_selected:
        user_action = input("Enter an action: ")

        if user_action.lower() == "back":
            #cascade back to main page
            return user_action.lower()
        else:
            try:
                isinstance(int(user_action), numbers.Number)
                #if input is an int, check if a post is selected
                if int(user_action) <= len(matching_posts):
                    #return the post selected by user
                    return matching_posts[int(user_action)-1]
                else:
                    print("Invalid! Please try again.\n")
            except:
                print("Invalid! Please try again.\n")


def query_for_posts(keywords):
    #takes in keywords list
    #queries for posts
    #returns a list of Post objects
    global db
    posts = db["Posts"]

    ###############################################     QUERY
    #KEYWORDS MATCH IN TITLE, BODY, OR TAG FIELDS
    #GET POST (TITLE, CREATION DATE, SCORE)
    #GET NUMBER OF ANSWERS FOR EACH POST

    #####NEED TO USE INDEX FOR SEARCHING

    matching_posts = []
    i = 1  # to keep track of how many posts

    #search for posts that are questions (PostTypeId = 1)
    #       and match keywords provided
    for doc in posts.find({'$and': [{'PostTypeId': "1"}, {'terms': {'$in': keywords}}]}):

        if doc == None:
            #did not find a match
            return None

        else:
            #create Post class object
            #get all values
            id = doc.get('Id', None)
            accepted_answer_id = doc.get('AcceptedAnswerId', None)
            creation_date = doc.get('CreationDate', None)
            score = doc.get('Score', 0)
            view_count = doc.get('ViewCount', 0)
            body = doc.get('Body', "")
            owner_user_id = doc.get('OwnerUserId', None)
            last_edit_date = doc.get('LastEditDate', None)
            last_activity_date = doc.get('LastActivityDate', None)
            title = doc.get('Title', "")
            tags = doc.get('Tags', None)
            answer_count = doc.get('AnswerCount', 0)
            comment_count = doc.get('CommentCount', 0)
            favorite_count = doc.get('FavoriteCount', 0)
            content_liscense = doc.get('ContentLicense', 'CC BY 2.5')

            new_post = Post(i, id, accepted_answer_id, creation_date, score, view_count,
            body, owner_user_id, last_edit_date, last_activity_date, title, tags,
            answer_count, comment_count, favorite_count, content_liscense, None)

            matching_posts.append(new_post)

            i += 1


    ################################################
    return matching_posts



def show_post(post):
    #get post data
    # item order:
    # [Id, OwnerUserId,
    # ViewCount, Score, FavoriteCount,
    # CommentCount, AnswerCount,
    # CreationDate,
    # Title,
    # Body,
    # Tags,
    # AcceptedAnswerId,
    # LastActivityDate, LastEditDate, ContentLicense]
    post_data = post.get_post_data()

    decorator = "- "*10

    format = ["|Post Id: {:^8} | Owner User Id: {:^8}|\n",
              "|Views: {:^7} | Score: {:^3} | Favorites: {:^3}\n",
              "|Comments: {:^3} | Answers: {:^3}|\n",
              " Date created: {}\n",
              " Title: {}\n",
              " Body: {}\n",
              " Tags: {}\n",
              " Id of Accepted Answer: {}\n",
              " Last Activity Date: {}\n"
              " Last Edited: {}|\n",
              " Content License: {}|"]

    print(decorator)
    print("".join(format).format(*post_data))
    print(decorator)


def search():
    #this function is called when user want to search
    #handles searching and displaying results
    #returns a Post object of the post selected by the user
    #        or a string that says otherwise

    border = "-"*50
    print(border)

    #gets a list of keywords from user to search with
    keywords = get_keywords()
    #queries posts
    matching_posts = query_for_posts(keywords)

    #if no posts found, return to main signed in block
    if len(matching_posts) == 0:
        print("No posts found")
        return

    #show posts and allow selection
    selected_post = select_post(matching_posts, "questions")

    #if user enters 'back', return
    if selected_post == 'back':
        return

    print("selected question post: ", selected_post.get_Id())
    # update the view_count
    global db
    posts = db["Posts"]
    view_count = int(posts.find_one({"Id": selected_post.get_Id()})["ViewCount"])
    posts.update({"Id": selected_post.get_Id()}, {"$set":{"ViewCount": view_count + 1}})
    show_post(selected_post)
    print("")

    return selected_post

def query_for_answers(qid):
        #takes in question id
        #queries for answers
        #returns a list of Post(answers) objects
        global db
        posts = db["Posts"]

        ###############################################     QUERY
        #ParentId = qid
        #GET first 80 characters of the body text, creation date, and the score.
        #GET NUMBER OF ANSWERS FOR EACH POST

        matching_posts = []
        i = 1  # to keep track of how many posts

        #get the AcceptedAnswerId
        #accepted_id = posts.find({'AcceptedAnswerId':{'$Id':qid}})

        #rest of answers of questions
        for doc in posts.find({'$and': [{'PostTypeId': "2"}, {'ParentId':qid}]}):
            if doc == None:
                #did not find a match
                return None
            else:
                id = doc.get('Id', None)
                body = doc.get('Body', "")
                creation_date = doc.get('CreationDate', None)
                score = doc.get('Score', 0)
                content_license = doc.get('ContentLicense', "CC BY-SA 2.5")
                parent_id = doc.get('ParentId', "")


                new_post = Post(i, id, None, creation_date, score, None, body,
                                None, None, None, None, None, None, 0,
                                None, content_license, parent_id)
                matching_posts.append(new_post)

                i += 1

        return matching_posts

def display_answers(post_list):
    #display results
    #show:
    #- question number (1-n for easier selecting)
    #- title, creation date, score, answer count

    #post_list needs to be in format:
    # [[post number, title, date, score, number of answers], ...,[post n]]

    border = '-'*120
    print("\nAll answers:")
    print(border)
    #maybe we can get this from cursor.description
    col_names = ["#", "body", "date created", "score"]
    print("|{:^3}|{:^83}|{:^10}|{:^5}|".format(*col_names))
    print(border)
    #print each answer
    for post in post_list:
        post_data = [post.get_post_number(), post.get_Body(),
        post.get_CreationDate(), post.get_Score()]
        if len(post.get_Body()) > 80:
            #long body
            print("|{:^3}|{:^80.80}...|{:^10}|{:^5}|".format(*post_data))
        else:
            print("{:^3}|{:^83}|{:^10}|{:^5}|".format(*post_data))
    print(border)


#################################################

def connect():
    global db

    # Connect to the port on localhost for the mongodb server.
    #port_num = int(input("Please enter a port number to connect to: "))
    port_num = 27017
    client = MongoClient('localhost', port_num)

    # Create or open the video_store database on server.
    db = client["291db"]


def main():

    connect()

    user = intro()
    #move to main menu block
    main_menu(user)


if __name__ == "__main__":
    main()
