const fs = require('fs');

const options = {
  apiVersion: 'v1', // default
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN,
  requestOptions: {
    agentOptions: {
      ca: fs.readFileSync(process.env.VAULT_CACERT),
    }
  }
};

const vault = require("node-vault")(options);

async function getEnvVars() {
  const secrets = await vault.read("services/production/circle_jira_webhook");
  return secrets.data;
}

// getEnvVars().then(console.log);

module.exports.env = () => getEnvVars();