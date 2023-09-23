from allauth.account.adapter import DefaultAccountAdapter
from dj_rest_auth.serializers import PasswordResetSerializer


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return f"{emailconfirmation.key}"


# Reset Password Endpoint
class CustomAllAuthPasswordResetForm(PasswordResetSerializer):
    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            # 'use_https': request.is_secure(),
            # 'from_email': 'example@yourdomain.com',
            'request': request,
            "password_reset_url": "http://transend-store.ongshak.com/",
            # here I have set my desired template to be used
            # don't forget to add your templates directory in settings to be found
            'email_template_name': 'account/email/password_reset_key_message.txt'
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)

