FROM bitcoin/bitcoin

# Use root temporarily to set directory permissions
USER root

# Create the Bitcoin data directory
RUN apt update && \
    apt install -y bash bash-completion && \
    chown -R 101:0 /home/bitcoin && \
    chmod -R g+rwX /home/bitcoin

ENV SHELL=/bin/bash

ENTRYPOINT ["bitcoind"]
