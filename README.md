# twitter_unfollower.py
It does its job

# How it select people to unfollow

* Selects all your friends (people that you follow)
* Verify the last mentions and replies to your tweets, in range of 1 month (that can be changed)
* Verify if they followed you back
* Verify if they are "big" accounts (need to beat some threshold of followers)
or if they are verified
* The ids that match one or more of the last 3 points are excluded. The remain will be unfollowed


The multiples "types" of id's were saved on files to prevent, when testing, API sleep (10-15 minutes)


# Ruby Alternative
If you would like an alternative to this python script or just an alternative on Ruby check that:
[clean-twitter](https://github.com/bellesamways/clean-twitter)


# Infos
* If you want to contact me:<br>
  * [Twitter](https://twitter.com/iN128pkt)<br>
  * [Email](mailto:tiagodeha@protonmail.com)

* Or pay me some coffee: [Paypal](https://www.paypal.me/tigaxmt)
