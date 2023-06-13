//
// app.get('/download/:assetid', async (req, res) => {...});
//
// downloads an asset from S3 bucket and sends it back to the
// client as a base64-encoded string.
//
const dbConnection = require('./database.js')
const { GetObjectCommand } = require('@aws-sdk/client-s3');
const { s3, s3_bucket_name, s3_region_name } = require('./aws.js');

exports.get_download = async (req, res) => {

  console.log("call to /download...");

  try {
    // extract assetid parameter from url 
    var asset_id = req.params.assetid;

    var sql = 'SELECT * FROM assets WHERE assetid = ?'
    dbConnection.query(sql, [asset_id], async (err, results, _) => {
      if (err) {
        res.status(400).json({
            "message": err.message,
            "user_id": -1,
            "asset_name": "?",
            "bucket_key": "?",
            "data": []
          });
        return;
      }
      var sql_result = await results;

      if (sql_result.length == 0) {
        // if assetid is invalid
        res.json({
          "message": "no such asset...",
          "user_id": -1,
          "asset_name": "?",
          "bucket_key": "?",
          "data": []
        });
        return;
      };
      
      user_id = sql_result[0].userid;
      asset_name = sql_result[0].assetname;
      bucket_key = sql_result[0].bucketkey;
      
      // Download item from S3 bucket
      var params = {
        Bucket: s3_bucket_name,
        Key: bucket_key 
      };

      const listObjects = async (params) => {
        try {
          console.log('hey', params)
          const command = new GetObjectCommand(params);
          const response = await s3.send(command);
          var datastr = await response.Body.transformToString("base64");
          console.log("/bucket done, sending response...");
          
          res.json({
            "message": "success",
            "user_id": user_id,
            "asset_name": asset_name,
            "bucket_key": bucket_key,
            "data": datastr
          });
          return;
        
        } catch (err) {
          res.status(400).json({
            "message": err.message,
            "user_id": -1,
            "asset_name": "?",
            "bucket_key": "?",
            "data": []
          });
          return;
        };
      };
      
      listObjects(params);
    
    })

  }//try
  catch (err) {
    //
    // generally we end up here if we made a 
    // programming error, like undefined variable
    // or function:
    //
    res.status(400).json({
      "message": err.message,
      "user_id": -1,
      "asset_name": "?",
      "bucket_key": "?",
      "data": []
    });
    return;
  }//catch

}//get