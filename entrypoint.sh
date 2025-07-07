#!/bin/sh

if [ "$MODE" = "gcp" ]; then
  python3.11 main.py --mode gcp
else
  python3.11 main.py --mode api-prod
fi