# core/utils.py
def keyword_verify(post):
    keywords = ['clean', 'plant', 'donate', 'help', 'volunteer',
                'blood', 'tree', 'food', 'education', 'health', 'recycle']
    caption_lower = post.caption.lower()
    found = [kw for kw in keywords if kw in caption_lower]
    if len(found) >= 2:
        return {'is_authentic': True, 'score': 0.8, 'status': 'verified', 'details': {'keywords': found}}
    elif len(found) >= 1:
        return {'is_authentic': True, 'score': 0.6, 'status': 'verified', 'details': {'keywords': found}}
    else:
        return {'is_authentic': False, 'score': 0.2, 'status': 'flagged', 'details': {'keywords': []}}