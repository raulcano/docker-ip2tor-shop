FROM nginx
RUN rm /etc/nginx/conf.d/default.conf
COPY .docker/shop.localhost.conf /etc/nginx/conf.d/default.conf