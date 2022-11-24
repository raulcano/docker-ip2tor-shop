FROM nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY .docker/shop.localhost.conf /etc/nginx/conf.d/default.conf

# ADD static /usr/share/nginx/static
# ADD media /usr/share/nginx/media