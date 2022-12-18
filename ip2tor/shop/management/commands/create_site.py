from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    """
    Create a site
        Example:
        manage.py create_site --name="My Site" --domain=mysite.com
    """

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--domain", required=True)
    
    def handle(self, *args, **options):
        
        domain = options["domain"]
        sitename = options["name"]

        if Site.objects.filter(domain=domain).exists():
            self.stdout.write(f'Site with domain "{domain}" exists already. No new site was created')
            return

        Site.objects.create(name=sitename, domain=domain)
        self.stdout.write(f'Site with domain "{domain}" and name "{sitename}" was created')
        return

        
            


        