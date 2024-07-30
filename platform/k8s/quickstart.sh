kubectl create configmap utils-memgpt --from-file=utils/memgpt.py
kubectl create configmap agent-app --from-file=agent/app.py
kubectl create configmap agent-code --from-file=agent.py

kubectl apply -f k8s/facilitator.yaml 
kubectl apply -f k8s/hr.yaml
kubectl apply -f k8s/cv.yaml 

# kubectl logs -f facilitator 
# kubectl logs -f isp-cv-expert 
# kubectl logs -f isp-hr-expert

kubectl port-forward facilitator 8888:80 &

#simulation announce of domain agents
curl -X 'PUT' \
  'http://localhost:8888/api/v1/new_agent?agent_name=isp-cv-expert%20&purpose=collecting%20cv%20of%20the%20group&hostname=isp-cv-expert&port=80' \
  -H 'accept: application/json'

curl -X 'PUT' \
  'http://localhost:8888/api/v1/new_agent?agent_name=isp-hr-expert%20&purpose=hr%20expert%20of%20the%20company&hostname=isp-hr-expert&port=80' \
  -H 'accept: application/json'

kubectl delete cm utils-memgpt