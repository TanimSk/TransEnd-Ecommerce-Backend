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
    sociallogin = kwargs.get("sociallogin")
    if sociallogin and sociallogin.account.provider == "google":
        # Extract the first_name from user data
        name = sociallogin.account.extra_data.get("name", "")
        Consumer(
            consumer=user,
            name=name,
            phone_number="",
            address="",
            payment_method="mobile",
            inside_dhaka=False,
            rewards=0,
        ).save()

        user.is_consumer = True
        user.save()
