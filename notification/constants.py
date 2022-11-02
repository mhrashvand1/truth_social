PRIORITIES = [
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5")
]

NOTIF_TYPES = [
    (0, "truth_social_message"),
    (1, "follow"), 
    (2, "like"), 
    (3, "mention"), 
    (4, "retweet"), 
    (5, "new_tweet")
]

# default priorities
TRUTH_SOCIAL_MESSAGE_PRIORITY = 5 
FOLLOW_PRIORITY = 3
LIKE_PRIORITY = 2 
MENTION_PRIORITY = 4 
RETWEET_PRIORITY = 3 

# TODO
# Later we create a section named `settings` and user determine which priority 
# should be set for notifes