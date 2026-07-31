# 临时模拟数据：用于开发 Results 页面
# 等 AI 能稳定返回 JSON 后，这份数据会被真实分析结果替代

SAMPLE_ANALYSIS_RESULT = {
    # 顶部整体匹配结果
    "overall": {
        "score": 72,
        "level": "Good Match",
        "summary": (
        "You are a good developer with good experience in Python and Django development."
        ),
    },

    # 四项分类评分
    "category_scores": {
        "hard_skills": 78,
        "soft_skills": 70,
        "experience": 65,
        "education": 80,
    },

    # 候选人与目标岗位匹配的主要优势
    "strengths": [
        "Experience in Python and Django development",
        "Good understanding of WEB application",
        "Experience in Git and version control",
    ],

    # 候选人相对于目标岗位的主要短板
    "gaps": [
        "Limited experience with cloud platforms",
        "No supporting evidence of a huge and complex project",
        "Limited evidence of front-end framework experience",
    ],

    # 岗位要求与候选人证据的逐条对照
    "requirements": [
        {
            "requirement": "Cook a burger",
            "evidence": (
                "Lead team to complete many projects including "
                "cucumber and bread and beef."
            ),
            "assessment": "Basic Match",
        },
        {
            "requirement": " API development",
            "evidence": (
                "Developed and documented REST APIs using "
                "Django REST Framework."
            ),
            "assessment": "Strong Match",
        },
        {
            "requirement": "Cloud deployment (AWS / Azure / GCP)",
            "evidence": "No supporting evidence found in the resume.",
            "assessment": "Clear Gap",
        },
        {
            "requirement": "testing",
            "evidence": (
                "No testing experience was mentioned."
            ),
            "assessment": "Weak Match",
        },
    ],

    # must fixed issues
    "must_fix_issues": [
        {
            "location": "Work Experience - project description",
            "problem": (
                "The statement 'Improved system performance' "
                "is too vague."
            ),
            "why_it_matters": (
                "The recruiter cannot understand what was improved "
                "or evaluate the candidate's contribution."
            ),
            "suggested_correction": (
                "Explain the specific action taken and add a verified "
                "result or metric if one is available."
            ),
        },
        {
            "location": "Project Experience",
            "problem": (
                "The statement 'Responsible for backend development' "
                "does not describe a specific contribution."
            ),
            "why_it_matters": (
                "A responsibility-only statement does not demonstrate "
                "the candidate's actual technical impact."
            ),
            "suggested_correction": (
                "Describe the backend feature developed, the technology "
                "used, and the verified outcome."
            ),
        },
        {
            "location": "Skills section",
            "problem": (
                "The naming and capitalization of technical skills "
                "are inconsistent."
            ),
            "why_it_matters": (
                "Inconsistent terminology makes the resume appear "
                "less carefully prepared."
            ),
            "suggested_correction": (
                "Use consistent names such as Python, Django, REST API, "
                "and Git throughout the resume."
            ),
        },
    ],

    # 针对目标岗位的进阶优化建议
    "suggestions": [
        {
            "priority": "High",
            "target_section": "Project Experience",
            "recommendation": (
                "Add a project that demonstrates cloud deployment "
                "with AWS or Azure."
            ),
            "reason": (
                "The target role requires cloud platform experience, "
                "but no direct supporting evidence was found."
            ),
        },
        {
            "priority": "Medium",
            "target_section": "Technical Skills",
            "recommendation": (
                "Add verified automated testing experience, such as "
                "PyTest unit tests or integration tests."
            ),
            "reason": (
                "Testing experience would provide stronger evidence "
                "of production-ready development skills."
            ),
        },
        {
            "priority": "Low",
            "target_section": "Project Experience",
            "recommendation": (
                "Include relevant front-end framework experience "
                "if the candidate has used React or Vue."
            ),
            "reason": (
                "Front-end knowledge is not essential, but it could "
                "strengthen the candidate's full-stack profile."
            ),
        },
    ],
}
