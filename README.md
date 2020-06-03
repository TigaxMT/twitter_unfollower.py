# twitter_unfollower.py
It does its job

# How it select people to unfollow

* Selects all your friends (people that you follow)
* Verify the last mentions and replies to your tweets, in range of 1 month (that can be changed)
* Verify if they followed you back
* Verify if they are "big" accounts (need to beat some threshold of followers)
or if they are verified
* The ids that match one or more of the last 3 points are excluded. The remain will be unfollowed
