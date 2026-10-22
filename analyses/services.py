"""
AI Usage Declaration:
-This file contains code generated with help of AI tools.
-Tool Used: ChatGPT
-Date Generated: 2026-08
-ChatGPT was used to assist in building the basic code framework for the DeepSeek and OpenAI model-calling functions. 
the author configured the models, output formats, token limits, reasoning effort, and other specific parameters, 
and further adjusted and optimised these settings based on subsequent testing.

I have reviewed, tested, and understood the AI-generated code.
"""

import json
from pathlib import Path  # help with file path construction

from django.conf import settings
from openai import OpenAI

def analysis_prompt( # assemble prompt
    resume_text,
    job_title,
    job_description,
    supplementary_text,
):
    # services.py is in analyses, so locate the prompt file from here
    prompt_path = (
        Path(__file__).resolve().parent
        / "prompts"
        / "cv_analyse.txt"
    )

    # locate JSON output example file
    json_example_path = (
        Path(__file__).resolve().parent
        / "json_example.json"
    )

    # read prompt template
    prompt_template = prompt_path.read_text(encoding="utf-8")
    # read JSON structure example
    json_example = json_example_path.read_text(encoding="utf-8")

    # replace placeholders with actual user-submitted content
    return prompt_template.format(
        resume_text=resume_text,
        job_title=job_title,
        job_description=job_description,
        supplementary_text=supplementary_text,
        json_example=json_example,
    ).strip()


def call_deepseek(
    resume_text,
    job_title,
    job_description,
    supplementary_text,
):
    prompt = analysis_prompt(
        resume_text,
        job_title,
        job_description,
        supplementary_text,
    )

    client = OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",
    )

    response = client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a careful and professional career advisor.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],  #deepseek调用时必须带这个参数，gpt可以不选instruction

        # ask ds to use JSON output mode
        response_format={
            "type": "json_object",
        },
                
        temperature=0,  # reduce randomness, from 1 to 0

        reasoning_effort="max",  # none, low, high, max

        max_tokens=20000,

        stream=False,
    )

    # The content returned by the model is essentially still a string
    response_text = (
        response.choices[0].message.content or ""
    ).strip()   

    # Convert the JSON string into a Python dictionary for easy access by key
    return json.loads(response_text)


def call_openai( 
    resume_text,
    job_title,
    job_description,
    supplementary_text,
):
    prompt = analysis_prompt(
        resume_text,
        job_title,
        job_description,
        supplementary_text,
    )

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url="https://api.openai.com/v1",
    )

    response = client.responses.create(
        model=settings.OPENAI_MODEL,
        instructions=(
            "You are a careful and professional career advisor. "
            "Return the result as one valid JSON object."
        ),  # 对于gpt来说该参数是可选的，input已经包含了实际任务
        input=prompt,
        reasoning={
            "effort": "low",
        },
        text={
            "format": {
                "type": "json_object",
            },
        },
        max_output_tokens=6000,
        store=False,
    )

    response_text = response.output_text.strip()

    return json.loads(response_text)