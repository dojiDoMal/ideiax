import time

from ..django._core import INSTALLED_APPS


INSTALLED_APPS.extend([
    'martor',
    'markdownify',
])

# Global martor settings
# Input: string boolean, `true/false`
MARTOR_ENABLE_CONFIGS = {
    'imgur': 'true',     # to enable/disable imgur/custom uploader.
    'mention': 'true',  # to enable/disable mention
    'jquery': 'true',    # to include/revoke jquery (require for admin default django)
    'living': 'false',   # to enable/disable live updates in preview
}

# To setup the martor editor with label or not (default is False)
MARTOR_ENABLE_LABEL = True

# Imgur API Keys
MARTOR_IMGUR_CLIENT_ID = 'your-client-id'
MARTOR_IMGUR_API_KEY = 'your-api-key'

# Safe Mode
MARTOR_MARKDOWN_SAFE_MODE = True  # default

# Markdownify
MARTOR_MARKDOWNIFY_FUNCTION = 'martor.utils.markdownify'  # default
MARTOR_MARKDOWNIFY_URL = '/martor/markdownify/'  # default

# Markdown extensions (default)
MARTOR_MARKDOWN_EXTENSIONS = [
    'markdown.extensions.extra',
    'markdown.extensions.nl2br',
    'markdown.extensions.smarty',
    'markdown.extensions.fenced_code',

    # Custom markdown extensions.
    'martor.extensions.urlize',
    'martor.extensions.del_ins',    # ~~strikethrough~~ and ++underscores++
    'martor.extensions.mention',    # to parse markdown mention
    'martor.extensions.mdx_video',  # to parse embed/iframe video
]

# Markdown Extensions Configs
MARTOR_MARKDOWN_EXTENSION_CONFIGS = {}

# Markdown urls
MARTOR_UPLOAD_URL = '/media/uploader/'  # default
MARTOR_SEARCH_USERS_URL = '/martor/search-user/'  # default

# Markdown Extensions
MARTOR_MARKDOWN_BASE_MENTION_URL = '/users/profile/'  # default (change this)
MARTOR_UPLOAD_PATH = 'images/uploads/{}'.format(time.strftime("%Y/%m/%d/"))
