from tweepy import OAuthHandler, API, Cursor
import sys
import os
import concurrent.futures
import datetime

""" FOR AUTH"""

# consumer tokens
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
# tokens
access_token = "YOUR_ACCESS_TOKEN"
access_token_secret = "YOUR_ACCESS_SECRET"


""" FILENAMES"""

# Filename for each type of ids
friends_file = "ids.txt"
mentions_file = "mention_ids.txt"
friends_followers_file = "friends_followers.txt"
big_accounts_file = "big_accounts.txt"



""" CONSTANTS """

# Account name
account_name = "YOUR_ACCOUNT_NAME"

# Threshold to verify if an account has the right ammount of followers
# to classify as "Big Account"
threshold_followers = 5000

# Since date until some date (in this case 30 days)
today = datetime.date.today()
lastMonth = today - datetime.timedelta(days=30)

today = today.strftime("%Y-%m-%d")
lastMonth = lastMonth.strftime("%Y-%m-%d")



def thread_jobs(job, *args):
	""" Thread Functions """

	res = None
	with concurrent.futures.ThreadPoolExecutor() as executor:
		# *args here unpack the tuple into single arguments
		res = executor.submit(job, *args)
	
	return res.result()

def read_write_ids(filename, mode, ids=None):
	""" Function that writes a list of ids on a file"""

	# Verify if the file already exist, if not write to it and save
	if mode == "w":

		# Save the ids on a file 
		with open(filename, "w") as f:
			for idt in ids:
				f.write("%s\n" % str(idt))

	# File exists, so read it
	else:
		with open(filename, "rb") as f:
			ids = f.readlines()
			ids = [int(i) for i in ids]

		return ids

	return

def get_friends_ids(api):
	""" Just get all ids of all people that the account follow"""
	return [user.id for user in Cursor(api.friends, screen_name=account_name).items()]


def get_mention_ids(api):

	# Get ids where the account had been mentioned (range of 1 month)
	mention_ids = []
	for mentions in Cursor(api.mentions_timeline,since=lastMonth, until=today).items():
		mention_ids.append( mentions.user.id )

	# Get my last tweets and get the user ids from replies (range of 1 month)
	for tweet in Cursor(api.user_timeline, since=lastMonth, until=today).items():
		if tweet.in_reply_to_user_id != api.me().id or tweet.in_reply_to_user_id != None:
			mention_ids.append(tweet.in_reply_to_user_id)

	return mention_ids

def following_mention_ids(api, ids):
	""" 
		This function has the mention_ids and make sure if the account follow them
		if not ... don't make sense to unfollow them

		returns the ids list only with the ones that the account follow
	"""

	following_mention_ids = []
	for idt in ids:
		if api.show_friendship(source_id= idt, target_id= api.me().id)[0].followed_by:
			following_mention_ids.append(idt)

	return following_mention_ids


def friend_follows_me(api, ids):
	""" 
		This function has the friends ids and verify if they follow the account
		if yes, the script will not unfollow them

		return an list with friends following the account
	"""
	followed_me = []	
	for idt in ids:
		if api.show_friendship(source_id= idt, target_id= api.me().id)[0].following:
			followed_me.append(idt)
	
	return followed_me

def big_accounts(api, ids):
	""" Verify if an account has a lot of followers and/or is verified"""

	big_accs = []

	for idt in ids:
		usr = api.get_user(idt)

		if int(usr.followers_count) >= threshold_followers or usr.verified == True:
			big_accs.append(idt)

	return big_accs

def unfollow(api, friends_ids, not_unfollow_ids):
	""" Create a list of unique ids to unfollow """
	
	# Get all the matched ids
	not_unfollow_ids = list( set(friends_ids) & set(not_unfollow_ids) )


	# Remove the macthed ids to the list of all friends
	for idt in not_unfollow_ids:
		friends_ids.remove(idt)

	# Now we can unfollow the remaining
	for idt in friends_ids:
		api.destroy_friendship(idt)

	return 

def main():

	""" Auth """
	try:
		auth = OAuthHandler(consumer_key, consumer_secret)
		auth.secure = True
		auth.set_access_token(access_token, access_token_secret)
		api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

	except BaseException as e:
		print("Error in main()", e)
		sys.exit(1)


	""" I/O different ids"""

	# All friends/following ID's
	if os.path.exists(friends_file):
		ids = thread_jobs(read_write_ids, friends_file, "r")
	else:
		ids = thread_jobs(get_friends_ids, api)
		thread_jobs(read_write_ids, friends_file, "w", ids)

	print("Friends number: ", len(ids))

	# Get mention and reply ids
	if os.path.exists(mentions_file):
		mention_ids = thread_jobs(read_write_ids, mentions_file, "r")
	else:
		mention_ids = thread_jobs(get_mention_ids, api)
		mention_ids = thread_jobs(following_mention_ids, api, mention_ids)
		thread_jobs(read_write_ids, mentions_file, "w", mention_ids)

	print("Mention and reply number: ", len(mention_ids))

	# Get friends that follow the account too
	if os.path.exists(friends_followers_file):
		friends_followers_ids = thread_jobs(read_write_ids, friends_followers_file, "r")
	else:
		friends_followers_ids = thread_jobs(friend_follows_me, api, ids)
		thread_jobs(read_write_ids, friends_followers_file, "w", friends_followers_ids)

	print("Friends and Followers number: ", len(friends_followers_ids))

	# Get big accounts ids
	if os.path.exists(big_accounts_file):
		big_accs_ids = thread_jobs(read_write_ids, big_accounts_file, "r")
	else:
		big_accs_ids = thread_jobs(big_accounts, api, ids)
		thread_jobs(read_write_ids, big_accounts_file, "w", big_accs_ids)

	print("Big accounts number: ", len(big_accs_ids))




	""" Treat the ids """

	# Remove duplicates using set() and convert again to a list
	# All this lists have ids that are not supose to be unfollowed
	mention_ids = list( set(mention_ids) )
	friends_followers_ids = list( set(friends_followers_ids) )
	big_accs_ids = list( set(big_accs_ids) )

	# Concatenate all the ids to keep following
	not_unfollow = list( set( mention_ids + friends_followers_ids + big_accs_ids ) )
	print("People not to unfollow number: ", len(not_unfollow))


	# Now let's create a final list with only the ids to unfollow
	thread_jobs(unfollow, api, ids, not_unfollow)

if __name__ == "__main__":
	main()
