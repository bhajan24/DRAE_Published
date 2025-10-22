const { Lambda } = require("@aws-sdk/client-lambda");
const { fromCognitoIdentityPool } = require("@aws-sdk/credential-provider-cognito-identity");
const { CognitoIdentityClient } = require("@aws-sdk/client-cognito-identity");

const REGION = "us-east-1";
const IDENTITY_POOL_ID = "us-east-1:896efff8-cd15-4b26-a376-189b81e902f8";
const LAMBDA_FUNCTION_NAME = "StudentUploadLambda";

async function testUpload() {
  try {
    console.log("🧪 Testing Lambda upload functionality...");
    
    const lambdaClient = new Lambda({
      region: REGION,
      credentials: fromCognitoIdentityPool({
        client: new CognitoIdentityClient({ region: REGION }),
        identityPoolId: IDENTITY_POOL_ID,
      }),
    });

    const params = {
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: new TextEncoder().encode(
        JSON.stringify({
          body: JSON.stringify({
            filename: "test-upload.pdf",
            contentType: "application/pdf",
            studentId: "test-student"
          })
        })
      ),
    };

    console.log("📤 Invoking Lambda function...");
    const response = await lambdaClient.invoke(params);
    const payload = JSON.parse(new TextDecoder().decode(response.Payload));
    
    console.log("✅ Lambda Response:", JSON.stringify(payload, null, 2));
    
    if (payload.statusCode === 200) {
      const presignedData = JSON.parse(payload.body);
      console.log("🔗 Presigned URL generated:", presignedData.uploadUrl.substring(0, 100) + "...");
      console.log("📁 S3 Key:", presignedData.key);
      console.log("🪣 Bucket:", presignedData.bucket);
    }
    
  } catch (error) {
    console.error("❌ Test failed:", error.message);
  }
}

testUpload();
