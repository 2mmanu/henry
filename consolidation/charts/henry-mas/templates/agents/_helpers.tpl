{{- define "formatAgentInfo" }}
{{- $description := .agentDescription | trim | replace "\n" "\n" -}}
{{- $examples := .exampleQuestions | trim | replace "\n" "\n" -}}
DESCRIPTION:
{{ $description }}
EXAMPLES:
{{ $examples }}
{{ end -}}