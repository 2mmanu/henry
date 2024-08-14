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
          "python /app.py",
        ]
      env:
        - name: MEMGPT_BASEURL
          value: "http://my-memgpt:8083"
        - name: AGENT_NAME
          value: "{{ .name }}"
        - name: PERSONA_NAME
          value: "{{ .name }}"
        - name: AGENT_HOST
          value: "{{ .name }}"
        - name: AGENT_PORT
          value: "80"
        - name: AGENT_P_HOST
          value: "facilitator"
        - name: AGENT_P_PORT
          value: "80"
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
      volumeMounts:
        - name: code-volume
          mountPath: /app.py
          subPath: agent.py
        - name: code-utils-volume
          mountPath: /utils/memgpt.py
          subPath: memgpt.py
        - name: code-agent-volume
          mountPath: /agent/app.py
          subPath: app.py
  volumes:
    - name: code-volume
      configMap:
        name: agent-code
    - name: code-utils-volume
      configMap:
        name: utils-memgpt
    - name: code-agent-volume
      configMap:
        name: agent-app
{{ end -}}