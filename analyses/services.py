from pathlib import Path  # 帮程序构造文件路径

from django.conf import settings
from openai import OpenAI

def analysis_prompt(
    resume_text,
    job_title,
    job_description,
    supplementary_text,
):
    # services.py 所在目录就是 analyses，因此从这里定位提示词文件
    prompt_path = (
        Path(__file__).resolve().parent
        / "prompts"
        / "cv_analyse.txt"
    )

    # 读取独立保存的提示词模板
    prompt_template = prompt_path.read_text(encoding="utf-8")

    # 把四个占位符替换成当前用户实际提交的内容
    return prompt_template.format(
        resume_text=resume_text,
        job_title=job_title,
        job_description=job_description,
        supplementary_text=supplementary_text or "None provided.",
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