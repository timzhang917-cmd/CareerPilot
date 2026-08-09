import json

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

    # 定位 JSON 输出示例文件
    json_example_path = (
        Path(__file__).resolve().parent
        / "json_example.json"
    )

    # 读取独立保存的提示词模板
    prompt_template = prompt_path.read_text(encoding="utf-8")
    # 读取固定的 JSON 结构示例
    json_example = json_example_path.read_text(encoding="utf-8")

    # 把占位符替换成当前用户实际提交的内容
    return prompt_template.format(
        resume_text=resume_text,
        job_title=job_title,
        job_description=job_description,
        supplementary_text=supplementary_text or "None provided.",
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
        ],

        # 要求 DeepSeek 使用 JSON 输出模式
        response_format={
            "type": "json_object",
        },

        # 降低生成随机性，让相同输入的结果尽量稳定
        temperature=0,

        max_tokens=6000,
        stream=False,
        extra_body={
            "thinking": {
                "type": "disabled",
            }
        },
    )

    # 模型返回的内容本质上仍是一段字符串
    response_text = (
        response.choices[0].message.content or ""
    ).strip()   

    # 把 JSON 字符串转换成 Python 字典，方便后续按 key 取值
    return json.loads(response_text)