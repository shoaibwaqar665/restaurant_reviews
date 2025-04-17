#!/bin/bash

if [ -z "$1" ]; then
  echo "No restaurant slug provided"
  exit 1
fi
# Run the curl command and store the response in a text file
curl --location "https://www.yelp.com/biz/$1" \
  --header 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0' \
  --header 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
  --header 'Accept-Language: en-US,en;q=0.5' \
  --header 'Accept-Encoding: gzip, deflate, br, zstd' \
  --header 'Alt-Used: www.yelp.com' \
  --header 'Connection: keep-alive' \
  --header 'Upgrade-Insecure-Requests: 1' \
  --header 'Sec-Fetch-Dest: document' \
  --header 'Sec-Fetch-Mode: navigate' \
  --header 'Sec-Fetch-Site: none' \
  --header 'Sec-Fetch-User: ?1' \
  --header 'Priority: u=0, i' \
  --header 'TE: trailers' \
  --header 'Cookie: bse=e43a34ccfc5c4985aac920d63e7c89aa; hl=en_US; bsi=1%7Cc7bb9dad-8d5c-5cbb-a215-703ae21b3989%7C1742580580782%7C1742578273542%7C1%7Ca6ac43062bd691c9; wdi=2|CFCAA4676196EA17|0x1.9f76898629f62p+30|65809861450fb296; xcj=1|jvmVI8LAInYsyashV-W2R8t6UxjY2xdncbCEtmlIEuM; _gcl_au=1.1.1606996840.1742578277; datadome=HutE0M4ySVES4bnQ~LAa6PHB9dXHOz~APrnB6MFBxq2tciUgGBP8krX19o6K6ve2ZI1yHFESVgoMQPoWhaqC87KFEltorVnmtEMbyJivnX5evNwj9v7LcW13PvUvHMYd; _scid=6GdkU3sMXhaooMRzuNOFbfV8INAxDAF3; ndp_session_id=ad0ed671-0ae5-4e48-95c2-0978f8bbbeb1; _sctr=1%7C1742497200000; spses.d161=*; spid.d161=772ba771-b9da-4abf-8d4e-0fb7925e7822.1742578281.1.1742580687..0e01f670-271c-4ae2-b4ae-a4506fe51971..ed724f04-b2f1-42ad-bdf4-eddab283b160.1742578281010.59; _ga_K9Z2ZEVC8C=GS1.2.1742578281.1.1.1742579792.0.0.0; _ga=GA1.2.CFCAA4676196EA17; _fbp=fb.1.1742578284026.223913002276667587; g_state={"i_p":1742585490813,"i_l":1}; OptanonConsent=isGpcEnabled=0&datestamp=Fri+Mar+21+2025+22%3A58%3A59+GMT%2B0500+(Pakistan+Standard+Time)&version=202403.1.0&browserGpcFlag=1&isIABGlobal=false&identifierType=Cookie+Unique+Id&hosts=&consentId=ecf462b6-c598-4581-b560-eff56cb749da&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.yelp.com%2Fbiz%2Fshakeys-pizza-parlor-burbank-3&groups=BG122%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1%2CC0004%3A1; _scid_r=8udkU3sMXhaooMRzuNOFbfV8INAxDAF3c8uSrQ; _uetsid=4c1c8610067a11f09ad76f7f6406088c; _uetvid=4c1c8b60067a11f09c62376bc715634c' \
   --compressed \
  -o $1.html
