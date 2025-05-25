# Stage 1: Booklet builder with prebuilt dependencies
FROM pandoc/latex:latest-ubuntu AS booklet
WORKDIR /src

# Copy only scripts and templates first for better caching
COPY script/booklet.sh script/booklet-template.tex ./script/
COPY content/cordeis ./content/cordeis

RUN bash script/booklet.sh

# Stage 2: Hugo build
FROM ghcr.io/hugomods/hugo:latest AS builder
WORKDIR /src
COPY . .

# Copy generated PDFs from booklet stage
COPY --from=booklet /src/static/livretos ./static/livretos

ARG HUGO_BASEURL=http://localhost:8080/
RUN hugo --minify --baseURL "$HUGO_BASEURL"

RUN apk add --no-cache pngquant \
    && find public/cordeis -name 'cover.png' -exec pngquant --force --ext .png 80 {} \;

# Stage 3: Nginx serve
FROM nginx:alpine
COPY --from=builder /src/public /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
