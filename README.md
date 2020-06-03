# twitter_unfollower.py
It does its job

# How it select people to unfollow

* Selects all your friends (people that you follow)
* Verify the last mentions and replies to your tweets, in range of 1 month (that can be changed)
* Verify if they followed you back
* Verify if they are "big" accounts (need to beat some threshold of followers)
or if they are verified
* The ids that match one or more of the last 3 points are excluded. The remain will be unfollowed

# What do you need
* A Twitter Developer account and an created app with write and read privileges
* Replace the Keys and Tokens on the code for the ones you generated on your app
* Replaced the `account_name` value for your account name
