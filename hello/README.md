# openshift

## load balance to different pods

Add to deployment yaml:
  annotations:
    haproxy.router.openshift.io/balance: roudrobin
    haproxy.router.openshift.io/disable_cookies: 'true'

## deploy
oc apply -f hello.yml
oc start-build hello --follow

