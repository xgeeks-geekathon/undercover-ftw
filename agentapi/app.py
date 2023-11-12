import logging
import sys
import json
import subprocess
from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema.output_parser import StrOutputParser
from datetime import datetime
import requests

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

app = Flask(__name__)
llm = ChatOpenAI(model_name="gpt-4", openai_api_key="ai aiJ", temperature=0)
GITHUB_KEY = 'merds'
REPO_URL = 'github.com/mlimaloureiro/opa-llm.git'


@app.route('/policy', methods=['GET'])
def get_policy():
    body = requests.get('http://policy_bundle/policies.rego')

    return body.content

@app.route('/audit', methods=['GET'])
def get_audit():
    body = requests.get('http://policy_bundle/decision-log.txt')

    return body.content


@app.route('/update_policy', methods=['POST'])
def update_policy():
    record = json.loads(request.data)

    body = requests.get('http://policy_bundle/policies.rego')
    content = str(body.content)

    # read content from file
    template = """Write open policy agent rego code to solve the user's problem.

    Always return the full file with the rego code in Markdown format and change as little as possible, e.g.:

    ```rego
    ....
    ```"""
    prompt = ChatPromptTemplate.from_messages([("system", template), ("human", "{input}")])

    def _sanitize_output(text: str):
        _, after = text.split("```rego")
        return after.split("```")[0]

    chain = prompt | llm | StrOutputParser() | _sanitize_output

    prompt_input = ""
    if record["messages"][0]["role"] == "user":
        prompt_input = record["messages"][0]["content"]
    if len(record["messages"]) > 1:
        if record["messages"][1]["role"] == "user":
            prompt_input = record["messages"][1]["content"]
    if prompt_input == "":
        return 400

    result = chain.invoke({"input": "assume '" + content + "' '" + prompt_input})

    app.logger.info(result)

    git_commit_push(result)

    return result, 201

def git_commit_push(file_content=""):
    if file_content == "":
        return

    policies_file_path = '/project_dir/bundles/policies.rego'
    timestamp = datetime.now().strftime("%H%M%S%f")
    branch_name = "compliance-request-" + timestamp
    subprocess.run(["git", "checkout", "-b", branch_name], cwd="/project_dir")

    # Open the file in write mode
    with open(policies_file_path, 'w') as file:
        # Write the new content to the file
        file.write(file_content)

    subprocess.run(["git", "add", policies_file_path], cwd="/project_dir")
    subprocess.run(["git", "commit", "-m", "apply policy change by AI " + timestamp], cwd="/project_dir")
    subprocess.run(["git", "push", "https://mlimaloureiro:" + GITHUB_KEY + "@" + REPO_URL, branch_name], cwd="/project_dir")
    subprocess.run(["git", "checkout", "main"], cwd="/project_dir")

    return

if __name__ == '__main__':
    app.run(port=5001, debug=True)

