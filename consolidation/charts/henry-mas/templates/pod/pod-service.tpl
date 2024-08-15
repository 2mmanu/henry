{{ define "pod-service.tpl" -}}
apiVersion: v1
kind: Service
metadata:
  name: {{ .name }}
spec:
  selector:
    app: {{ .name }}
  ports:
    - protocol: TCP
      port: {{ .port }}
      targetPort: {{ .port }}
{{ end -}}