FROM lightninglabs/lnd:v0.19.0-beta.rc2

RUN mkdir -p /data/.lnd && \
    chgrp -R 0 /data/.lnd && \
    chmod -R g+rwX /data/.lnd

ENV LND_DIR=/data/.lnd

ENTRYPOINT ["lnd"]
