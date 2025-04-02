const { Client } = require('pg');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function promptForConnectionDetails() {
  return new Promise((resolve) => {
    console.log('Please enter your Neon database connection details:');
    
    rl.question('Hostname (e.g., ep-xyz-123456.us-east-2.aws.neon.tech): ', (hostname) => {
      rl.question('Database name (default is "neondb"): ', (dbname) => {
        const database = dbname || 'neondb';
        
        rl.question('Username (default is "default"): ', (username) => {
          const user = username || 'default';
          
          rl.question('Password or API key: ', (password) => {
            resolve({
              hostname,
              database,
              user,
              password
            });
          });
        });
      });
    });
  });
}

async function testNeonConnection() {
  try {
    const connectionDetails = await promptForConnectionDetails();
    
    const connectionString = `postgres://${connectionDetails.user}:${connectionDetails.password}@${connectionDetails.hostname}/${connectionDetails.database}?sslmode=require`;
    
    console.log('\nConnecting to Neon database...');
    
    const client = new Client({
      connectionString: connectionString,
    });

    await client.connect();
    console.log('Successfully connected to Neon database!');
    
    const result = await client.query('SELECT NOW()');
    console.log('Current database time:', result.rows[0].now);
    
    await client.end();
    console.log('Connection closed.');
  } catch (error) {
    console.error('Error connecting to Neon database:', error.message);
  } finally {
    rl.close();
  }
}

testNeonConnection();
