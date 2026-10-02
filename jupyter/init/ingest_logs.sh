#!/bin/bash
setsid nohup python /opt/scripts/ingest_logs.py > /tmp/ingest.log 2>&1 &
setsid nohup python /opt/scripts/warmup_and_run.py > /tmp/warmup.log 2>&1 &