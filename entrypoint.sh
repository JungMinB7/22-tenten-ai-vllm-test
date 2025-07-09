#!/bin/sh

if [ "$MODE" = "gcp-prod" ]; then
  python3.11 main.py --mode gcp-prod
else
  python3.11 main.py --mode api-prod
fi