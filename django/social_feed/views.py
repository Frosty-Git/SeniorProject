from django.shortcuts import render, redirect, get_object_or_404
from social_feed.models import *
from social_feed.forms import *
from django.utils import timezone
from django.db.models.functions import Cast
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse

# Create your views here.
# def share_song(request, id):
#     """
#     """
# comment to check if commit is working


def display_posts(request):
    """
    Displays all posts in the database. Based only on users your follow and
    yourself.
    Last updated: 3/17/21 by Jacelynn Duranceau, Katie Lee, Marc Colin, Joe Frost
    """
    all_post_list = Post.objects.order_by('-date_last_updated')
    you = UserProfile.objects.get(pk=request.user.id)
    following = you.users_followed.all()
    upvotes = PostUserUpvote.objects.filter(user_from=you).values()
    downvotes = PostUserDownvote.objects.filter(user_from=you).values()

    post_list = feed_vote_dictionary(upvotes, downvotes, all_post_list, you, following)
    comment_list = Comment.objects.order_by('date_last_updated')
    postform = PostForm()

    context = {
        'post_list': post_list,
        'comment_list': comment_list,
        'postform': postform,
    }  
    return render(request, 'social_feed/feed.html', context)

def feed_vote_dictionary(upvotes, downvotes, posts, you, following):
    """
    """
    post_list = {}
    for post in posts:
        new_post = cast_subclass(post)
        if post.user_profile_fk == you:
            up = False
            down = False
            for upvote in upvotes:
                if upvote.get('post_to_id') == post.id:
                    up = True
            
            for downvote in downvotes:
                if downvote.get('post_to_id') == post.id:
                    down = True
            post_list[new_post] = [up, down]

        for user in following:
            if post.user_profile_fk == user:
                up = False
                down = False
                for upvote in upvotes:
                    if upvote.get('post_to_id') == post.id:
                        up = True
                
                for downvote in downvotes:
                    if downvote.get('post_to_id') == post.id:
                        down = True
                post_list[new_post] = [up, down]
    return post_list


def cast_subclass(post):
    """
    Gets the SongPost instead of Post.
    Last updated: 3/21/21 by Marc Colin, Katie Lee
    """
    try:
        return SongPost.objects.get(id=post.id)
    except:
        return post

def create_post(request):
    """
    Creates a post. Redirects to the feed, which is where it will show up.
    Last updated: 3/17/21 by Jacelynn Duranceau, Katie Lee, Marc Colin, Joe Frost
    """
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.text = form.cleaned_data.get('text')
            post.user_profile_fk = UserProfile.objects.get(pk=request.user.id)
            post.save()
    return redirect('/feed/')

def create_post_profile(request):
    """
    Creates a post. Redirects to the profile.
    Last updated: 3/23/21 by Katie Lee
    """
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.text = form.cleaned_data.get('text')
            post.user_profile_fk = UserProfile.objects.get(pk=request.user.id)
            post.save()
    return redirect('/user/profile/' + str(request.user.id))



def delete_post(request, post_id):
    """
    Deletes a post and redirects back to profile.
    This will only show up for the logged in user's profile.
    Last updated: 3/18/21 by Katie Lee
    """
    post = Post.objects.get(pk=post_id)
    post.delete()
    return redirect('/user/profile/' + str(request.user.id))

def create_comment(request, post_id):
    """
    Creates a comment on a particular post.
    Last updated: 3/19/21 by Katie Lee, Joseph Frost, Jacelynn Duranceau
    """
    if request.method == "POST":
        form = CommentForm(request.POST)
        post = get_object_or_404(Post, id=post_id)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.text = form.cleaned_data.get('text')
            comment.post_fk = post
            user = UserProfile.objects.get(pk=request.user.id)
            comment.user_profile_fk = user
            comment.save()
            url = '/feed/' + post_id
            return redirect(url)
    else:
        context = get_comments(post_id)
    return render(request, 'social_feed/post_detail.html', context)

def get_comments(post_id):
    """
    Gets all the comments on a particular post.
    Last updated: 3/19/21 by Katie Lee, Joseph Frost, Jacelynn Duranceau
    """
    post = Post.objects.get(id=post_id)
    comment_list = Comment.objects.filter(post_fk=post)
    comment_form = CommentForm()

    context = {
        'post_id': post_id,
        'post': post,
        'comment_list': comment_list,
        'comment_form': comment_form, 
    }  
    return context
 

def delete_comment(request, comment_id):
    """
    """
    comment = Comment.objects.get(pk=comment_id)
    comment.delete()
    return redirect('/feed/')


def update_comment(request):
    """
    Updates a comment on the feed.
    Last updated: 3/20/21 by Katie Lee
    """
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        comment_id = request.POST.get('comment_id')
        comment = Comment.objects.get(pk=comment_id)
        text = request.POST.get('new_text')
        if text is not None:
            comment.text = text
            comment.date_last_updated = timezone.now()
            comment.save()
        return redirect('/feed/' + str(post_id))
    else:
        return render(request, 'social_feed/edit_post.html')

def create_songpost(request, track_id):
    """
    Called when a user clicks the share button on a song. Will create a song post
    that the user can share to the feed.
    Last updated: 3/19/21 by Katie Lee, Jacelynn Duranceau
    """
    if request.method == 'POST':
        postform = PostForm(request.POST)
        if form.is_valid():
            songpost = SongPost(song=track_id)
            form = postform.save(commit=False)
            songpost.text = form.cleaned_data.get('text')
            songpost.user_profile_fk = UserProfile.objects.get(pk=request.user.id)
            songpost.save()
            return redirect('/')
    else:
        postform = PostForm()
        return render(request, '', {'postform': postform})

def update_post(request):
    """
    Updates a post on the profile. 
    Last updated: 3/20/21 by Katie Lee
    """
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = Post.objects.get(pk=post_id)
        text = request.POST.get('new_text')
        if text is not None:
            post.text = text
            post.date_last_updated = timezone.now()
            post.save()
        return redirect('/user/profile/' + str(request.user.id))
    else:
        return render(request, 'social_feed/edit_post.html')


def popup_post(request, post_id):
    """
    Creates a popup post for the profile and user profile.
    Last updated: 3/22/21 by Katie Lee
    """
    post = Post.objects.get(pk=post_id)
    user_id = request.user.id
    user = UserProfile.objects.get(pk=user_id)
    if request.method == 'POST':
        text = request.POST.get('comment_text')
        if text is not None:
            comment = Comment(text=text, post_fk=post, user_profile_fk=user)
            comment.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'ko'})

    if post.user_profile_fk.user.id == user_id:
        return redirect('/user/profile/' + str(request.user.id))
    else:
        return redirect('/user/userprofile/' + str(post.user_profile_fk.user.id))
    


def popup_songpost(request):
    """
    """
    if request.method == 'POST':
        user_id = request.user.id
        user = UserProfile.objects.get(pk=user_id)
        text = request.POST.get('post_text')
        track = request.POST.get('track_id')
        if text is not None:
            song = SongPost(song=track, text=text, user_profile_fk=user, type_post="SongPost")
            song.save()
            return redirect('/feed/')
    else:
        return render(request, 'social_feed/popup_songpost.html')


def upvote(request):
    """
    Counts upvotes for posts
    Last updated: 3/22/21 by Marc Colin, Katie Lee
    """
    post_id = request.POST.get('post_id')
    action = request.POST.get('action')
    user = UserProfile.objects.get(pk=request.user.id)
    if post_id and action:
        post = Post.objects.get(pk=post_id)
        if action == 'like':
            upvote = PostUserUpvote.objects.filter(user_from=user, post_to=post).first()
            downvote = PostUserDownvote.objects.filter(user_from=user, post_to=post).first()
            if upvote is None:
                up = PostUserUpvote(user_from=user, post_to=post)
                up.save()
                if downvote is not None:
                    downvote.delete()
                    post.upvotes += 2
                    post.save()
                    return JsonResponse({'status':'switch'})
                else:
                    post.upvotes += 1
                    post.save()
                    return JsonResponse({'status':'ok'})
            else:
                upvote.delete()
                post.upvotes -= 1
                post.save()
                return JsonResponse({'status':'undo_upvote'})
    return JsonResponse({'status':'ko'})

def downvote(request):
    """
    Counts downvotes for posts
    Last updated: 3/22/21 by Marc Colin, Katie Lee
    """
    post_id = request.POST.get('post_id')
    action = request.POST.get('action')
    user = UserProfile.objects.get(pk=request.user.id)
    if post_id and action:
        post = Post.objects.get(pk=post_id)
        if action == 'dislike':
            down_list = PostUserDownvote.objects.filter(user_from=user, post_to=post).first()
            up_list = PostUserUpvote.objects.filter(user_from=user, post_to=post).first()
            if down_list is None:
                downvote = PostUserDownvote(user_from=user, post_to=post)
                downvote.save()
                if up_list is not None:
                    up_list.delete()
                    post.upvotes -= 2
                    post.save()
                    return JsonResponse({'status':'switch'})
                else:
                    post.upvotes -= 1
                    post.save()
                    return JsonResponse({'status':'ok'})
            else:
                down_list.delete()
                post.upvotes += 1
                post.save()
                return JsonResponse({'status':'undo_downvote'})
    return JsonResponse({'status':'ko'})
    
