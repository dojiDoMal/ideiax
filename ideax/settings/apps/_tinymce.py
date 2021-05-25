from ..django._core import INSTALLED_APPS, STATIC_URL


INSTALLED_APPS.append('tinymce')

TINYMCE_SPELLCHECKER = False
TINYMCE_FILEBROWSER = False
# TINYMCE_JS_URL = '//cdn.tinymce.com/4/tinymce.min.js'
TINYMCE_JS_URL = f'{STATIC_URL}tinymce/js/tinymce/tinymce.min.js'
TINYMCE_ADDITIONAL_JS_URLS = None
TINYMCE_CSS_URL = None
TINYMCE_CALLBACKS = {}

TINYMCE_DEFAULT_CONFIG = {
    'selector': 'textarea',
    'theme': 'modern',
    'plugins': 'textpattern table code lists',
    'toolbar1': 'formatselect | bold italic underline | alignleft aligncenter alignright alignjustify '
               '| bullist numlist | outdent indent | table ',
    'contextmenu_never_use_native': True,
    'textpattern_patterns': [
        {'start': '*', 'end': '*', 'format': 'italic'},
        {'start': '**', 'end': '**', 'format': 'bold'},
        {'start': '#', 'format': 'h1'},
        {'start': '##', 'format': 'h2'},
        {'start': '###', 'format': 'h3'},
        {'start': '####', 'format': 'h4'},
        {'start': '#####', 'format': 'h5'},
        {'start': '######', 'format': 'h6'},
        {'start': '1. ', 'cmd': 'InsertOrderedList'},
        {'start': '* ', 'cmd': 'InsertUnorderedList'},
        {'start': '- ', 'cmd': 'InsertUnorderedList'}
    ],
    'menubar': False,
    'inline': False,
    'statusbar': True,
    'width': 'auto',
    'height': 360,
}
