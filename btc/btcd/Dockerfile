FROM bitcoin/bitcoin

USER root
WORKDIR /app

RUN chown -R 101:0 /home/bitcoin && \
    chmod -R g+rwX /home/bitcoin

RUN echo '#!/bin/bash' > /app/env.sh && \
    echo "alias bcli='bitcoin-cli -regtest -rpcuser=bitcoin -rpcpassword=$RPC_PASSWORD -rpcconnect=127.0.0.1 -rpcport=18443'" >> /app/env.sh 

RUN echo 'source /app/env.sh' >> /etc/bashrc

ENTRYPOINT ["bitcoind"]
