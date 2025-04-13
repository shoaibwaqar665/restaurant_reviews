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
  --header 'Cookie: rollup_ga_GQ3NG7ZMF4=GS1.1.1743957064.1.0.1743957064.0.0.0; rollup_ga=GA1.1.2098251283.1743957064; _ga_MEZL1ZKM71=GS1.1.1743957064.1.1.1743957070.0.0.0; _ga=GA1.2.DF69B3B872414D0D; _gcl_au=1.1.1475894219.1743957065; _clck=4fr16c%7C2%7Cfuu%7C0%7C1922; _fbp=fb.1.1743957066402.27466834537507476; _clsk=n61vl4%7C1743957067300%7C1%7C1%7Cq.clarity.ms%2Fcollect; IR_gbd=yelp.com; IR_12770=1743957066755%7Cc-23333%7C1743957066755%7C%7C; IR_PI=8b74312f-1304-11f0-a306-75eddef5d75b%7C1743957066755; datadome=T3PejQjiyWzdPDzYzMX~DAUehqfS5UoHR2WdF6ZGsclIxMScdnqBCftRgYn2HhkhOG63S1ghV8oWNtvsmtDwIeQUKYebdS6ozc8I_NEZ4nuUYdGJdaduI_tJ_uFKhAZL; bse=8e607b4fa9664172a2fec2f303f38aae; hl=en_US; bsi=1%7Cd3c986d3-a94a-5691-9bfb-e71840954c5b%7C1743960794563%7C1743958085231%7C1%7Cd1e8371bd6898182; wdi=2|DF69B3B872414D0D|0x1.9fcac114ebd38p+30|11f6cd1d56f94d06; xcj=1|RU0sUCrbfrkPJAKI8W876CpzaRRDgKBWd0monJErosw; spses.d161=*; spid.d161=bdbe40d2-788c-4b07-b9cc-6cc7adf32d3b.1743958090.1.1743960812..026157f9-843f-4d09-bf9d-27e092435724..87b0c9b9-af37-436a-b804-73cb366b4410.1743958089830.239; _ga_K9Z2ZEVC8C=GS1.2.1743958089.1.1.1743960806.0.0.0; __adroll_fpc=2c9740ff5275f5138ebb6ffb0c0f97fe-1743958093959; __ar_v4=7YX6SJQ4RZAMPB6LZ7CHFF%3A20250406%3A26%7CQB5JPFIKRZDSBOZSULG4YB%3A20250406%3A26%7CBHPKS4B4ONEJJMGH4QCJZR%3A20250406%3A26; g_state={"i_p":1743965297743,"i_l":1}; recentlocations=Los+Angeles%2C+CA%2C+United+States%3B%3BSan+Francisco%2C+CA%3B%3B; location=%7B%22address1%22%3A+%22%22%2C+%22accuracy%22%3A+4%2C+%22place_id%22%3A+%221214%22%2C+%22latitude%22%3A+34.052393%2C+%22parent_id%22%3A+371%2C+%22city%22%3A+%22Los+Angeles%22%2C+%22min_latitude%22%3A+33.9547806%2C+%22max_latitude%22%3A+34.1682093%2C+%22state%22%3A+%22CA%22%2C+%22provenance%22%3A+%22YELP_GEOCODING_ENGINE%22%2C+%22display%22%3A+%22Los+Angeles%2C+CA%22%2C+%22unformatted%22%3A+%22Los+Angeles%2C+CA%2C+United+States%22%2C+%22location_type%22%3A+%22locality%22%2C+%22min_longitude%22%3A+-118.4896057%2C+%22country%22%3A+%22US%22%2C+%22zip%22%3A+%22%22%2C+%22address2%22%3A+%22%22%2C+%22longitude%22%3A+-118.24368%2C+%22max_longitude%22%3A+-118.1529362%2C+%22county%22%3A+%22Los+Angeles+County%22%2C+%22address3%22%3A+%22%22%2C+%22borough%22%3A+%22%22%2C+%22confident%22%3A+null%2C+%22isGoogleHood%22%3A+false%2C+%22language%22%3A+null%2C+%22neighborhood%22%3A+%22%22%2C+%22polygons%22%3A+null%2C+%22usingDefaultZip%22%3A+false%7D; _uetsid=89fd4db0130411f0b59be1acef5dc0a4; _uetvid=89fd5da0130411f0913903815671498d; OptanonConsent=isGpcEnabled=0&datestamp=Sun+Apr+06+2025+22%3A33%3A32+GMT%2B0500+(Pakistan+Standard+Time)&version=202403.1.0&browserGpcFlag=0&isIABGlobal=false&identifierType=Cookie+Unique+Id&hosts=&consentId=0a7f32f4-6c1d-4510-9d5d-4402f9b34353&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.yelp.com%2Fbiz%2Fshakeys-pizza-parlor-san-gabriel-2%3Fosq%3DShakey%2527s+Pizza+Parlor&groups=BG122%3A1%2CC0003%3A1%2CC0002%3A1%2CC0001%3A1%2CC0004%3A1' \
   --compressed \
  -o $1.txt
