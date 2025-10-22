import { Lambda } from "@aws-sdk/client-lambda";
import { fromCognitoIdentityPool } from "@aws-sdk/credential-provider-cognito-identity";
import { CognitoIdentityClient } from "@aws-sdk/client-cognito-identity";

// AWS Configuration
const REGION = "us-east-1";
const IDENTITY_POOL_ID = "us-east-1:896efff8-cd15-4b26-a376-189b81e902f8";
const LAMBDA_FUNCTION_NAME = "sagemaker-uni-university-persona";

const lambdaClient = new Lambda({
  region: REGION,
  credentials: fromCognitoIdentityPool({
    client: new CognitoIdentityClient({ region: REGION }),
    identityPoolId: IDENTITY_POOL_ID,
  }),
});

export const submitApplication = async (applicationData) => {
  try {
    // Use the exact autofill response structure and add application_id
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "submit_application",
        "input": {
          "application_id": applicationData.application_id,
          "application_form": {
            "application_id": applicationData.application_id,
            "submitted_date": new Date().toISOString(),
            ...applicationData // Spread the entire autofill response
          }
        }
      }]
    };

    const response = await lambdaClient.invoke({
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: JSON.stringify(payload),
    });

    const result = JSON.parse(new TextDecoder().decode(response.Payload));
    
    return {
      success: true,
      data: result
    };

  } catch (error) {
    console.error('Application submission failed:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

export default { submitApplication };
