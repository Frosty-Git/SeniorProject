from django.shortcuts import render, redirect, get_object_or_404
from social_feed.models import *
from social_feed.forms import *

# Create your views here.
# def share_song(request, id):
#     """
#     """

def display_posts(request):
    """
    Displays all posts in the database. Based only on users your follow and
    yourself.
    Last updated: 3/17/21 by Jacelynn Duranceau, Katie Lee, Marc Colin, Joe Frost
    """
    all_post_list = Post.objects.order_by('-date_created')

    you = UserProfile.objects.get(pk=request.user.id)
    following = you.users_followed.all()

    post_list = []

    for post in all_post_list:
        if post.user_profile_fk == you:
            post_list.append(post)
        for user in following:
            if post.user_profile_fk == user:
                post_list.append(post)

    comment_list = Comment.objects.order_by('date_created')
    postform = PostForm()

    context = {
        'post_list': post_list,
        'comment_list': comment_list,
        'postform': postform, 
    }  
    return render(request, 'social_feed/posts.html', context)

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
    return render(request, 'social_feed/comment_post.html', context)

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
            post.date_last_updated = datetime.datetime.now()
            post.save()
        return redirect('/user/profile/' + str(request.user.id))
    else:
        return render(request, 'social_feed/edit_post.html')


def popup_post(request):
    """
    """
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = Post.objects.get(pk=post_id)
        user_id = request.user.id
        user = UserProfile.objects.get(pk=user_id)
        text = request.POST.get('comment_text')
        if text is not None:
            comment = Comment(text=text, post_fk = post, user_profile_fk=user)
            comment.save()
        return redirect('/user/profile/' + str(request.user.id))
    else:
        return render(request, 'social_feed/popup_post.html')