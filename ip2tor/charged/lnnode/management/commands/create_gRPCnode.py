from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from charged.lnnode.models.lnd import LndGRpcNode

class Command(BaseCommand):
    """
    Create a node programatically
    Example:
        manage.py create_node --name=MyNode --priority=0 --owner=operator --macaroon_admin=xxxx --macaroon_invoice=yyyy --macaroon_readonly=zzzz --tls_certificate=XXXX --host=localhost --port=8080
    """

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--priority", required=False, default=0)
        parser.add_argument("--owner", required=False, default="operator")
        parser.add_argument("--macaroon_admin", required=True)
        parser.add_argument("--macaroon_invoice", required=True)
        parser.add_argument("--macaroon_readonly", required=True)
        parser.add_argument("--tls_certificate", required=True)
        parser.add_argument("--tls_verification", required=False, default=True)
        parser.add_argument("--host", required=True)
        parser.add_argument("--port", required=False, default=10009)

    def handle(self, *args, **options):

        User = get_user_model()
        if not User.objects.exists():
            return
        
        if not User.objects.filter(username=options["owner"]).exists():
            return f'The user "{options["owner"]}" does not exist'
        
        if LndGRpcNode.objects.filter(name=options["name"]).exists():
            return f'A node with the name "{options["name"]}" exists already. Make sure to use a unique name.'

        if LndGRpcNode.objects.filter(hostname=options["host"], port=options["port"]).exists():
            return f'A node with the hostname "{options["host"]}" and port "{options["port"]}" exists already. Make sure to use a unique combination of hostname and port.'

        owner = User.objects.filter(username=options["owner"]).first()
        priority = options["priority"]
        name = options["name"]
        macaroon_admin = options["macaroon_admin"]
        macaroon_invoice = options["macaroon_invoice"]
        macaroon_readonly = options["macaroon_readonly"]
        tls_certificate = options["tls_certificate"]
        tls_verification = options["tls_verification"]
        ln_host = options["host"]
        ln_port = options["port"]


        # Check that name nor host exist

        LndGRpcNode.objects.create(
            priority=priority,
            name=name,
            owner=owner,
            tls_cert_verification=tls_verification,
            tls_cert=tls_certificate,
            macaroon_admin=macaroon_admin,
            macaroon_invoice=macaroon_invoice,
            macaroon_readonly=macaroon_readonly,
            hostname=ln_host,
            port=ln_port,
        )

        self.stdout.write(f'Node "{name}" was created')