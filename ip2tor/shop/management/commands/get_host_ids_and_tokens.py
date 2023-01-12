from django.core.management.base import BaseCommand
from shop.models import Host
from itertools import chain
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    """
    List the string of Host IDs and Tokens that will be needed in the environment variables of the Host
        Examples:
        # To get the Host IDs and Tokens under of one or more IPs (separated by comma)
        python3 manage.py get_host_ids_and_tokens --ips=192.88.99.10
        python3 manage.py get_host_ids_and_tokens --ips=192.88.99.10,123.45.67.89,82.158.0.2
        
        # To get ALL stored Host IDs and Tokens
        python3 manage.py get_host_ids_and_tokens
    """

    def add_arguments(self, parser):
        parser.add_argument("--ips", required=False)
    
    def handle(self, *args, **options):
        
        ips = options["ips"]
        suffix_text = ""


        registered_ip_list = list(Host.objects.values_list('ip', flat=True).distinct())
        self.stdout.write(f'==============================================================')
        self.stdout.write(f'Registered IPs: {registered_ip_list}')
        
        if not None == ips:
            ips_list = ips.split(',')
            # here we limit the list of registered_ip_list to the ones passed in the argument
            registered_ip_list = [x for x in registered_ip_list if x in ips_list]
            pass

        self.stdout.write(f'Processing these IPs: {registered_ip_list}')
        
        hosts_active = []
        hosts_all = []

        for ip in registered_ip_list:
            hosts_active = chain(hosts_active, Host.active.filter(ip=ip))
            hosts_all = chain(hosts_all, Host.objects.filter(ip=ip))     


            host_active_string = ""
            for host in hosts_active:
                token = Token.objects.filter(user=host.token_user).first()
                host_active_string = host_active_string + str(host.id) + ',' + token.key + ':'
            
            
            host_all_string = ""
            for host in hosts_all:
                token = Token.objects.filter(user=host.token_user).first()
                host_all_string = host_all_string + str(host.id) + ',' + token.key + ':'


            self.stdout.write(f'--------------------------------------------------------------')
            self.stdout.write(f'IP ' + ip + ' - Host IDs and Token only for ACTIVE hosts:')
            self.stdout.write(host_active_string.strip(':'))
            self.stdout.write(f'IP ' + ip + ' - Host IDs and Token for ALL hosts:')
            self.stdout.write(host_all_string.strip(':'))       

        self.stdout.write(f'==============================================================')

        return

        
            


        