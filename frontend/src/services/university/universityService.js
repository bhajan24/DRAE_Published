import { Lambda } from "@aws-sdk/client-lambda";
import { fromCognitoIdentityPool } from "@aws-sdk/credential-provider-cognito-identity";
import { CognitoIdentityClient } from "@aws-sdk/client-cognito-identity";

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

export const reviewApplication = async (applicationId, decision) => {
  try {
    const payload = {
      "Records": [{
        "eventSource": "university-review",
        "action": "review_application",
        "input": {
          "application_id": applicationId,
          "decision": decision
        }
      }]
    };

    const response = await lambdaClient.invoke({
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: JSON.stringify(payload),
    });

    const result = JSON.parse(new TextDecoder().decode(response.Payload));
    
    if (result.status_code === 200) {
      return { success: true, review: result.review };
    } else {
      return { success: false, error: result.error || 'Failed to review application' };
    }

  } catch (error) {
    console.error('Review application failed:', error);
    return { success: false, error: error.message };
  }
};

export default { reviewApplication };
