# docker build -t base-image:latest .
# docker tag base-image:latest 2mmanu/agentbuddy:latest
# docker push 2mmanu/agentbuddy:latest

kubectl delete pod isp-cv-expert  isp-hr-expert facilitator
kubectl delete cm utils-memgpt agent-app agent-code

kubectl create configmap utils-memgpt --from-file=utils/memgpt.py
kubectl create configmap agent-app --from-file=agent/app.py
kubectl create configmap agent-code --from-file=agent.py

sleep 10
kubectl apply -f k8s/facilitator.yaml 
sleep 5
kubectl apply -f k8s/hr.yaml
sleep 5
kubectl apply -f k8s/cv.yaml 

curl localhost:8888
curl localhost:8790
curl localhost:8690

kubectl port-forward facilitator 8888:80 &
kubectl port-forward isp-cv-expert 8790:80 &
kubectl port-forward isp-hr-expert 8690:80 &

kubectl logs -f facilitator