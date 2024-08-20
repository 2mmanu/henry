{{- define "pod-deploy.tpl" }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
  labels:
    app: {{ .name }}
spec:
  replicas: {{ .podTemplates.replicaCount | default 1 }}
  selector:
    matchLabels:
      app: {{ .name }}
  template:
    metadata:
      labels:
        app: {{ .name }}
    spec:
      containers:
        - name: {{ .name }}
          image: 2mmanu/agentbuddy:latest
          command:
            [
              "sh",
              "-c",
              "{{ .command }}",
            ]
          env:
            - name: MEMGPT_BASE_URL
              valueFrom:
                configMapKeyRef:
                  name: memgpt-config
                  key: memgpt-host
            - name: MEMGPT_KEY
              valueFrom:
                configMapKeyRef:
                  name: memgpt-config
                  key: memgpt-key
            {{- with .podTemplates }}
              {{- if .env }}
                {{- toYaml .env | nindent 12 }}
              {{- end }}
            {{- end }}
{{ end -}}