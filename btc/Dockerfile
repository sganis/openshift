FROM bitcoin/bitcoin

# Ensure script runs as root during build
USER root

# Set UID and GID to 101 for OpenShift compatibility
RUN groupmod -g 101 bitcoin && \
    usermod -u 101 -g 101 bitcoin && \
    mkdir -p /home/bitcoin/.bitcoin && \
    chown -R bitcoin:bitcoin /home/bitcoin && \
    chmod -R 700 /home/bitcoin

# Revert to non-root user (bitcoin)
USER bitcoin

# Entrypoint from base image remains unchanged
CMD ["bitcoind"]
