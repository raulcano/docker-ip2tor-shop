This files help create a container running a web service accessible via Tor.
This is useful to test the shop with a real onion address, by creating and suspending Tor bridges to this address.

To persist the onion address we mounted a volume in the folder .docker/sample_hidden_service/.tor

To retrieve the onion address, run this command once the container is up and running:
```
docker exec -it ip2tor-shop-sample-hidden-service cat /var/lib/tor/sample_hidden_service/hostname
```