from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from shop.models import Host, PortRange

class Command(BaseCommand):
    """
    Create a site
        Example:
        manage.py create_host --owner=operator --sitedomain="ip2tor.com" --name="host1" --description="A cool host" --ip=10.11.42.3 --portranges=10000,11000:20000,21000 --rangetype=T --isenabled=True --isalive=True 
        --istestnet=False --offerstorbridges=True --torbridgeduration=86400 --torbridgepriceinitial=25000 --torbridgepriceextension=20000
        --offersrsshtunnels=False --rsshtunnelprice=1000 --tos="" --tosurl="" --cistatus=0 --cidate="2022-12-19 00:00" --cimessage=""
    """

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True)
        parser.add_argument("--sitedomain", required=True)
        parser.add_argument("--name", required=True)
        parser.add_argument("--description", required=False)
        parser.add_argument("--ip", required=True)
        parser.add_argument("--portranges", required=False)
        parser.add_argument("--rangetype", required=False, default='I')
        parser.add_argument("--isenabled", required=False, default=True)
        parser.add_argument("--isalive", required=False, default=False)
        parser.add_argument("--istestnet", required=False, default=False)
        parser.add_argument("--offerstorbridges", required=False, default=True)
        parser.add_argument("--torbridgeduration", required=False, default=86400)
        parser.add_argument("--torbridgepriceinitial", required=False, default=25000)
        parser.add_argument("--torbridgepriceextension", required=False, default=20000)
        parser.add_argument("--offersrsshtunnels", required=False, default=False)
        parser.add_argument("--rsshtunnelprice", required=False, default=1000)
        parser.add_argument("--tos", required=False)
        parser.add_argument("--tosurl", required=False)
        parser.add_argument("--cistatus", required=False, default=0)
        parser.add_argument("--cidate", required=False)
        parser.add_argument("--cimessage", required=False)
    
    def handle(self, *args, **options):
        owner = options["owner"]
        sitedomain = options["sitedomain"]
        hostname = options["name"]
        description = options["description"]
        ip = options["ip"]
        portranges=options["portranges"]
        rangetype = options["rangetype"]
        isenabled = options["isenabled"]
        isalive = options["isalive"]
        istestnet = options["istestnet"]
        offerstorbridges = options["offerstorbridges"]
        torbridgeduration = options["torbridgeduration"]
        torbridgepriceinitial = options["torbridgepriceinitial"]
        torbridgepriceextension = options["torbridgepriceextension"]
        offersrsshtunnels = options["offersrsshtunnels"]
        rsshtunnelprice = options["rsshtunnelprice"]
        tos = options["tos"]
        tosurl = options["tosurl"]
        cistatus = options["cistatus"]
        cidate = options["cidate"]
        cimessage = options["cimessage"]

        User = get_user_model()
        if not User.objects.exists():
            return

        # Check if the owner exists - exit otherwise
        if not User.objects.filter(username=owner).exists():
            self.stdout.write(f'User with name "{owner}" does not exist. Host was not created')
            return
        else:
            owner_object = User.objects.filter(username=owner).first()
            # Load the token user
            # token_user_object = owner_object

        # Check if the site exists - exit otherwise
        if not Site.objects.filter(domain=sitedomain).exists():
            self.stdout.write(f'Site with domain "{sitedomain}" does not exist. Host was not created')
            return
        else:
            site_object = Site.objects.filter(domain=sitedomain).first()

        # # Check if the host exists already (identified by the name AND the IP)
        if Host.objects.filter(name=hostname).exists() and Host.objects.filter(ip=ip).exists():
            self.stdout.write(f'A Host with ip "{ip}" and name "{hostname}" exists already. Host was not created')
            return

        # Create host, and add it to user and site
        host = Host.objects.create(
            ip=ip, is_enabled=isenabled, is_alive=isalive, owner=owner_object, name=hostname, description=description,
            site=site_object, is_testnet=istestnet, offers_tor_bridges=offerstorbridges, tor_bridge_duration=torbridgeduration,
            tor_bridge_price_initial=torbridgepriceinitial, tor_bridge_price_extension=torbridgepriceextension,
            offers_rssh_tunnels=offersrsshtunnels, rssh_tunnel_price=rsshtunnelprice,terms_of_service=tos,
            terms_of_service_url=tosurl, ci_date=cidate, ci_message=cimessage, ci_status=cistatus
        )
        
        # If we pass the token_user , it won't create the Host if that has been used already
        # So we create it without token_user and it will generate one automatically
        # # Create host, and add it to user and site
        # host = Host.objects.create(
        #     ip=ip, is_enabled=isenabled, is_alive=isalive, owner=owner_object, token_user=token_user_object, name=hostname, 
        #     site=site_object, is_testnet=istestnet, offers_tor_bridges=offerstorbridges, tor_bridge_duration=torbridgeduration,
        #     tor_bridge_price_initial=torbridgepriceinitial, tor_bridge_price_extension=torbridgepriceextension,
        #     offers_rssh_tunnels=offersrsshtunnels, rssh_tunnel_price=rsshtunnelprice,terms_of_service=tos,
        #     terms_of_service_url=tosurl, ci_date=cidate, ci_message=cimessage, ci_status=cistatus
        # )

        # Create port ranges for this host, based on a list of start,end:start2,end2:start3,end3 etc
        
        portranges_list = portranges.strip().split(':')
        for range_separated_by_comma in portranges_list :
            range = range_separated_by_comma.split(',')
            PortRange.objects.create( type=rangetype, start=range[0], end=range[1], host=host )


        self.stdout.write(f'A Host with ip "{ip}" and name "{hostname}" was created successfully')
        return

        
            


        