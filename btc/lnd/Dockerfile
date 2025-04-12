FROM lightninglabs/lnd:v0.19.0-beta.rc2

# Create the LND data directory with open group permissions
RUN mkdir -p /root/.lnd && \
    chmod -R 0770 /root/.lnd

# Set group ownership to root group (GID 0) so OpenShift-assigned user can write
RUN chgrp -R 0 /root/.lnd

# Allow any user in group 0 to read/write
RUN chmod -R g+rwX /root/.lnd

ENTRYPOINT ["lnd"]