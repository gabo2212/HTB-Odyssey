#!/bin/bash
# Reclaim PIDs on odyssey-web
for pid in /proc/[0-9]*; do
  if [[ -r "$pid/cmdline" ]]; then
    cmdline=$(tr '\0' ' ' < "$pid/cmdline" 2>/dev/null)
    case "$cmdline" in
      *agent64*|*chisel*|*curl\ *|*apt-get*|*pip3*|*http.server*|*hive_recv*|*catch_system*|*sys_persist*)
        echo "KILL ${pid##*/} $cmdline"
        kill -9 "${pid##*/}" 2>/dev/null
        ;;
    esac
  fi
done
# keep one node server only
pids=$(pgrep -f '/home/webadmin/aegis/server.js' | sort -n)
set -- $pids
if [ "$#" -gt 1 ]; then
  shift
  echo "KILL extra node $*"
  kill -9 "$@" 2>/dev/null
fi
echo CLEAN_DONE
python3 -c 'print("pyok")'
