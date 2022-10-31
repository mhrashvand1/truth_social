from djoser.email import (
    ActivationEmail as BaseActivationEmail,
    ConfirmationEmail as BaseConfirmationEmail, 
    PasswordResetEmail as BasePasswordResetEmail,
    PasswordChangedConfirmationEmail as BasePasswordChangedConfirmationEmail,
    UsernameChangedConfirmationEmail as BaseUsernameChangedConfirmationEmail,
    UsernameResetEmail as BaseUsernameResetEmail
)
from config import settings


class ActivationEmail(BaseActivationEmail):
    def get_context_data(self):
        context = super().get_context_data()
        context['domain'] = getattr(settings, "FRONTEND_DOMAIN", "127.0.0.1")
        return context
    
class ConfirmationEmail(BaseConfirmationEmail):
    def get_context_data(self):
        context = super().get_context_data()
        context['domain'] = getattr(settings, "FRONTEND_DOMAIN", "127.0.0.1")
        return context
    
class PasswordResetEmail(BasePasswordResetEmail):
    def get_context_data(self):
        context = super().get_context_data()
        context['domain'] = getattr(settings, "FRONTEND_DOMAIN", "127.0.0.1")
        return context
    
class PasswordChangedConfirmationEmail(BasePasswordChangedConfirmationEmail):
    def get_context_data(self):
        context = super().get_context_data()
        context['domain'] = getattr(settings, "FRONTEND_DOMAIN", "127.0.0.1")
        return context
    
class UsernameChangedConfirmationEmail(BaseUsernameChangedConfirmationEmail):
    def get_context_data(self):
        context = super().get_context_data()
        context['domain'] = getattr(settings, "FRONTEND_DOMAIN", "127.0.0.1")
        return context
    
class UsernameResetEmail(BaseUsernameResetEmail):
    def get_context_data(self):
        context = super().get_context_data()
        context['domain'] = getattr(settings, "FRONTEND_DOMAIN", "127.0.0.1")
        return context