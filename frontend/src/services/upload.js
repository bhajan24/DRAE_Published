import { Lambda } from "@aws-sdk/client-lambda";
import { fromCognitoIdentityPool } from "@aws-sdk/credential-provider-cognito-identity";
import { CognitoIdentityClient } from "@aws-sdk/client-cognito-identity";

// AWS Configuration
const REGION = "us-east-1";
const IDENTITY_POOL_ID = "us-east-1:896efff8-cd15-4b26-a376-189b81e902f8";
const LAMBDA_FUNCTION_NAME = "StudentUploadLambda";

const lambdaClient = new Lambda({
  region: REGION,
  credentials: fromCognitoIdentityPool({
    client: new CognitoIdentityClient({ region: REGION }),
    identityPoolId: IDENTITY_POOL_ID,
  }),
});

export const uploadToS3 = async (file, studentId = 'university-student', onProgress) => {
  try {
    // Sanitize studentId to remove spaces and special characters
    const safeStudentId = studentId.replace(/\s+/g, '_').replace(/[^\w\-_.]/g, '');
    
    // Get presigned URL from Lambda
    const params = {
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: new TextEncoder().encode(
        JSON.stringify({
          body: JSON.stringify({
            filename: file.name,
            contentType: file.type,
            studentId: safeStudentId
          })
        })
      ),
    };

    const response = await lambdaClient.invoke(params);
    const payload = JSON.parse(new TextDecoder().decode(response.Payload));
    const presignedData = JSON.parse(payload.body);

    if (payload.statusCode !== 200) {
      throw new Error(presignedData.error || 'Failed to get presigned URL');
    }

    // Upload to S3 using presigned URL
    const uploadResponse = await fetch(presignedData.uploadUrl, {
      method: "PUT",
      body: file,
      headers: { 
        "Content-Type": file.type
      },
    });

    if (!uploadResponse.ok) {
      throw new Error('S3 upload failed');
    }

    return {
      success: true,
      key: presignedData.key,
      bucket: presignedData.bucket,
      url: `https://${presignedData.bucket}.s3.amazonaws.com/${presignedData.key}`
    };

  } catch (error) {
    console.error('Upload failed:', error);
    return { 
      success: false, 
      error: error.message 
    };
  }
};

export default { uploadToS3 };
