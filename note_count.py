import pytumblr
import heapq

# Authenticate via OAuth
client = pytumblr.TumblrRestClient(
  '878eRiHOu9LXg2pvQUsrfy7Tn835NOo4czF50LwUcuYZvDnV5m',
  'dkCQzKZNCzHTkHDWHaccUL1JwvwprVu9eBo3n1Cp1sL9T0c5GM',
  'g1CgrMV5xapDp0vwb6fX32xtdVY1ChGN018jFhhIeG127ib7MW',
  'xhzj13w4pExGyr4b2zkvpGyJVyQseMr4qkt5YrTVVd7FuTGx2u'
)

text_list = []
photo_list = []
video_list = []
chat_list = []
quote_list = []
audio_list = []
link_list = []
answer_list = []

text_dict = {}
photo_dict = {}
video_dict = {}
chat_dict = {}
quote_dict = {}
audio_dict = {}
link_dict = {}
answer_dict = {}

reblog_keys = []

# returns the post type of the given post
def post_type(post):
	return post['type']

# gives the corresponding list or dictionary depending on what the post type is
def correct_lib(post, lib):
	t = post_type(post)
	if t == 'text':
		if lib == 1:
			return text_list
		else:
			return text_dict
	elif t == 'photo':
		if lib == 1:
			return photo_list
		else:
			return photo_dict
	elif t == 'video':
		if lib == 1:
			return video_list
		else:
			return video_dict
	elif t == 'chat':
		if lib == 1:
			return chat_list
		else:
			return chat_dict
	elif t == 'audio':
		if lib == 1:
			return audio_list
		else:
			return audio_dict
	elif t == 'quote':
		if lib == 1:
			return quote_list
		else:
			return quote_dict
	elif t == 'answer':
		if lib == 1:
			return answer_list
		else:
			return answer_dict
	else:
		if lib == 1:
			return link_list
		else:
			return link_dict

# goes through the given blog's posts and puts entries into a list depending on what type of post it is
def categorize_posts(b): 
	posts = b['posts']
	for p in posts:
		correct_lib(p, 1).append(p)
	post_list = [text_list, photo_list, quote_list, link_list, chat_list, audio_list, video_list]
	return post_list

# determines if the given post is an original by looking at its trail and comparing the blog name to the given blog_name
def is_original(post, blog):
	t = post_type(post)
	if t == 'text' or t == 'link' or t == 'audio' or t == 'video' or t == 'photo':
		trail = post['trail']
		if len(trail) == 0:
			if t == 'photo':
				try:
					source_url = post['source_url']
					first_split = source_url.split('/')
					link = first_split[2].split('.')
					if link == post['blog_name']:
						return True
					else:
						return False
				except KeyError:
					return True 
			else:
				return True
		if t == 'answer':
			reblog_key = post['reblog_key']
			return not reblog_key in reblog_keys
		elif trail[0]['blog']['name'] == blog:
			if t == 'text' and post['reblog_key'] not in reblog_keys:
				return True
			else:
				return False
 		else: 
 			return False

# goes through the blog's posts and puts original posts into its proper dictionary with the post's short_url and note count
# returns the list of dictionaries
def organize_posts(posts):
	for p in posts:
		t = post_type(p)
		blog = p['blog_name']
		if is_original(p, blog):
			url = p['short_url']
			key = str(url) + ',' + str(t)
			note_count = p['note_count']
			reblog_key = p['reblog_key']
			dictionary = correct_lib(p, 2)
			dictionary[key] = note_count
			reblog_keys.append(reblog_key)
	dict_list = [text_dict, photo_dict, link_dict, chat_dict, audio_dict, quote_dict, video_dict]
	return dict_list

# goes through a dictionary and puts the items into a max heap for each 
def dict_to_heap(d):
	heap = [(-value, key) for key,value in d.items()]
	largest = heapq.nsmallest(5, heap)
	return largest

# given a list of dictionaries, merges all of them into one dictionary
def merge_dicts(dicts):
    results = {}
    for dictionary in dicts:
        results.update(dictionary)
    return results

# does the actual function of finding the top 5 original posts given the filters
def main_helper(blog, filters, post_count, offset):
	if len(filters) == 0:
		blog_posts = client.posts(blog, limit=post_count)
		posts_lists = categorize_posts(blog_posts)
		for post_types in posts_lists:
			posts_dicts = organize_posts(post_types)
			final_dict = merge_dicts(posts_dicts)
			results = dict_to_heap(final_dict)
			return results
	else:
		for f in filters:
			blog_posts = client.posts(blog, limit=post_count, filter=f)
			posts_lists = categorize_posts(blog_posts)
			for post_types in posts_lists:
				posts_dicts = organize_posts(post_types)
				for post_types in posts_dicts:
					dicts_list = []
					if f == 'text':
						dicts_list.append(posts_dicts[0])
					elif f == 'photo':
						dicts_list.append(posts_dicts[1])
					elif f == 'link':
						dicts_list.append(posts_dicts[2])
					elif f == 'chat':
						dicts_list.append(posts_dicts[3])
					elif f == 'audio':
						dicts_list.append(posts_dcts[4])
					elif f == 'quote':
						dicts_list.append(posts_dicts[5])
					else:
						dicts_list.append(posts_dicts[6])
		final_dict = merge_dicts(dicts_list)
		results = dict_to_heap(final_dict)
		return results
			
# the main function
# blog = tumblr blog username
# post_amount = amount of posts that the blog has
# filter = what type of posts the user wants to consider
def main(args):
	blog_name = args[0]
	filters = args[1]
	post_number = client.blog_info(blog_name)['blog']['total_posts']
	count = 0
	posts = 0
	if post_number > 50:
		while count < post_number:
			results = main_helper(blog_name, filters, post_number, count)
			count += 50
		for post in results:
			post_number = str(count)
			key = post[1]
			url = str(key.split(',')[0])
			p_type = str(key.split(',')[1])
			note_count = -post[0]
			print(str(posts + 1) + '. ' + p_type.capitalize() + ' post: URL = {} with {} notes.'.format(url, note_count))
			posts += 1
	else:
		results = main_helper(blog_name, filters, post_number, 0)
		for post in results:
			post_number = str(count)
			url = post[1]
			note_count = -post[0]
			print(str(posts + 1) + '. ' + p_type.capitalize() + 'post: URL = {} with {} notes.'.format(url, note_count))
			posts += 1
				

#main(['kimjonginxx', []])
blog_name = 'kimjonginxx'
post_count = client.blog_info(blog_name)['blog']['total_posts']
print post_count
blog = client.posts(blog_name)
print answer_dict