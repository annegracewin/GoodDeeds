# core/utils.py
# core/utils.py

def keyword_verify(post):
    keywords = ['clean', 'plant', 'donate', 'help', 'volunteer',
                'blood', 'tree', 'food', 'education', 'health', 'recycle']
    caption_lower = post.caption.lower()
    found = [kw for kw in keywords if kw in caption_lower]
    unique_keywords = list(set(found))  # Remove duplicates
    count = len(unique_keywords)
    
    if count >= 2:
        return {
            'is_authentic': True,
            'score': 0.8,
            'status': 'verified',
            'details': {'keywords': unique_keywords}
        }
    elif count >= 1:
        return {
            'is_authentic': True,
            'score': 0.6,
            'status': 'verified',
            'details': {'keywords': unique_keywords}
        }
    else:
        return {
            'is_authentic': False,
            'score': 0.2,
            'status': 'flagged',
            'details': {'keywords': []}
        }