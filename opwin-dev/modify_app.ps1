$path = Join-Path $PSScriptRoot "App.tsx"
$content = Get-Content -Path $path -Raw

# Step 1: Add LLM_API_BASE constant after faqs array
$marker = "];`n`nexport default function App()"
$idx = $content.IndexOf($marker)
if ($idx -lt 0) { Write-Host "ERROR: faqs marker not found"; exit 1 }
$llm = @"
// LLM endpoint for the fun chatbot. Points to the local llama-server on this
const LLM_API_BASE = import.meta.env.VITE_LLM_API_URL || "http://127.0.0.1:9931/v1";

export default function App()
"@
$content = $content.Substring(0, $idx) + $llm + $content.Substring($idx)
Write-Host "Step 1 done"
