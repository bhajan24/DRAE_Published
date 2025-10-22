from tools.eval_framework import AggregatedEvaluation
import json
import logging

import boto3
from botocore.config import Config as BotocoreConfig
from bedrock_agentcore.runtime import BedrockAgentCoreApp

from strands import Agent
from strands.models import BedrockModel
from strands_tools import calculator, current_time, python_repl

from config import (
    AWS_REGION, BEDROCK_MODEL_ID, BOTO_CONFIG, LOG_LEVEL,
    PROGRAM_DETAILS_FILE, EVALUATION_FRAMEWORK_FILE
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

with open(PROGRAM_DETAILS_FILE, "r") as f:
    pgm = f.read()

with open(EVALUATION_FRAMEWORK_FILE, "r") as f:
    requirements = f.read()

agent = Agent(model=bedrock_model,
             system_prompt=f"""You are university university admissions officer who is in charge of processing student applications, specifically for the following program:
{pgm}

The following are the guidelines for analysis and scoring.
{requirements}

Perform all levels of evaluation even if the current step fails.
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
        user_input = payload.get("prompt")

        if not user_input:
            logger.warning("No prompt found in payload")
            return {
                "error": "No prompt provided in payload"
            }
        logger.info("Calling agent with user input")
        result = agent(
    f"""
{user_input} 
    """
)

        result = agent.structured_output(
                                        AggregatedEvaluation,
                                        f"""
                                    {user_input} 
                                        """
                                    )
        logger.info("Structured output generated successfully")
    except Exception as ex:
        print(f"Error {ex}")
        return {
            "error": f"{ex}"
        }
    return result.model_dump()


if __name__ == "__main__":
    app.run()
