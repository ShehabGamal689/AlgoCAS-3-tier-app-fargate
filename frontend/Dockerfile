FROM nginx:stable-alpine

# 1. Copy your custom nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

# 2. Copy the static site
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

# nginx’s default CMD already runs the server
