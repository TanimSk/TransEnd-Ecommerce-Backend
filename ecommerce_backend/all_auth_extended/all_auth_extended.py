from allauth.account.adapter import DefaultAccountAdapter


class AccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return f"{emailconfirmation.key}"


# Social Login
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from userAPI.models import Consumer


@receiver(user_signed_up)
def create_consumer_profile(request, user, **kwargs):
    # Check if the user signed up through social authentication
    if kwargs.get("sociallogin"):
        # Create a Consumer instance linked to the user
        print(kwargs)
        Consumer(
            consumer=user,
            name="dce",
            phone_number="sac",
            address="kjds",
            payment_method="mobile",
            inside_dhaka=False,
            rewards=0,
        ).save()
