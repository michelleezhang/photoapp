//
// app.post('/image/:userid', async (req, res) => {...});
//
// Uploads an image to the bucket and updates the database,
// returning the asset id assigned to this image.
//
const dbConnection = require('./database.js')
const { PutObjectCommand } = require('@aws-sdk/client-s3');
const { s3, s3_bucket_name, s3_region_name } = require('./aws.js');

const uuid = require('uuid');

exports.post_image = async (req, res) => {

  console.log("call to /image...");

  try {
    // extract assetid parameter from url 
    var user_id = req.params.userid

    // check that userid exists
    var userid_sql = 'SELECT bucketfolder FROM users WHERE userid = ?'
    dbConnection.query(userid_sql, [user_id], async (err, results, _) => {
      if (err) {
         res.status(400).json({
            "message": "ERROR",
            "user_id": -1
            });
          return;
      }
       var user_bucket = await results;
      
      if (user_bucket.length == 0) {
        // if no such userid, return with 200
        res.status(200).json({
          "message": "no such user...",
          "assetid": -1
        });
        return;
      }
      else {
        var body = req.body;  // data => JS object
        var data = Buffer.from(body["data"], 'base64');
        // we recieve an image as a base64-encoded string
        // decode our string into raw bytes

        var bucket_name = user_bucket[0].bucketfolder;
        var key = uuid.v4();
        // generate a unique bucket key with UUID v4
        var bucket_key = bucket_name + "/" + key + ".jpg"

        // upload image (data) to S3

        
        const PutObject = async () => {
          const command = new PutObjectCommand({
            Bucket: s3_bucket_name,
            Key: bucket_key,
            Body: data
          });
          try {
            const response = await s3.send(command);

             // insert a new row into the assets table
            // columns are: assetid, userid, assetname, bucketkey

            //  assetid: 1015,
   // userid: 80001,
   // assetname: 'duofrench.jpg',
   // bucketkey: '3059381-3274-44b2-ba6b-5669039496ee/a14de707-9ba4-4f0a-a5f9-e35ce2b9f954.jpg'
            
            var insert_sql = 'INSERT INTO assets (userid, assetname, bucketkey) VALUES (?, ?, ?)';
            dbConnection.query(insert_sql, [user_id, body["assetname"], bucket_key], async (err, insert_result, _) => {
              if (err) {
                res.status(400).json({
                  "message": "Error adding to assets",
                  "assetid": -1
                });
                return;
              };

              res.json({
                "message": "success",
                "assetid": insert_result.insertId
              });
              return;
            });  
          } catch (err) {
            res.status(200).json({
              "message": "Error putting object",
              "assetid": -1
            });
            return;
          }
        };

        PutObject();

      }; 
    });
    



  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "assetid": -1
    });
  }//catch

}//post