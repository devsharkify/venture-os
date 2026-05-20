#!/bin/bash
# Background AI backfill loop. Smaller batches (limit=10 ~ 60s) to fit under gateway timeout.
LOG=/tmp/ai_backfill.log
API_URL=$(grep REACT_APP_BACKEND_URL /app/frontend/.env | cut -d '=' -f2)
echo "$(date) Starting AI backfill loop (limit=10 per batch)" > "$LOG"

CONSECUTIVE_ZEROS=0
for i in $(seq 1 800); do
  RESP=$(curl -s -m 120 -X POST -H "X-Admin-Phone: 7386917770" "$API_URL/api/news/admin/backfill-summaries?limit=10&use_ai=true" 2>&1)

  FIXED=$(echo "$RESP" | python3 -c "import sys,json
try:
    d = json.load(sys.stdin)
    print(d.get('fixed', -1))
except Exception:
    print(-1)" 2>/dev/null)

  echo "$(date) Batch $i: fixed=$FIXED" >> "$LOG"

  if [ "$FIXED" = "0" ]; then
    CONSECUTIVE_ZEROS=$((CONSECUTIVE_ZEROS+1))
    if [ "$CONSECUTIVE_ZEROS" -ge 3 ]; then
      echo "$(date) 3 consecutive zero-batches, stopping at $i." >> "$LOG"
      break
    fi
  else
    CONSECUTIVE_ZEROS=0
  fi
  sleep 1
done
echo "$(date) AI backfill loop complete" >> "$LOG"
