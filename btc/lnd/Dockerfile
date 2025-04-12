FROM lightninglabs/lnd:v0.19.0-beta.rc2

USER root
WORKDIR /app
RUN mkdir -p /data/.lnd && \
    chgrp -R 0 /data/.lnd && \
    chmod -R g+rwX /data/.lnd

RUN echo '#!/bin/bash' > /app/env.sh && \
    echo 'export LND_DIR=/data/.lnd' >> /app/env.sh && \
    echo "alias lcli='lncli --network=regtest --lnddir=/data/.lnd'" >> /app/env.sh && \
    echo "alias ll='ls -ltr --color'" >> /app/env.sh
    
ENTRYPOINT ["lnd"]
