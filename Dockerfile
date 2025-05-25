# Stage 1: Build Hugo site
FROM ghcr.io/hugomods/hugo:latest AS builder
WORKDIR /src
COPY . .
ARG HUGO_BASEURL=http://localhost:8080/
RUN hugo --minify --baseURL "$HUGO_BASEURL"

# Optimize cover images
RUN apk add --no-cache pngquant \
    && find public/cordeis -name 'cover.png' -exec pngquant --force --ext .png 80 {} \;

# Stage 2: Nginx para servir os arquivos estáticos
FROM nginx:alpine
COPY --from=builder /src/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
