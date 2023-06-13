//
// app.get('/users', async (req, res) => {...});
//
// Return all the users from the database:
//
const dbConnection = require('./database.js');

exports.get_users = async (req, res) => {

  console.log("call to /users...");

  try {
    var rds_response = new Promise ((resolve, reject) => {
      console.log("/users: calling RDS...");
      var sql = 'SELECT * FROM users ORDER BY userid ASC';
            dbConnection.query(sql, (err, results, _) => {
        if (err) {
          reject(err);
          return;
        }
        console.log("/users query done");
        resolve(results);
      });
    });
     Promise.all([rds_response]).then(results => {
       var rds_results = results[0];

      console.log("/users done, sending response...");
       res.json({
        "message": "success",
         "data": rds_results
       });
     }).catch(err => {
      // error if RDS failed
      res.status(400).json({
        "message": err.message,
        "data": -1
      });
       return;
     });
    
    // MySQL in JS:
    //   https://expressjs.com/en/guide/database-integration.html#mysql
    //   https://github.com/mysqljs/mysql
  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "data": []
    });
  }//catch

}//get
