#add imports

def save_token(request, authenticator):
    user_id = request.user.id
    session = request.session.get('_auth_user_id')
    if int(user_id) == int(session):
        #check for token expiration
        request.session['_sp_auth_token'] = authenticator.get_cached_token()
        sptoken = request.session['_sp_auth_token']
    else:
        request.session['_sp_auth_token'] = None
        sptoken = request.session['_sp_auth_token']