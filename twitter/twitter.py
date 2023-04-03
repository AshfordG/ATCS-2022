from models import *
from database import init_db, db_session
from datetime import datetime

class Twitter:

    def __init__(self):
        self.currentuser = None

    """
    The menu to print once a user has logged in
    """
    def print_menu(self):
        print("\nPlease select a menu option:")
        print("1. View Feed")
        print("2. View My Tweets")
        print("3. Search by Tag")
        print("4. Search by User")
        print("5. Tweet")
        print("6. Follow")
        print("7. Unfollow")
        print("0. Logout")
    
    """ 
    Prints the provided list of tweets.
    """
    def print_tweets(self, tweets):
        for tweet in tweets:
            print("==============================")
            print(tweet)
        print("==============================")

    """
    Should be run at the end of the program
    """
    def end(self):
        print("Thanks for visiting!")
        db_session.remove()
    
    """
    Registers a new user. The user
    is guaranteed to be logged in after this function.
    """
    def register_user(self):
        #Loop through until succsessful register user
        prompt = True
        while prompt:
            handle = input("What will your twitter handle be?\n")
            password = input("Enter a password:\n")
            check = input("Re-enter your password:\n")
            #Check that password was correct
            if check==password:
                #Check that handle is not already in use
                #Create new user, commit, and set current user
                if db_session.query(User).where(User.username == handle).count() == 0:  
                    newuser = User(username = handle, password = password)
                    db_session.add(newuser)
                    print("Welcome @" + newuser.username)
                    prompt = False
                    self.currentuser = newuser
                    db_session.commit()
                else:
                    print("Username Taken. Try Again\n")
            else:
                print("Those Passwords don't match. Try Again\n")
        
            
    """
    Logs the user in. The user
    is guaranteed to be logged in after this function.
    """
    def login(self):
        #Loop through login until succsessful
        loop=True
        while loop:
            name = input("Username: ")
            key = input("Password: ")
            #Check if entered info matches a registered user, if yes then set currentuser
            if db_session.query(User).where((User.username == name) & (User.password == key)).first() != None:
                self.currentuser = db_session.query(User).where((User.username == name) & (User.password == key)).first()
                loop = False
                print("\nWelcome back, @" + self.currentuser.username)
            else:
                print("\nInvalid Username or Password\nTry Again\n")

    def logout(self):
        self.currentuser = None
        print("You have been logged out")
        return

    """
    Allows the user to login,  
    register, or exit.
    """
    def startup(self):
        print("Welcome to ATCS Twitter!\n Please select a Menu Option")
        choice = int(input("1. Login\n2. Register User\n0. Exit\n"))
        if choice==1:
            self.login()
        elif choice==2:
            self.register_user()
        elif choice==0:
            self.logout()

    def follow(self):
        #Ask user who to follow, check if user is already followed
        #If yes, exit and tell user, else check if user is real and follow if true
        following_username = input("Who Would you like to follow? ")
        following_user = db_session.query(User).where(User.username==following_username).first()
        if following_user in self.currentuser.following:
            print("You already follow @" + following_username)
        else:
            if following_user is not None:
                db_session.add(Follower(follower_id = self.currentuser.username, following_id = following_username))
                db_session.commit()
                print("\n\nYou now follow @" + following_username)
            else:
                print("Username entered incorrectly")

    def unfollow(self):
        #Prompt for user to unfollow, query for user by entered username
        following_username = input("Who would you like to unfollow\n")
        followed = db_session.query(Follower).where((Follower.follower_id==self.currentuser.username) & (Follower.following_id==following_username)).first()
        #Check user is followed, if yes --> unfollow and commit, else do nothing and tell user
        if followed is not None:
            db_session.delete(followed)
            db_session.commit()
            print("\n\nYou unfollowed @" + following_username)
        else:
            print("You dont follow @" + following_username)

    def tweet(self):
        #Gather tweet information
        txt = input("Create Tweet: ")
        hashtags = input("Enter your tags seperated by spaces: ").split()
        time = datetime.now()
        #Create tag objects for each tag and commit
        tag_list = []
        for tag in hashtags:
            newtag = Tag(content=tag)
            tag_list.append(newtag)
            db_session.add(newtag)
            db_session.commit()
        #Create tweet object and commit
        newtweet = Tweet(content=txt, timestamp=time, username=self.currentuser.username)
        db_session.add(newtweet)
        db_session.commit()
        #Create new TweetTag Object for each tag corresponding to tweet
        for tag in tag_list:
            newTweetTag = TweetTag(tweet_id = newtweet.id, tag_id=tag.id)
            db_session.add(newTweetTag)
            db_session.commit()
        #Show user their tweet 
        print("\nYou posted:\n")
        print("==============================")
        print(newtweet)    
        print("==============================\n")

    def view_my_tweets(self):
        #Print all tweets whose user matches current user
        current_tweets = db_session.query(Tweet).where(Tweet.username==self.currentuser.username).all()
        self.print_tweets(current_tweets)
    """
    Prints the 5 most recent tweets of the 
    people the user follows
    """
    def view_feed(self):
        #Add all followed users to a list, then print all tweets from users in list
        followers = [person.username for person in self.currentuser.following]
        tweets = db_session.query(Tweet).where(Tweet.username.in_(followers)).order_by(Tweet.timestamp).limit(5).all()
        self.print_tweets(tweets)

    def search_by_user(self):
        #Query for all tweets with username matching desired user, then print
        user = input("\nWho's tweets do you want to see: ")
        check = db_session.query(User).where(User.username==user).first()
        #Check that entered searched user exists
        if check is None:
            print("\nThere are no users by that name\n")
            return
        tweets = db_session.query(Tweet).where(Tweet.username==user).order_by(Tweet.timestamp).all()
        self.print_tweets(tweets)

    def search_by_tag(self):
        #Ask for tag to search by
        desired_tag = input("\nWhat tag do you want to search by: ")
        tag_instances = db_session.query(Tag).where(Tag.content==desired_tag).all()
        #Check that tag exists
        if tag_instances is None:
            print("There are no tweets with that tag yet\n")
            return
        #Gather ids of each instance of tag to search by, then print all tweets with that tag
        tag_ids = []
        for tag in tag_instances:
            tag_ids.append(tag.id)
        tweets = db_session.query(Tweet).where((Tweet.id==TweetTag.tweet_id) & (TweetTag.tag_id.in_(tag_ids))).all()
        self.print_tweets(tweets)

    """
    Allows the user to select from the 
    ATCS Twitter Menu
    """
    def run(self):
        init_db()

        print("Welcome to ATCS Twitter!")
        self.startup()
        
        loop=True
        while loop:
            self.print_menu()
            option = int(input(""))

            if option == 1:
                self.view_feed()
            elif option == 2:
                self.view_my_tweets()
            elif option == 3:
                self.search_by_tag()
            elif option == 4:
                self.search_by_user()
            elif option == 5:
                self.tweet()
            elif option == 6:
                self.follow()
            elif option == 7:
                self.unfollow()
            else:
                self.logout()
                loop=False
        
        self.end()
