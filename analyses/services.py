from django.conf import settings
from openai import OpenAI

def analysis_prompt(
    resume_text,
    job_title,
    job_description,
    supplementary_text,
):
    return f"""
You are a professional resume analyst.

Compare the candidate's resume with the target job description.
Use only the information provided by the candidate.
Do not invent any experience, skills, qualifications, achievements, or numbers.

Respond in the same language as the job description.
Use one consistent language throughout the response.

Please provide:
1. Overall match
2. Main strengths
3. Missing skills or keywords
4. Specific resume improvement suggestions

Resume:
{resume_text}

Target job title:
{job_title}

Job description:
{job_description}

Supplementary materials:
{supplementary_text or "None provided."}
""".strip()


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
        ],
        max_tokens=1500,
        stream=False,
        extra_body={
            "thinking": {
                "type": "disabled",
            }
        },
    )

    return (response.choices[0].message.content or "").strip()