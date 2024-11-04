#!/bin/bash

# .env 파일 로드
set -a
source .env
set +a

ERROR_EMOJI=":warning:"
SUCCESS_EMOJI=":tada:"
TITLE="알림"
CHECK_INTERVAL=60
ERROR_MSG="에러: 서버가 중단되었습니다."
SUCCESS_MSG="성공: 서버가 정상 작동 중입니다."

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

# 초기 상태를 undefined로 설정
PREVIOUS_STATUS="undefined"

if [ "$PREVIOUS_STATUS" = "undefined" ]; then
        PAYLOAD="payload={\"channel\": \"$CHANNEL\", \"username\": \"$USERNAME\", \"text\": \"$TITLE \n\n $SUCCESS_MSG\", \"icon_emoji\": \"$SUCCESS_EMOJI\"}"
        /usr/bin/curl -X POST --data-urlencode "$PAYLOAD" "$SLACK_HOOK"
    fi

while true; do
    # API 상태 체크
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")
    

    # 이전 상태가 200이고 현재 상태가 실패일 때만 에러 메시지 전송
    if [ "$PREVIOUS_STATUS" = 200 ] && [ "$RESPONSE" -ne 200 ]; then
        PAYLOAD="payload={\"channel\": \"$CHANNEL\", \"username\": \"$USERNAME\", \"text\": \"$TITLE \n\n $ERROR_MSG\", \"icon_emoji\": \"$ERROR_EMOJI\"}"
        /usr/bin/curl -X POST --data-urlencode "$PAYLOAD" "$SLACK_HOOK"
    fi

    # 이전 상태를 현재 상태로 업데이트
    PREVIOUS_STATUS="$RESPONSE"

    sleep "$CHECK_INTERVAL"
done
