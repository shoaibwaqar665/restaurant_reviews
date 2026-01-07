#!/bin/bash

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <url> [output_html_path]" >&2
  exit 1
fi

URL="$1"
OUTPUT="${2:-}"

if [ -z "$OUTPUT" ]; then
  SLUG=$(echo "$URL" | sed -E 's|https?://[^/]+/||; s|\?.*||; s|[/?&=]+|-|g')
  OUTPUT="${SLUG}.html"
fi


# Proxy credentials
PROXY_SERVER="geo.iproyal.com:12321"
PROXY_USER="jxuQHPGrydd0jIva"
PROXY_PASS="RU7veaFCDR0nRHbL"

echo "URL: $URL"

MAX_RETRIES="${MAX_RETRIES:-12}"
RETRY_SLEEP_SECONDS="${RETRY_SLEEP_SECONDS:-5}"

# Function to try curl with or without proxy
try_curl() {
  local USE_PROXY=$1
  local PROXY_FLAG=""
  
  if [ "$USE_PROXY" = "true" ]; then
    PROXY_FLAG="--proxy $PROXY_USER:$PROXY_PASS@$PROXY_SERVER"
    echo "🔐 Using proxy..."
  else
    echo "🌐 Trying without proxy..."
  fi
  
  HTTP_STATUS=$(curl $PROXY_FLAG \
  --location "$URL" \
  --connect-timeout 20 \
  --max-time 60 \
  --compressed \
  --header 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  --header 'accept-language: en-GB,en;q=0.9' \
  --header 'priority: u=0, i' \
  --header 'referer: https://www.yelp.com/biz/toi-on-sunset-los-angeles' \
  --header 'sec-ch-device-memory: 8' \
  --header 'sec-ch-ua: "Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"' \
  --header 'sec-ch-ua-arch: "arm"' \
  --header 'sec-ch-ua-full-version-list: "Google Chrome";v="143.0.7499.192", "Chromium";v="143.0.7499.192", "Not A(Brand";v="24.0.0.0"' \
  --header 'sec-ch-ua-mobile: ?0' \
  --header 'sec-ch-ua-model: ""' \
  --header 'sec-ch-ua-platform: "macOS"' \
  --header 'sec-fetch-dest: document' \
  --header 'sec-fetch-mode: navigate' \
  --header 'sec-fetch-site: same-origin' \
  --header 'upgrade-insecure-requests: 1' \
  --header 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' \
  --header 'Cookie: bse=75e60ad5ceb34e16b9a5e6c304a2ed22; hl=en_US; bsi=1%7Ca00560a2-4de8-5c9e-ba8a-72ea43e5ac0a%7C1767812829052%7C1767812829052%7C1%7C9dfc5f856f5f8128; wdi=2|BE97DF8093665434|0x1.a57abb74350d3p+30|c2029729db7280fe; xcj=1|21A_rGMJWOLSp2bpNgizDYOD5YhLiyjT-FkpxOqW0xg; spses.5f33=*; _ga=GA1.2.BE97DF8093665434; _ga_K9Z2ZEVC8C=GS2.2.s1767812832$o1$g0$t1767812832$j60$l0$h0; _gcl_au=1.1.1906543569.1767812833; g_state={"i_l":0,"i_ll":1767812833586,"i_b":"boGU2qmXum8AfOVi8RrQPB/0ZcQONitUBR1JyQdSb7k","i_e":{"enable_itp_optimization":0}}; _fbp=fb.1.1767812833702.503642055167571303; _uetsid=139a0910ebfc11f08d43f7ab551220da; _uetvid=139a2300ebfc11f0ab8fa34939412129; __adroll_fpc=b0bfc683fe5cd70aad4304118779da0c-1767812836613; spid.5f33=56d589b0-b70e-4323-aaea-b74be7a645e7.1767812832.1.1767812837..d9b1c05d-6846-47f8-aa2f-19fb1bbcbf6d..e2a4816e-4e67-42e8-9397-def391153b6a.1767812831947.3; __ar_v4=%7CBHPKS4B4ONEJJMGH4QCJZR%3A20260106%3A1%7CQB5JPFIKRZDSBOZSULG4YB%3A20260106%3A1%7C7YX6SJQ4RZAMPB6LZ7CHFF%3A20260106%3A1; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Jan+08+2026+00%3A07%3A17+GMT%2B0500+(Pakistan+Standard+Time)&version=202510.2.0&browserGpcFlag=0&isIABGlobal=false&identifierType=Cookie+Unique+Id&hosts=&consentId=730dfd7e-162e-42e8-a31b-c3ba392fd3c5&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.yelp.com%2Fbiz%2Ftoi-on-sunset-los-angeles&groups=BG122%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1%2CC0004%3A1; datadome=5yt_fA7suDUqmYzFSYxM7nlfQzq~f4WvFx1b~Lb~oK0FdCjbAwkAb8Rn0NaiEleY0tIHTcqfl3S2_boWrwzw5l3OfclKOTeeLa4NYqdRNf~f0nXrREgllOvabWhggWZW; bsi=1%7Ca00560a2-4de8-5c9e-ba8a-72ea43e5ac0a%7C1767812926918%7C1767812829052%7C1%7C661c140dcc6ef51b; datadome=RWdySJ5hlYP~fBEIBiti0vKR2w1slR_7hgyIZ9~tPoM6yRs50V3DxFkdfz0jmPOtn8dDV~8JEMQ08Z4ZmyEY_9wozDTfshai8fUurVs2gcg4giIEH3M4XnbyJnZ_wVn2; wdi=2|BE97DF8093665434|0x1.a57abb74350d3p+30|c2029729db7280fe' \
  --write-out "%{http_code}" \
  --silent --show-error \
  --output "$OUTPUT"
)

  CURL_EXIT=$?
  
  echo "HTTP Status: $HTTP_STATUS"
  return $CURL_EXIT
}

# Retry loop - try without proxy first, then with proxy
attempt=1
use_proxy=false

while [ "$attempt" -le "$MAX_RETRIES" ]; do
  echo "Attempt ${attempt}/${MAX_RETRIES}: Trying $URL"
  
  try_curl "$use_proxy"

  if [ "$CURL_EXIT" -eq 0 ] && [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Success: Received 200 OK"
    exit 0
  else
    rm -f "$OUTPUT" >/dev/null 2>&1 || true
    echo "❌ Failed (curl_exit=$CURL_EXIT, http_status=$HTTP_STATUS)"
    
    # If first attempt without proxy failed, switch to proxy
    if [ "$use_proxy" = "false" ]; then
      echo "💡 Switching to proxy for next attempt..."
      use_proxy=true
    fi
    
    if [ "$attempt" -lt "$MAX_RETRIES" ]; then
      echo "Retrying in ${RETRY_SLEEP_SECONDS}s..."
      sleep "$RETRY_SLEEP_SECONDS"
    fi
  fi
  attempt=$((attempt + 1))
done

echo "Failed to fetch $URL after ${MAX_RETRIES} attempts." >&2
exit 2
