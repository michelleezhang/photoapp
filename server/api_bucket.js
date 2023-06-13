//
// app.get('/bucket?startafter=bucketkey', async (req, res) => {...});
//
// Retrieves the contents of the S3 bucket and returns the 
// information about each asset to the client. Note that it
// returns 12 at a time, use startafter query parameter to pass
// the last bucketkey and get the next set of 12, and so on.
//
const { ListObjectsV2Command } = require('@aws-sdk/client-s3');
const { s3, s3_bucket_name, s3_region_name } = require('./aws.js');

exports.get_bucket = async (req, res) => {

  console.log("call to /bucket...");

  try {
    const params = {
      Bucket: s3_bucket_name,
      MaxKeys: 12,
      StartAfter: req.query.startafter // extract startafter param from query
        };
    const listObjects = async (params) => { 
      const command = new ListObjectsV2Command(params);
      const response = await s3.send(command);
      console.log("/bucket done, sending response...");
      
      if (response.KeyCount == 0) {
        res.json({
          "message": "success",
          "data": []
        });
        return;
      };
      
      res.json({
        "message": "success",
        "data": response.Contents
      });
      return;
    };

  
    listObjects(params);
    
  }//try
  catch (err) {
    res.status(400).json({
      "message": err.message,
      "data": []
    });
    return;
  }//catch

}//get
