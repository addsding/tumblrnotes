import pytumblr
import heapq

# Authenticate via OAuth
client = pytumblr.TumblrRestClient(
    # your keys here
)

"""
Lists for all of the types of posts.
"""
text_list = []
photo_list = []
video_list = []
chat_list = []
quote_list = []
audio_list = []
link_list = []
answer_list = []

"""
Dictionaries for all types of posts.
"""
text_dict = {}
photo_dict = {}
video_dict = {}
chat_dict = {}
quote_dict = {}
audio_dict = {}
link_dict = {}
answer_dict = {}

"""
List that keeps track of reblog keys of the final posts.
"""
reblog_keys = []

"""
List that keeps track of the URLs of the final posts.
"""
printed_urls = []

"""
Finds the post type of the given post.

:param post: the post that the user wants the type from

:returns: String that tells the user what type of post it is
"""


def post_type(post):
    return post['type']


"""
Gives the corresponding list or dictionary depending on what the post type is.

:param post: the post that the user wants to find its corresponding list/dict for
:param lib: 1 = list, 2 = dictionary

:returns: the correct list/dict for the given post
"""


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


"""
Goes through the given blog's posts and puts its entries into a list depending on what type of post it is

:param b: the blog username

:returns: a list of all of the post list types
"""


def categorize_posts(b):
    posts = b['posts']
    for p in posts:
        correct_lib(p, 1).append(p)
    post_list = [text_list, photo_list, quote_list, link_list, chat_list, audio_list, video_list, answer_list]
    return post_list


"""
Determines if the given post is an original post. If a post is original, it satisfies one of these restraints:
- its username is present in the field, 'source_url'
- its 'reblog_key' is not present in the list 'reblog_keys'
- its username is present in the 'trail' field for the post

:param post: the post that is trying to be identified as original or not
:param blog: the blog username/URL

:returns: True = the post is an original, False = the post is not an original
"""


def is_original(post, blog):
    t = post_type(post)
    if t == 'text' or t == 'link' or t == 'audio' or t == 'video' or t == 'photo' or t == 'answer':
        trail = post['trail']
        if len(trail) == 0:
            if t == 'photo' or t == 'text':
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


"""
Goes through the blog's posts and puts only original posts into its proper dictionary.
key = the post's short_url, value = note count

:param posts: the blog's posts

:returns: a list of all of the dictionaries
"""


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
    dict_list = [text_dict, photo_dict, link_dict, chat_dict, audio_dict, quote_dict, video_dict, answer_dict]
    return dict_list


"""
Goes through a dictionary and puts the items into a max heap while maintaining both the value and key of each entry.

:param d: the dictionary that needs to be changed into a max heap

:returns: the max heap
"""


def dict_to_heap(d):
    heap = [(-value, key) for key, value in d.items()]
    return heap


"""
Given a list of dictionaries, merges all of them into one dictionary.

:param dicts: the list of dictionaries that needs to be combined into one

:returns: one dictionary containing all of the keys and values of all the ones in the previous list
"""


def merge_dicts(dicts):
    results = {}
    for dictionary in dicts:
        results.update(dictionary)
    return results


"""
Finds the top __ original posts, the number specified by the user.

:param blog: the blog's username/URL
:param filters: list of filters with Strings representing post types desired
:param offset: the number where the function is to begin pulling posts from the blog

:returns the dictionary of posts
"""


def main_helper(blog, filters, offset):
    if len(filters) == 0:
        blog_posts = client.posts(blog, limit=50, offset=offset)
        posts_lists = categorize_posts(blog_posts)
        for post_types in posts_lists:
            posts_dicts = organize_posts(post_types)
            final_dict = merge_dicts(posts_dicts)
        return final_dict
    else:
        for f in filters:
            blog_posts = client.posts(blog, limit=50, offset=offset, filter=f)
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
                        dicts_list.append(posts_dicts[4])
                    elif f == 'quote':
                        dicts_list.append(posts_dicts[5])
                    else:
                        dicts_list.append(posts_dicts[6])
        final_dict = merge_dicts(dicts_list)
        return final_dict


"""
Executes main function.
:param args: [0] = blog username/URL
             [1] = list of filters, Strings

:returns: prints the top posts by note count
"""

def main(args):
    blog_name = args[0]
    filters = args[1]
    post_number = client.blog_info(blog_name)['blog']['total_posts']
    count = 0  # counter for how many posts have been done in the initial pull
    posts = 1  # counter for how many posts have been reported
    if post_number > 50:  # only 50 posts can be pulled at a time
        final_dict = {}
        while count < post_number:
            first_dict = main_helper(blog_name, filters, count)
            final_dict = merge_dicts([first_dict, final_dict])
            count += 50
        results = dict_to_heap(final_dict)
        largest = heapq.nsmallest(len(results), results)
        for post in largest:
            url = str(post[1].split(',')[0])
            if url in printed_urls:  # checks if the post is already reported; happens when posts are reblogged twice
                continue
            p_type = str(post[1].split(',')[1])
            note_count = -post[0]
            print(str(posts) + '. ' + p_type.capitalize() + ' post: URL = {} with {} notes.'.format(url, note_count))
            posts += 1
            printed_urls.append(url)
            if posts > 5:
                break
    else:
        results = main_helper(blog_name, filters, post_number, 0)
        largest = heapq.nsmallest(len(results), results)
        for post in largest:
            url = str(post[1].split(',')[0])
            if url in printed_urls:
                continue
            p_type = str(post[1].split(',')[1])
            note_count = -post[0]
            print(str(posts) + '. ' + p_type.capitalize() + 'post: URL = {} with {} notes.'.format(url, note_count))
            posts += 1
            printed_urls.append(url)
            if posts > 5:
                break
