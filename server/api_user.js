// inserts a new user or updates an existing user
// app.put('/user', async (req, res) => {...});
//
// Inserts a new user into the database, or if the
// user already exists (based on email) then the
// user's data is updated (name and bucket folder).
// Returns the user's userid in the database.
//
const dbConnection = require('./database.js')

exports.put_user = async (req, res) => {

  console.log("call to /user...");

  try {
    // rows of users are
    // userid
    // email
    // lastname
    // firstname
    // bucketfolder
    
                               
    // client makes a put request, passing in JSON data
    // "data" is that JSON object
    var data = req.body;  // data => json object
    
    // search for the email with SQL
    var email_input = data["email"];
    var sql = 'SELECT * FROM users WHERE email = ?';
    
    dbConnection.query(sql, [email_input], async (err, results, _) => {
      if (err) {
         res.status(400).json({
            "message": "ERROR",
            "userid": -1
            });
          return;
      }
      var sql_result = await results;

      if (sql_result.length == 0) {
        // if the email doesn't exist, insert a new user
        
        var insert_sql = 'INSERT INTO users (email, lastname, firstname, bucketfolder) VALUES (?, ?, ?, ?)';
        dbConnection.query(insert_sql, [email_input, data["lastname"], data["firstname"], data["bucketfolder"]], async (err, insert_result, _) => {
          if (err) {
            res.status(400).json({
            "message": "ERROR",
            "userid": -1
            });
            return;
          };

          res.json({
            "message": "inserted",
            "userid": insert_result.insertId
          });
          return;
        });  
      }
      else {
        // if the email exists, update the user
        var update_sql = 'UPDATE users SET lastname = ?, firstname = ?, bucketfolder = ? WHERE email = ?';
        dbConnection.query(update_sql, [data["lastname"], data["firstname"], data["bucketfolder"], data["email"]], async (err, update_res, _) => {
          if (err) {
            res.status(400).json({
            "message": "ERROR",
            "userid": -1
            });
            return;
          };
          
          dbConnection.query('SELECT userid FROM users WHERE email = ?', [data["email"]], async (err, userid, _) => {
          if (err) {
            res.status(400).json({
            "message": "ERROR",
            "userid": -1
            });
            return;
          };
  
          res.json({
            "message": "updated",
            "userid": userid[0].userid
          });
          return;
        }); 
          }); 
    
      };
    });

    console.log("/user done, sending response...");


    
    
  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "userid": -1
    });
  }//catch

}//put
