# create from template (kubernetes apply)
oc create -f nolock.yaml

# cleanup
oc delete all -l app=nolock

# autoscale
oc autoscale deployment/frontend --min=1 --max=5 --cpu-percent=50

# mongo
oc new-app --name=mongodb --image=mongo:latest -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=1234

