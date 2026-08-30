#!/bin/bash
curl -T /tmp/hives/system.save http://10.10.15.183:9002/system.save
touch /tmp/sys_forwarded