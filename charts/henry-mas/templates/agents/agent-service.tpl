{{ define "agent-service.tpl" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ .name }}
spec:
  selector:
    app: {{ .name }}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
{{ end -}}