from common.throttles import CustomBaseThrottle

class FollowThrottle(CustomBaseThrottle):
        
    def __init__(self):
        self.num_requests = 15
        self.duration = 3600  # seconds
    
    def get_cache_key(self, request, view):
        return 'throttle_%(scope)s_%(ident)s' % {
            'scope': 'follow',
            'ident': str(request.user.username)
        }
