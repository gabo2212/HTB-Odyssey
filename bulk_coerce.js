const sql = require("mssql");
(async () => {
  const cfg = {
    user: "aegis_audit_publisher",
    password: "Rxd!Qw6n8sP..2bJ@Wpx-2026",
    server: "172.16.0.11",
    database: "aegis_audit",
    port: 1433,
    options: { encrypt: false, trustServerCertificate: true, enableArithAbort: true },
  };
  try {
    await sql.connect(cfg);
    const r = await sql.query`SELECT IS_SRVROLEMEMBER('bulkadmin') AS bulkadmin, IS_SRVROLEMEMBER('sysadmin') AS sysadmin`;
    console.log(JSON.stringify(r.recordset));
    // Coercion - UNC to web host eth1
    const unc = process.argv[2] || "\\\\172.16.0.12\\x\\test";
    console.log("BULK INSERT to", unc);
    try {
      await sql.query(`EXEC ('BULK INSERT aegis_audit.dbo.audit_ingest_staging FROM ''${unc}'' WITH (DATAFILETYPE = ''char'')')`);
    } catch (e) {
      console.log("bulk err:", e.message);
    }
  } catch (e) {
    console.log("err", e.message);
  }
  process.exit(0);
})();
