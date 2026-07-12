from rest_framework.throttling import SimpleRateThrottle


class ApplyRateThrottle(SimpleRateThrottle):
    scope = "apply"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return self.cache_format % {"scope": self.scope, "ident": request.user.pk}
        return None
