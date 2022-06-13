AUTHOR_USERNAME = 'TestName'
GROUP_SLUG = 'TestSlug'

URL_INDEX = reverse('posts:index')
URL_PROFILE = reverse('posts:profile', args=[AUTHOR_USERNAME])
URL_GROUP_LIST = reverse('posts:group_list', args=[GROUP_SLUG])
URL_CREATE_POST = reverse('posts:post_create')
