#!/bin/bash

ngrok config add-authtoken "$NGROK_AUTH_TOKEN"

ngrok http frontend:8501 > /tmp/ngrok.log &

sleep 5

# In URL từ log ra màn hình
grep -o 'https://[a-z0-9]*\.ngrok.io' /tmp/ngrok.log | head -n 1

tail -f /dev/null