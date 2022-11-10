PRIORITIES = [
    (1, "1"),
    (2, "2"),
    (3, "3"),
    (4, "4"),
    (5, "5")
]

NOTIF_TYPES = [
    (0, "truth_social"),
    (1, "follow"), 
    (2, "like"), 
    (3, "mention"), 
    (4, "retweet"), 
    (5, "new_tweet")
]

# Default notification priorities
TRUTH_SOCIAL_MESSAGE_PRIORITY = 5 
FOLLOW_PRIORITY = 3
LIKE_PRIORITY = 2 
MENTION_PRIORITY = 4 
RETWEET_PRIORITY = 3 

# TODO
# Later we create a section named `settings` and user determine which priority 
# should be set for notifes

# Notification Messages 
TRUTH_SOCIAL_MESSAGE = "type=truth_social&text={}&link={}"
FOLLOW_MESSAGE = "type=follow&actor={}" # username
LIKE_MESSAGE = "type=like&actor={}&tweet={}" # username, tweet_id
MENTION_MESSAGE = "type=mention&actor={}&tweet={}&mention={}" # username, tweet_id, mention_id
RETWEET_MESSAGE = "type=retweet&actor={}tweet={}&retweet={}" # username, tweet_id, retweet_id
NEW_TWEET_MESSAGE = "type=new_tweet&actor={}&tweet={}" # username, tweet_id
