$BASE = "http://127.0.0.1:8001"
$SESSION = "portal-s1"
$INDEX = "portal-index"

# 1) Health
Invoke-RestMethod "$BASE/health"

# 2) Start application
Invoke-RestMethod "$BASE/chat" -Method Post -ContentType "application/json" -Body (@{
  session_id = $SESSION
  message = "start a liquor primary application"
  selected_index = $INDEX
} | ConvertTo-Json)

# 3) Upsert field
Invoke-RestMethod "$BASE/application/upsert" -Method Post -Form @{
  application_id = "APP-0000001"
  session_id = $SESSION
  field_id = "establishmentName"
  value = "Test Lounge"
}

# 4) Get fields
Invoke-RestMethod "$BASE/application/fields?session_id=$SESSION"

# 5) Upload a floorplan
"fake pdf" | Out-File -Encoding ascii floorplan.pdf
Invoke-RestMethod "$BASE/upload/floorplan?session_id=$SESSION" -Method Post -Form @{ file = Get-Item "floorplan.pdf" }

# 6) Review application
Invoke-RestMethod "$BASE/application/review?session_id=$SESSION"

# 7) Compute fees
Invoke-RestMethod "$BASE/application/fees?session_id=$SESSION"

# 8) Submit
Invoke-RestMethod "$BASE/application/submit?session_id=$SESSION" -Method Post -Form @{ attestation = "true" }
