FROM bitcoin/bitcoin

USER root

RUN chown -R 101:0 /home/bitcoin && \
    chmod -R g+rwX /home/bitcoin

ENTRYPOINT ["bitcoind"]
