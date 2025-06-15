FROM nginx:1.25-alpine

RUN apk add --no-cache openssl

COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN rm -f /etc/nginx/conf.d/default.conf.dpkg-old

RUN mkdir -p /etc/ssl/certs /etc/ssl/private

RUN chmod 755 /etc/ssl/certs && \
    chmod 700 /etc/ssl/private

COPY wait-for-ssl.sh /wait-for-ssl.sh
RUN chmod +x /wait-for-ssl.sh

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f https://localhost/health || exit 1

EXPOSE 80 443 9001

CMD ["/wait-for-ssl.sh"]
