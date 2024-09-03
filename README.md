# HEnRY 

### TL;TR

#### REQUIREMENTS

``` bash
brew install jq
```

``` bash
helm install --repo https://2mmanu.github.io/helm-memgpt-charts/ henry-memgpt memgpt
kubectl port-forward svc/henry-memgpt 8083:8083
```

``` bash
export MEMGPT_KEY=$(curl -X 'POST' \
  'http://localhost:8083/admin/users/keys' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer password' \
  -H 'Content-Type: application/json' \
  -s -d '{
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "string"
}' | jq ".api_key")
```

#### INSTALL

``` bash
helm install henry charts/henry-mas/ --set .Values.global.memgpt.key=$MEMGPT_KEY
kubectl port-forward svc/krakend-service  8000:8000
```

Then, open a browser and navigate to [`http://localhost:8000`](http://localhost:8000)