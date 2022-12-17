from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings

class Command(BaseCommand):
    """
    Create a user and assign it to the operators group
    The operators group must exist , otherwise we won't do anything
    Example:
        manage.py create_operator --user=admin --password=changeme --email=operator@email.com
    """

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="operator@example.com")
    
    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.exists():
            return
        
        operators_group_name = getattr(settings, 'SHOP_OPERATOR_GROUP_NAME', 'operators')
        if not Group.objects.filter(name=operators_group_name).exists():
            self.stdout.write(f'The operator group does not exist. Make sure to run this command AFTER you migrate the database or (1)create an operator group, (2)set its name in the settings variable SHOP_OPERATOR_GROUP_NAME and (3)run this command manually')
            return 

        username = options["user"]
        password = options["password"]
        email = options["email"]
        
        
        if not User.objects.filter(username=username).exists():
            User.objects.create(username=username, password=password, email=email, is_staff=True, is_active=True)
            self.stdout.write(f'User "{username}" was created.')
        else:
            self.stdout.write(f'User "{username}" exists already. No user was created')

        operator = User.objects.filter(username=username).first()
        if not operator.groups.filter(name=operators_group_name).exists():
            operators_group = Group.objects.get(name=operators_group_name)
            operators_group.user_set.add(operator)
            self.stdout.write(f'User "{username}" was assigned to the group "{operators_group_name}".')
        else:
            self.stdout.write(f'User "{username}" was already assigned to the group "{operators_group_name}". No changes were made')
        return

        
            


        