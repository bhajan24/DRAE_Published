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

export const listApplications = async () => {
  try {
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "list_applicants_v2",
        "input": {}
      }]
    };

    const response = await lambdaClient.invoke({
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: JSON.stringify(payload),
    });

    const result = JSON.parse(new TextDecoder().decode(response.Payload));
    
    if (result.status_code === 200) {
      return {
        success: true,
        applications: result.result,
        stats: {
          total: result.result.length,
          new: result.result.filter(app => app.application_status === 'New').length,
          processing: result.result.filter(app => app.application_status?.includes('Processing')).length,
          accepted: result.result.filter(app => app.final_decision === 'ACCEPT').length
        }
      };
    } else {
      return { success: false, error: 'Failed to fetch applications' };
    }

  } catch (error) {
    console.error('List applications failed:', error);
    return { success: false, error: error.message };
  }
};

export const processApplication = async (applicationId) => {
  try {
    console.log(`📤 Processing application: ${applicationId}`);
    
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "process_application",
        "input": {
          "application_id": applicationId
        }
      }]
    };

    console.log(`📋 Payload:`, payload);

    const response = await lambdaClient.invoke({
      FunctionName: LAMBDA_FUNCTION_NAME,
      InvocationType: "RequestResponse",
      Payload: JSON.stringify(payload),
    });

    const result = JSON.parse(new TextDecoder().decode(response.Payload));
    console.log(`📥 Lambda response:`, result);
    
    if (result.status_code === 200 || result.success) {
      return { 
        success: true, 
        message: result.message || 'Application processing started successfully',
        data: result
      };
    } else {
      return { 
        success: false, 
        error: result.error || result.message || 'Failed to start processing' 
      };
    }

  } catch (error) {
    console.error('❌ Process application failed:', error);
    return { 
      success: false, 
      error: `Service error: ${error.message}` 
    };
  }
};

export const getApplication = async (applicationId) => {
  try {
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "get_application",
        "input": {
          "application_id": applicationId
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
      return { success: true, application: result.application };
    } else {
      return { success: false, error: result.error || 'Failed to get application' };
    }

  } catch (error) {
    console.error('Get application failed:', error);
    return { success: false, error: error.message };
  }
};

export const getEvaluation = async (applicationId) => {
  try {
    const payload = {
      "Records": [{
        "eventSource": "student-application",
        "action": "get_evaluation",
        "input": {
          "application_id": applicationId
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
      return { success: true, evaluation: result.evaluation };
    } else {
      return { success: false, error: result.error || 'Failed to get evaluation' };
    }

  } catch (error) {
    console.error('Get evaluation failed:', error);
    return { success: false, error: error.message };
  }
};

export default { listApplications, processApplication, getApplication, getEvaluation };
