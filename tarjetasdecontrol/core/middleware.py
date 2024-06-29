# core/middleware.py

import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect

class AutoLogoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        max_idle_time = getattr(settings, 'AUTO_LOGOUT_DELAY', 10)  # minutos
        now = datetime.datetime.now()
        
        last_activity = request.session.get('last_activity')
        
        if last_activity:
            elapsed_time = (now - datetime.datetime.fromisoformat(last_activity)).total_seconds() / 60
            if elapsed_time > max_idle_time:
                logout(request)
                return redirect('login')  # Redirigir a la página de login después de logout

        request.session['last_activity'] = now.isoformat()
