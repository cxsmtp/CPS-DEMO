# Nexa Commerce - storefront (PHP).
FROM php:8.3-cli-alpine

WORKDIR /srv/storefront
COPY public/ ./public/
RUN mkdir -p ./data && chown -R www-data:www-data /srv/storefront

# USER is set deliberately: running as root rates High in the reference
# tenant and every chain here must stay at Medium or below.
USER www-data

EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://127.0.0.1:8080/index.php || exit 1
CMD ["php", "-S", "0.0.0.0:8080", "-t", "public"]
