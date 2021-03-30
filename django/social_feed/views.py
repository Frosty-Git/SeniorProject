from django.shortcuts import render, redirect, get_object_or_404
from social_feed.models import *
from social_feed.forms import *
from user_profile.models import *
from django.utils import timezone
from django.db.models.functions import Cast
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from recommender.Scripts.search import get_audio_features
import numpy as np
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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
    return redirect('/user/profile/' + str(post.user_profile_fk.user.id))
    

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
    Last updated: 3/30/21 by Marc Colin, Katie Lee
    """
    post_id = request.POST.get('post_id')
    action = request.POST.get('action')
    user = UserProfile.objects.get(pk=request.user.id)
    if post_id and action:
        post = Post.objects.get(pk=post_id)
        type_post = post.type_post
        if action == 'like':
            vote = PostUserVote.objects.filter(user_from=user, post_to=post).first()
            if vote is None:
                up = PostUserVote(user_from=user, post_to=post, vote="Like")
                up.save()
                if type_post == 'SongPost':
                    songpost = SongPost.objects.get(pk=post_id)
                    change_prefs_songpost(songpost.song, user, "like")
                post.upvotes += 1
                post.save()
                return JsonResponse({'status':'ok'})
            else:
                if vote.vote == 'Dislike':
                    if type_post == 'SongPost':
                        songpost = SongPost.objects.get(pk=post_id)
                        change_prefs_songpost(songpost.song, user, "like")
                    vote.vote = 'Like'
                    post.upvotes += 2
                    post.save()                                    
                    return JsonResponse({'status':'switch'}) 
                else:
                    vote.delete()
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
        type_post = post.type_post
        if action == 'dislike':
            vote = PostUserVote.objects.filter(user_from=user, post_to=post).first()
            if vote is None:
                down = PostUserVote(user_from=user, post_to=post, vote="Dislike")
                down.save()
                if type_post == 'SongPost':
                    songpost = SongPost.objects.get(pk=post_id)
                    change_prefs_songpost(songpost.song, user, "dislike")
                post.upvotes -= 1
                post.save()
                return JsonResponse({'status':'ok'})
            else:
                if vote.vote == 'Like':
                    if type_post == 'SongPost':
                        songpost = SongPost.objects.get(pk=post_id)
                        change_prefs_songpost(songpost.song, user, "dislike")
                    vote.vote = 'Dislike'
                    post.upvotes -= 2
                    post.save()                                       
                    return JsonResponse({'status':'switch'}) 
                else:
                    vote.delete()
                    post.upvotes += 1
                    post.save()
                    return JsonResponse({'status':'undo_downvote'})
    return JsonResponse({'status':'ko'})
    
    
def change_prefs_songpost(track, profile, type_vote):
    """
    Change the preferences for a user after they like or dislike a song.
    Last updated: 3/29/21 Katie Lee, Marc Colin, Jacelynn Duranceau
    """
    features = get_audio_features([track])
    prefs = Preferences.objects.get(user_profile_fk=profile.user.id)
    song_pref = features[0]

    pref_list =[]
    pref_list.append(prefs.danceability)
    pref_list.append(prefs.tempo)
    pref_list.append(prefs.energy)
    pref_list.append(prefs.instrumentalness)
    pref_list.append(prefs.loudness)
    pref_list.append(prefs.valence)
    pref_list.append(prefs.speechiness)
    pref_list.append(prefs.acousticness)

    song_features = []
    song_features.append(song_pref.get('danceability'))
    song_features.append(song_pref.get('tempo'))
    song_features.append(song_pref.get('energy'))
    song_features.append(song_pref.get('instrumentalness'))
    song_features.append(song_pref.get('loudness'))
    song_features.append(song_pref.get('valence'))
    song_features.append(song_pref.get('speechiness'))
    song_features.append(song_pref.get('acousticness'))

    changes = []
    index_of_max = 0
    count = 0
    # Default array
    max = [[-1,0,-1,0]]
    for feature, pref in zip(song_features, pref_list):
        diff = percent_diff(feature, pref)
        absdiff = abs(diff)

        if absdiff < 5:
            percent = 0 # We won't be making a change due to negligible difference

        elif absdiff < 20:
            percent = 0.001 if type_vote == 'dislike' else 0.0005

        elif absdiff < 40:
            percent = 0.002 if type_vote == 'dislike' else 0.001
                
        elif absdiff < 60:
            percent = 0.0025 if type_vote == 'dislike' else 0.00125
                
        elif absdiff < 80:
            percent = 0.005 if type_vote == 'dislike' else 0.0025
                
        elif absdiff < 100:
            percent = 0.0075 if type_vote == 'dislike' else 0.00375

        elif absdiff < 200:
            percent = 0.01 if type_vote == 'dislike' else 0.005

        elif absdiff < 400:
            percent = 0.025 if type_vote == 'dislike' else 0.0125

        else: # >= 400
            percent = 0.05 if type_vote == 'dislike' else 0.025
            
        change = percent * pref
        if diff > 0: # Song feature is greater than preference
            # Move farther away from the current preferences if it is a dislike,
            # Move closer if it is a like. Like moves in same direction as the
            # sign of the difference.
            value = pref - change if type_vote == 'dislike' else pref + change
        else:
            value = pref + change if type_vote == 'dislike' else pref - change
        changes.append(value)

        max_arr = max[count]
        if abs(max_arr[1]) < absdiff:
            # Reset to default array since we will override previous max
            max = [[-1,0,-1,0]]
            count = 0
            max.append([index_of_max, diff, pref, percent])
        elif abs(max_arr[1]) == absdiff:
            count += 1
            max.append([index_of_max, diff, pref, percent])
            
        index_of_max += 1
            
    for arr in max:
        index = arr[0]
        diff = arr[1]
        pref = arr[2]
        percent = arr[3]
        # Double the effect of the max difference(s) in preferences
        change = 2 * percent * pref
        if diff > 0: # Song feature is greater than preference
            # Move farther away from the current preferences if it is a dislike,
            # Move closer if it is a like. Like moves in same direction as the
            # sign of the difference.
            value = pref - change if type_vote == 'dislike' else pref + change
        else:
            value = pref + change if type_vote == 'dislike' else pref - change
        changes[index] = value

    field_min = validate_min('danceability')
    field_max = validate_max('danceability')
    if changes[0] <  field_min:
        prefs.danceability = field_min
    elif changes[0] > field_max:
        prefs.danceability = field_max
    else:
        prefs.danceability = prefs.danceability if changes[0] == 0 else changes[0]

    field_min = validate_min('tempo')
    field_max = validate_max('tempo')
    if changes[1] <  field_min:
        prefs.tempo = field_min
    elif changes[1] > field_max:
        prefs.tempo = field_max
    else:
        prefs.tempo = prefs.tempo if changes[1] == 0 else changes[1]

    field_min = validate_min('energy')
    field_max = validate_max('energy')
    if changes[2] <  field_min:
        prefs.energy = field_min
    elif changes[2] > field_max:
        prefs.energy = field_max
    else:
        prefs.energy = prefs.energy if changes[2] == 0 else changes[2]
        
    field_min = validate_min('instrumentalness')
    field_max = validate_max('instrumentalness')
    if changes[3] <  field_min:
        prefs.instrumentalness = field_min
    elif changes[3] > field_max:
        prefs.instrumentalness = field_max
    else:
        prefs.instrumentalness = prefs.instrumentalness if changes[3] == 0 else changes[3]
    
    field_min = validate_min('loudness')
    field_max = validate_max('loudness')
    if changes[4] <  field_min:
        prefs.loudness = field_min
    elif changes[4] > field_max:
        prefs.loudness = field_max
    else:
        prefs.loudness = prefs.loudness if changes[4] == 0 else changes[4]
    
    field_min = validate_min('valence')
    field_max = validate_max('valence')
    if changes[5] <  field_min:
        prefs.valence = field_min
    elif changes[5] > field_max:
        prefs.valence = field_max
    else:
        prefs.valence = prefs.valence if changes[5] == 0 else changes[5]
    
    field_min = validate_min('speechiness')
    field_max = validate_max('speechiness')
    if changes[6] <  field_min:
        prefs.speechiness = field_min
    elif changes[6] > field_max:
        prefs.speechiness = field_max
    else:
        prefs.speechiness = prefs.speechiness if changes[6] == 0 else changes[6]
    
    field_min = validate_min('acousticness')
    field_max = validate_max('acousticness')
    if changes[7] <  field_min:
        prefs.acousticness = field_min
    elif changes[7] > field_max:
        prefs.acousticness = field_max
    else:
        prefs.acousticness = prefs.acousticness if changes[7] == 0 else changes[7]
    
    prefs.save()
        
        
def validate_min(field):
    """
    Will check the minimum allowed value for a field within the Preferences
    model.
    Last updated: 3/29/21 by Marc Colin, Katie Lee, Jacelynn Duranceau
    """
    min = Preferences._meta.get_field(field).validators[0].limit_value
    return min

def validate_max(field):
    """
    Will check the maximum allowed value for a field within the Preferences
    model.
    Last updated: 3/29/21 by Marc Colin, Katie Lee, Jacelynn Duranceau
    """
    max = Preferences._meta.get_field(field).validators[1].limit_value
    return max

def percent_diff(a, b):
    """
    Calculates the percent difference between two numbers
    Last updated: 3/29/21 by Marc Colin, Jacelynn Duranceau, Katie Lee
    """
    percent_diff = ((a - b)/b) * 100
    return percent_diff