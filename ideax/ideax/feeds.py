from django.contrib.syndication.views import Feed
from django.utils.translation import ugettext_lazy as _ # noqa
from martor.templatetags.martortags import safe_markdown

from .models import Comment, Idea


class CommentFeed(Feed):
    title = "ideax - " + str(_('Comments')) + ": "
    link = "/rss"
    description = str(_('Sharing ideas'))

    def items(self):
        return Comment.objects.all().order_by('-date')[:10]

    def item_title(self, item):
        return str(_('Idea'))+" #"+str(item.idea.id)+": " + item.idea.title

    def item_description(self, item):
        comment = (item.raw_comment[:200] + ' ...') if len(item.raw_comment) > 75 else item.raw_comment
        comment += '</br></br>' + str(_('Comment by: ')) + '<strong> ' + ' ' + item.author.user.username + '</strong>'
        return comment

    def item_link(self, item):
        return "/idea/" + str(item.idea.id) + "/#" + str(item.id)


class NewIdeaFeed(Feed):
    title = "ideax - "+str(_('New ideas'))
    link = "/rss"
    description = str(_('Sharing ideas'))

    def items(self):
        return Idea.objects.filter(discarded=False).order_by('-creation_date')[:10]

    def item_title(self, item):
        return str(_('Idea'))+" #"+str(item.id)+": " + item.title

    def item_description(self, item):
        return safe_markdown(item.summary)

    def item_link(self, item):
        return "/idea/"+str(item.id)
