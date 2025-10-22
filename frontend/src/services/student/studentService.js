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

export const submitApplication = async (applicationData) => {
  try {
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "submit_application",
        "input": applicationData
      }]
    };

    const response = await lambdaClient.invoke({
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: JSON.stringify(payload),
    });

    const result = JSON.parse(new TextDecoder().decode(response.Payload));
    
    if (result.status_code === 200) {
      return { success: true, application: result.application };
    } else {
      return { success: false, error: result.error || 'Failed to submit application' };
    }

  } catch (error) {
    console.error('Submit application failed:', error);
    return { success: false, error: error.message };
  }
};

export const getStudentApplications = async () => {
  try {
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "list_wishlist"
      }]
    };

    const response = await lambdaClient.invoke({
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: JSON.stringify(payload),
    });

    const result = JSON.parse(new TextDecoder().decode(response.Payload));
    
    if (result.status_code === 200) {
      return result.result || [];
    } else {
      return [];
    }

  } catch (error) {
    console.error('Get student applications failed:', error);
    return [];
  }
};

export const updateWishlist = async (applicationData) => {
  try {
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "update_wishlist",
        "input": {
          "wishlist_data": {
            "application_id": applicationData.application_id || `APP-2025-${Date.now()}`,
            "university_name": applicationData.university_name,
            "location_preference": applicationData.location_preference,
            "program": applicationData.program,
            "status": applicationData.status || "",
            "report": applicationData.report || "Open",
            "applied_on": applicationData.applied_on || new Date().toISOString()
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
    
    if (result.status_code === 200) {
      return { success: true, data: result };
    } else {
      return { success: false, error: result.error || 'Failed to update wishlist' };
    }

  } catch (error) {
    console.error('Update wishlist failed:', error);
    return { success: false, error: error.message };
  }
};

export default { submitApplication, getStudentApplications, updateWishlist };
