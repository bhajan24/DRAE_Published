from tools.student_form import MSCAgricultureApplication
from utils.utils import read_text_files_from_s3

import json
import logging

import boto3
from botocore.config import Config as BotocoreConfig
from bedrock_agentcore.runtime import BedrockAgentCoreApp

from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time

from config import (
    AWS_REGION, BEDROCK_MODEL_ID, BOTO_CONFIG, LOG_LEVEL,
    APPLICATION_FORM_TEMPLATE, file_names
)

# Create a boto client config with custom settings
boto_config = BotocoreConfig(**BOTO_CONFIG)

session = boto3.Session(region_name=AWS_REGION)

bedrock_model = BedrockModel(
    model_id=BEDROCK_MODEL_ID,
    boto_session=session,
    boto_client_config=boto_config
)

app = BedrockAgentCoreApp()

# Configure logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

with open(APPLICATION_FORM_TEMPLATE, "r") as f:
    application_form = json.load(f)


agent = Agent(model=bedrock_model,
             system_prompt=f"""You are university admissions officer who is in charge of processing student applications. The students submit their documents and you need to extract necessary information required to fill the application form. 
The application form is as shown in the below json format
{application_form}

If for any parameter of the form the value is absent return an empty string as default value. Do not assume or hallucinate.
""",
tools=[calculator, current_time])


@app.entrypoint
def invoke(payload):
    """Process user input and return a response"""
    logger.info("="*50)
    logger.info("Invoke function called - starting execution")
    logger.debug(f"Received payload keys: {payload.keys()}")
    result = ""
    try:
        s3_bucket_name = payload.get("s3_bucket_name")
        s3_key = payload.get("s3_key")

        logger.info("Calling agent")
        submissions = read_text_files_from_s3(
                        bucket_name=s3_bucket_name,
                        s3_key_prefix=s3_key,
                        file_names=file_names,
                        max_wait_time=20,
                        check_interval=5
                    )
        result = agent.structured_output(
    MSCAgricultureApplication,
    f"""Given below are the contents of the submitted document from the student.
{submissions}

Extract and fill the application form for the student. If for any parameter of the form the value is absent return an empty string as default value. Do not assume or hallucinate.
    """
)
        logger.info("Structured output generated successfully")
        output = result.model_dump()
        output["documents"] = {}
        for file in file_names:
            output["documents"][file] = f"s3://{s3_bucket_name}/{s3_key}{file}.pdf"
            
    except Exception as ex:
        print(f"Error {ex}")
        return {
            "error": f"{ex}"
        }
    return output


if __name__ == "__main__":
    app.run()
