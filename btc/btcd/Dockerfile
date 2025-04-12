FROM bitcoin/bitcoin

USER root

RUN chown -R 101:0 /home/bitcoin && \
    chmod -R g+rwX /home/bitcoin

RUN echo "alias bcli='bitcoin-cli -regtest -rpcuser=bitcoin -rpcpassword=Secret1! -rpcconnect=127.0.0.1 -rpcport=18443'" >> /etc/bashrc

ENTRYPOINT ["bitcoind"]
