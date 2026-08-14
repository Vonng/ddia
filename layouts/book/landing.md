{{- .Page.Store.Set "tdOutputFormat" "markdown" -}}
# {{ .Title | strings.TrimSpace }}
{{- with .Description | strings.TrimSpace }}

> {{ replace . "\n" "\n> " }}
{{- end }}

{{ .RawContent | safeHTML }}
