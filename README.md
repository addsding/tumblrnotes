# tumblrnotes
Finds the 'original' posts with the most notes from a single blog.

Notes are either:
- reblogs
- likes

'Original' in this case is if:
- the blog's username is present in the field, 'source_url'
- the blog's 'reblog_key' is not present in the list 'reblog_keys'
- the blog's username is present in the 'trail' field for the post

In other words, this blog is the /true/ source of  this post; it should not have been reblogged by anyone else to be present on this blog and this user is the owner of that post.
