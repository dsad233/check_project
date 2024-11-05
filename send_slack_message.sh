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

# 초기 상태를 undefined로 설정
PREVIOUS_STATUS="undefined"

while true; do
    # API 상태 체크
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

    # 초기 실행 or 상태 변경 시에만 메시지 전송
    if [ "$PREVIOUS_STATUS" = "undefined" ] && [ "$RESPONSE" = "200" ]; then
        # 최초 정상 동작 알림
        PAYLOAD="payload={\"channel\": \"$CHANNEL\", \"username\": \"$USERNAME\", \"text\": \"$TITLE \n\n $SUCCESS_MSG\", \"icon_emoji\": \"$SUCCESS_EMOJI\"}"
        /usr/bin/curl -X POST --data-urlencode "$PAYLOAD" "$SLACK_HOOK"
        PREVIOUS_STATUS="$RESPONSE"
    elif [ "$PREVIOUS_STATUS" = "200" ] && [ "$RESPONSE" != "200" ]; then
        # 서버 중단 알림
        PAYLOAD="payload={\"channel\": \"$CHANNEL\", \"username\": \"$USERNAME\", \"text\": \"$TITLE \n\n $ERROR_MSG\", \"icon_emoji\": \"$ERROR_EMOJI\"}"
        /usr/bin/curl -X POST --data-urlencode "$PAYLOAD" "$SLACK_HOOK"
        PREVIOUS_STATUS="$RESPONSE"
    elif [ "$PREVIOUS_STATUS" != "200" ] && [ "$RESPONSE" = "200" ]; then
        # 서버 재시작 알림
        PAYLOAD="payload={\"channel\": \"$CHANNEL\", \"username\": \"$USERNAME\", \"text\": \"$TITLE \n\n $SUCCESS_MSG\", \"icon_emoji\": \"$SUCCESS_EMOJI\"}"
        /usr/bin/curl -X POST --data-urlencode "$PAYLOAD" "$SLACK_HOOK"
        PREVIOUS_STATUS="$RESPONSE"
    fi

    sleep "$CHECK_INTERVAL"
done