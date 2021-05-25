from enum import Enum
from decouple import config
from django.utils.translation import ugettext_lazy as _ # noqa

class EvaluationPhase(Enum):
    """An idea could be in one of this phases of evaluation"""
    WAITING = 0
    PARCIAL = 1
    DONE = 2

class UserEditCommentsProfile(Enum):
    """The user have diferent levels of prilege to change comments"""
    MANAGER = 'manager'
    PARTIAL = 'partial'

class NotificationType(Enum):
    """Data necessary to each notification to be sended"""
    COMMENT = {"icon_class":'far fa-comment',
               "description":_("commented on idea #ID {0}"),
               "author_description":_("commented on idea #ID {0}"),
               "verb":"comment",
               "subject": _("[IdeiaX] The idea #ID {0} received a comment"),
               "message":{ 'message_pre': _("the idea "),
                            'message_midle': "", 
                            'message_pos': _("received a comment. Go to idea x to check it out.")},
               "url": '/idea/{0}/',
               "email_template": 'ideax/email.html',
               "author" : "11",
                "coauthor": "11",
                "mentionade": "00",
                "follower": "11"
               }
    EVALUATION = {"icon_class":'far fa-check-square',
                  "description":_("The Idea #ID {0} has been evaluated"),
                  "author_description":_("Your idea was evaluated"),
                  "verb":"evaluate",
                  "subject": _("[IdeiaX] The idea review #ID {0} foi realizada"),
                  "message":{ 'message_pre': _("the evaluation of the idea"),
                               'message_midle': "", 
                              'message_pos': _(".It was completed. Go to idea x to check it out.")},
                  "url": '/idea/{0}/',
                  "email_template": 'ideax/email.html',
                  "author" : "11",
                    "coauthor": "11",
                    "mentionade": "00",
                    "follower": "11" 
                }
    LIKE = {"icon_class":'far fa-thumbs-up',
            "description":_("the idea #ID {0} received a like" ),
            "author_description":_("Your idea received a like"),
            "verb":"like",
            "subject": _("[IdeaX] The idea #ID {0} received a like."),
            "message":{ 'message_pre': _("the idea"),
                        'message_midle': "", 
                        'message_pos': _("received a like. Go to idea x to check it out.")},
            "url": '/idea/{0}/',
            "email_template": 'ideax/email.html',
            "author" : "11",
            "coauthor": "11",
            "mentionade": "00",
            "follower": "01" }
    RELATIONSHIP = {"icon_class":'',    
                    "description": _("Idea #ID {0} was related to #ID {1}."),
                    "author_description":_("Idea #ID {0} was related to #ID {1}."),
                    "verb":"",
                    "subject": _("[IdeaX] The idea #ID {0} was related to another."),
                    "message":{ 'message_pre': _("the idea"),
                                'message_midle': _("was related to "), 
                                'message_pos': _(". Go to idea x to check it out.")},
                    "url": '/idea/{0}/',
                    "email_template": 'ideax/email_relationship.html',
                    "author" : "11",
                    "coauthor": "11",
                    "mentionade": "00",
                    "follower": "11" }
    IDEA_CO_AUTHOR = {"icon_class":"fas fa-plus",
                      "description":_("You're a co-author of idea #ID {0}!"),
                      "author_description":_("You're a co-author of idea #ID {0}!"),
                      "verb":"author",
                      "subject": _("[IdeiaX] You are co-authored with the idea #ID {0}"),
                       "message":{ 'message_pre': _("you have been co-authored with the idea"),
                                    'message_midle': _(" by "), 
                                    'message_pos': _(". Go to idea x to check it out.")},
                      "url": '/idea/{0}/',
                      "email_template": 'ideax/email_idea_by.html',
                      "author" : "00",
                        "coauthor": "11",
                        "mentionade": "00",
                        "follower": "00" }
    IDEA_MENTION = {"icon_class":"fas fa-at",
                    "description":_("You have been mentioned in idea #ID {0}!"),
                    "author_description":_("You have been mentioned in idea #ID {0}!"),
                    "verb":"mention",
                    "subject": _("[IdeiaX] You were mentioned in the idea #ID {0}"),
                    "message":{ 'message_pre': _("you were mentioned in the idea"),
                                'message_midle': _(" by "), 
                                'message_pos': _(". Go to idea x to check it out.")},
                    "url": '/idea/{0}/',
                    "email_template": 'ideax/email_idea_by.html',
                    "author" : "00",
                        "coauthor": "00",
                        "mentionade": "11",
                        "follower": "00" }
    PHASE = {"icon_class":'far fa-check-square',
             "description":_("Your idea #ID {0} has reached a new phase!"),
             "author_description":_("Your idea #ID {0} has reached a new phase!"),
             "verb":"phase",
             "subject": _("[IdeiaX] The idea #ID {0} has reached a new phase!"),
             "message":{ 'message_pre': _("the idea"),
                         'message_midle': "", 
                        'message_pos': _("  has changed to phase {0}. Go to idea x to check it out.")},
             "url": '/idea/{0}/',
             "email_template": 'ideax/email.html',
             "author" : "11",
                "coauthor": "11",
                "mentionade": "00",
                "follower": "11"}
    IDEA_FOLLOW = {"icon_class": 'fas fa-star',
                   "description": _("followed your idea #ID {0}"),
                   "author_description":_("followed your idea #ID {0}"),
                   "verb": "follow",
                   "subject": _("[IdeiaX] The idea #ID {0} has been followed!"),
                   "message":{ 'message_pre': _("the idea"),
                                'message_midle': "", 
                                'message_pos': _(". has been followed! Go to idea x to check it out.")},
                   "url": '/idea/{0}/',
                   "email_template": 'ideax/email.html',
                    "author" : "11",
                    "coauthor": "11",
                    "mentionade": "00",
                    "follower": "00"}
 

class Parameters(Enum):
    """General aplication parameters"""
    EMAIL_FROM = config('EMAIL_FROM', default='')
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    ADDRESS_ALIAS = config('ADDRESS_ALIAS', default='')
