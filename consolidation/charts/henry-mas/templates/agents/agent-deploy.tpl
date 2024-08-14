{{- define "agent-deploy.tpl" }}
apiVersion: v1
kind: Pod
metadata:
  name: {{ .name }}
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
          "pip install agentbuddy==0.1.1.dev1 && python -m agentbuddy.app",
        ]
      env:
        - name: MEMGPT_BASEURL
          valueFrom:
            configMapKeyRef:
              name: memgpt-config
              key: memgpt-host
        - name: MEMGPT_KEY
          valueFrom:
            configMapKeyRef:
              name: memgpt-config
              key: memgpt-key
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
                {{- toYaml .env | nindent 8 }}
            {{- end }}
        {{- end }}
        {{- with .info }}
        - name: AGENT_PURPOSE
          value: |
            {{- include "formatAgentInfo" . | nindent 12 -}}
        {{- end }}
{{ end -}}