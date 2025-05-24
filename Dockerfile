# Stage 1: Build Hugo site
FROM ghcr.io/hugomods/hugo:latest AS builder
WORKDIR /src
COPY . .
RUN hugo mod get
ARG HUGO_BASEURL=http://localhost:8080/
RUN hugo --minify --baseURL "$HUGO_BASEURL"

# Stage 2: Nginx para servir os arquivos estáticos
FROM nginx:alpine
COPY --from=builder /src/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
