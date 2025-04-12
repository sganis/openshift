FROM lightninglabs/lnd:v0.19.0-beta.rc2

USER root

# Ensure the default LND directory is writable by UID 101 (used in OpenShift restricted SCC)
RUN mkdir -p /root/.lnd && \
    chown -R 101:0 /root/.lnd && \
    chmod -R g+rwX /root/.lnd

ENTRYPOINT ["lnd"]