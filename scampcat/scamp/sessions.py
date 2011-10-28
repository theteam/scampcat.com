def set_scamp_session(request, scamp):
    """Sets the applicable session key 
    """
    # Each Scamp has a unique UID in the form of a scamp_key,
    # if the user is meant to have editing rights to this scamp
    # then we add that key to their `scamp_key` session key. That
    # way we can provide anonymous editing without the need for
    # registration.
    if request.session.get('scamp_key'):
        request.session['scamp_key'].append(scamp.key)
    else:
        # We start a list, so we can append multiple
        # in the future.
        request.session['scamp_key'] = [scamp.key]
    return True
