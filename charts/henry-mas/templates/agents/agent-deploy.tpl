{{- define "agent-deploy.tpl" }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
  labels:
    app: {{ .name }}
spec:
  {{- with .podTemplates }}
  replicas: {{ .replicaCount | default 1 }}
  {{- end }}
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
              "pip install agentbuddy==0.1.1.dev31 && python -m agentbuddy.agent.app",
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
            - name: SESSION_BASE_URL
              value: "http://webapp-session:8002"
            - name: AGENT_NAME
              value: "{{ .name }}"
            - name: PERSONA_NAME
              value: "{{ .name }}"
            - name: AGENT_HOST
              value: "{{ .name }}"
            - name: AGENT_PORT
              value: "80"
            {{- with .parent }}
            - name: AGENT_P_HOST
              value: "{{ . }}"
            - name: AGENT_P_PORT
              value: "80"
            {{- end }}
            {{- with .podTemplates }}
              {{- if .env }}
                {{- toYaml .env | nindent 12 }}
              {{- end }}
            {{- end }}
            {{- with .info }}
            - name: AGENT_PURPOSE
              value: |
                {{- include "formatAgentInfo" . | nindent 16 -}}
            {{- end }}
{{ end -}}