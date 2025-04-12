FROM lightninglabs/lnd:v0.19.0-beta.rc2

# Create a writable directory for LND data that works with random UIDs
RUN mkdir -p /data/.lnd && \
    chgrp -R 0 /data/.lnd && \
    chmod -R g+rwX /data/.lnd

# Default to the safe path
ENV LND_DIR=/data/.lnd

ENTRYPOINT ["lnd"]
