FROM bitcoin/bitcoin

# Use root temporarily to set directory permissions
USER root

# Create the Bitcoin data directory
RUN mkdir -p /home/bitcoin/.bitcoin && \
    chown -R 101:0 /home/bitcoin && \
    chmod -R g+rwX /home/bitcoin

ENTRYPOINT ["bitcoind"]
