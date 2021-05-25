import mistune

from django.db.models import Count, Case, When, Q
from .models import Dimension, Category_Dimension, Evaluation, Idea, Comment, Follow, Relationship
from .enums import EvaluationPhase
from ..util import get_client_ip, audit
from ..users.models import UserProfile
from .enums import NotificationType
from .idea_notification import message_menager


class RelationShipHelper:

    @classmethod
    def search_ideas(cls, search_part, idea):
        result = []

        ideas = Idea.objects.filter(
            Q(authors__user__first_name__icontains=search_part) |
            Q(category__title__icontains=search_part) |
            Q(title__icontains=search_part) |
            Q(id__icontains=search_part) |
            Q(summary__icontains=search_part), discarded=False).annotate(
                count_like=Count(Case(When(popular_vote__like=True, then=1)))).order_by('-count_like')
        

        relationship = Relationship.objects.filter(idea=idea, active=True)
        remove_list = [idea]
        for relation in relationship:
            remove_list.append(relation.idea_related)

        filtered_list = RelationShipHelper.filter_ideas(ideas, remove_list)

        for idea in filtered_list:
            result.append({"id": idea.id,
                            "title": idea.title,
                            "summary": idea.summary,
                            "author": idea.author.user.first_name})
        return result
    
    @classmethod
    def filter_ideas(cls, src_list, remove_list):
        result = []
        for item in src_list:
            if item not in remove_list:
                result.append(item)
        return result

    @classmethod
    def relate(cls, idea, idea_related):
        result_one_way = Relationship.objects.filter(idea=idea, idea_related=idea_related)
        result_two_way = Relationship.objects.filter(idea=idea_related, idea_related=idea)
        if len(result_one_way) == 0 and len(result_two_way) == 0:
            relationship_one_way = Relationship()
            relationship_two_way = Relationship()
    
            relationship_one_way.idea = idea
            relationship_one_way.idea_related = idea_related
            relationship_one_way.save()

            relationship_two_way.idea = idea_related
            relationship_two_way.idea_related = idea
            relationship_two_way.save()
        
                               
    @classmethod
    def unrelate(cls, idea, idea_related):
        result_one_way = Relationship.objects.filter(idea=idea, idea_related=idea_related)
        result_two_way = Relationship.objects.filter(idea=idea_related, idea_related=idea)

        if len(result_one_way) != 0: 
            result_one_way[0].delete()   
        if len(result_two_way) != 0:
            result_two_way[0].delete()
            
    @classmethod
    def get_relationship(cls, idea):
        result = []
        relationship = Relationship.objects.filter(idea=idea, active=True)
        for relation in relationship:
            result.append({"id": relation.idea_related.id,
                "title": relation.idea_related.title,
                "summary": relation.idea_related.summary,
                "author": relation.idea_related.author.user.first_name})
        return result

    @classmethod
    def get_relationship_raw(cls, idea):
        result = []
        for item in Relationship.objects.filter(idea=idea, active=True):
            result.append(item.idea_related)
        return result

class FollowHelper:
    @classmethod
    def isfollow(cls, user, idea):
        user_profile = UserProfile.objects.get(user=user)
        result = False
        for item in Follow.objects.filter(idea_id=idea, user=user_profile):
            if item.active:
                result = True
                break
        return result

    @classmethod
    def follow(cls, user, idea):
        user_profile = UserProfile.objects.get(user=user)
        follow_list = Follow.objects.filter(idea_id=idea, user=user_profile)
        if len(follow_list) != 0:
            follow_list[0].active = True
            follow_list[0].save()
        else:
            follow = Follow()
            follow.idea = idea
            follow.user = user_profile
            follow.save()

        context = {"idea" : idea, "user" : user}
        message_menager(context, NotificationType.IDEA_FOLLOW)

    @classmethod
    def unfollow(cls, user, idea):
        user_profile = UserProfile.objects.get(user=user)
        follow_list = Follow.objects.filter(idea_id=idea, user=user_profile)
        if len(follow_list) != 0:
            follow_list[0].active = False
            follow_list[0].save()

class DimensionHelper:
    @classmethod
    def get_dimension_list(cls):
        return {'dimension_list': Dimension.objects.filter(active=True)}

class CategoryDimensionHelper:
    @classmethod
    def filter_category_dimension_list(cls, dimension):
        return Category_Dimension.objects.filter(dimension=dimension, active=True)

    @classmethod
    def delete(cls, categories):
        if len(categories) > 0:
            for category in categories:
                if category.id is not None and category.id != '':
                    category.active = False
                    category.save()

    @classmethod
    def update(cls, request, dimension, categories, deletion=[]):
        dimension.save()
        audit(request.user.username, get_client_ip(request), 'DIMENSION_SAVE', Comment.__name__, dimension.log_msg())

        for category in deletion:
            if category.id is not None and category.id != '':
                category.active = False
                category.save()
                audit(request.user.username, get_client_ip(request), 'CATEGORY_DELETE', Comment.__name__, category.log_msg())

        for category in categories:
            category.dimension_id = dimension.pk
            if category.value != "" and category.description != "":
                category.save()
                audit(request.user.username, get_client_ip(request), 'CATEGORY_SAVE', Comment.__name__, category.log_msg())

def parcial_evaluation(dimension,category=None):

    assert dimension is not None

    evaluations = None

    if category is not None:
        evaluations = Evaluation.objects.filter(dimension=dimension, category_dimension=category)
    else:
        evaluations = Evaluation.objects.filter(dimension=dimension)

    for evaluation in evaluations:
        if evaluation.idea.evaluated == EvaluationPhase.PARCIAL.value:
            return True
    return False

def update_evaluation_phase(idea):
    idea_evaluation=idea.evaluation_set.all().order_by('dimension__id')

    if len(idea_evaluation) > 0 and idea.evaluated == EvaluationPhase.WAITING:
        if len(list(filter(lambda evaluation: evaluation.category_dimension is None, idea_evaluation))) > 0:
            idea.evaluated = EvaluationPhase.PARCIAL
        else:
            idea.evaluated = EvaluationPhase.DONE
        idea.save()

class CommentsHelper:
    @classmethod
    def delete_comment(cls, request, comment_id):
        comment = Comment.objects.get(id=comment_id)
        sons = Comment.objects.filter(parent_id=comment_id)
        for son in sons:
            CommentsHelper.delete_comment(request, son.id)
        comment.deleted = True
        comment.save()
        audit(request.user.username, get_client_ip(request), 'COMMENT_DELETE', Comment.__name__, comment.log_msg())

    @classmethod
    def update_comment(cls, request, comment_id, new_text):
        comment = Comment.objects.get(id=comment_id)
        msg_before = comment.log_msg()
        comment.raw_comment = mistune.markdown(new_text)
        comment.edited = True
        comment.save()
        msg_after = comment.log_msg()
        audit(request.user.username, get_client_ip(request), 'COMMENT_UPDATE_BEFORE', Comment.__name__, msg_before)
        audit(request.user.username, get_client_ip(request), 'COMMENT_UPDATE_AFTER', Comment.__name__, msg_after)

    @classmethod
    def comments_id_user(cls, user, comments):
        user_comments = filter(lambda comment: comment.author.user == user, comments)
        result = list(map(lambda comment: comment.pk, user_comments))
        result = str(result).replace("[", "").replace("]", "")
        return result

def is_same_author(user, idea):
    user_profile = UserProfile.objects.get(user=user)
    return idea.author.user == user
