import os
import smtplib
from datetime import datetime
from dateutil import parser
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.text import MIMEText
from openai import OpenAI
import random

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def compute_age(data):
    d, m, y = data.get("dob_day"), data.get("dob_month"), data.get("dob_year")
    try:
        if d and m and y:
            # This logic correctly handles the month number (e.g., '1', '2') from the updated frontend
            month = int(m)
            bd = datetime(int(y), month, int(d))
        else:
            bd = parser.parse(data.get("dob", ""), dayfirst=True)
    except Exception:
        bd = datetime.today()
    today = datetime.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def send_email(html_body: str):
    msg = MIMEText(html_body, 'html')
    msg["Subject"] = "老板报告提交"
    msg["From"] = SMTP_USERNAME
    msg["To"] = SMTP_USERNAME
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


@app.route("/boss_analyze", methods=["POST"])
def boss_analyze():
    data = request.get_json(force=True)

    member_name = data.get("memberName", "").strip()
    member_name_cn = data.get("memberNameCn", "").strip()
    position = data.get("position", "").strip()
    department = data.get("department", "").strip()
    experience = data.get("experience", "").strip()
    sector = data.get("sector", "").strip()
    challenge = data.get("challenge", "").strip()
    focus = data.get("focus", "").strip()
    email = data.get("email", "").strip()
    country = data.get("country", "").strip()
    age = compute_age(data)

    # Raw data for email content
    raw_info = f"""
    <h3>📥 提交的表单数据：</h3>
    <ul style="line-height:1.8;">
      <li><strong>合法姓名：</strong> {member_name}</li>
      <li><strong>中文名：</strong> {member_name_cn}</li>
      <li><strong>职位：</strong> {position}</li>
      <li><strong>部门：</strong> {department}</li>
      <li><strong>经验：</strong> {experience} 年</li>
      <li><strong>行业：</strong> {sector}</li>
      <li><strong>挑战：</strong> {challenge}</li>
      <li><strong>关注领域：</strong> {focus}</li>
      <li><strong>电子邮件：</strong> {email}</li>
      <li><strong>国家：</strong> {country}</li>
      <li><strong>出生日期：</strong> {data.get("dob_day", "")} - {data.get("dob_month", "")} - {data.get("dob_year", "")}</li>
      <li><strong>推荐人：</strong> {data.get("referrer", "")}</li>
      <li><strong>联系方式：</strong> {data.get("contactNumber", "")}</li>
    </ul>
    <hr><br>
    """

    metrics = [
        ("沟通效率", 85, 84, 82, "#5E9CA0"),
        ("领导准备度", 88, 88, 56, "#FF9F40"),
        ("任务完成可靠性", 85, 68, 65, "#9966FF")
    ]

    bar_html = ""
    for title, seg, reg, glo, color in metrics:
        bar_html += f"<strong>{title}</strong><br>"
        for v in (seg, reg, glo):
            bar_html += (
                f"<span style='display:inline-block;width:{v}%;height:12px;"
                f" background:{color}; margin-right:6px; border-radius:4px;'></span> {v}%<br>"
            )
        bar_html += "<br>"

    # Create the full summary text for the email
    summary = (
        "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>🧠 总结：</div><br>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"在{country}，具有{experience}年经验的{sector}行业的专业人士，经常在内部期望和市场变化之间找到平衡。沟通效果的表现（{metrics[0][1]}%）对于管理团队和跨部门合作至关重要，尤其在{department}等部门中。</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"领导准备度在这个行业越来越被情商和适应力所定义，区域基准为{metrics[1][2]}%。</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"可靠完成任务的能力（{metrics[2][1]}%）仍然是晋升潜力的信号。</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"您的关注领域 — {focus} — 反映了新加坡、马来西亚和台湾的管理者趋势。</p>"
    )

    prompt = f"给出10个区域性、情商高、针对{position}的改善建议，来自{country}，经验{experience}年，聚焦在{focus}。"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85
    )
    tips = response.choices[0].message.content.strip().split("\n")
    
    tips_html = "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>💡 创意建议：</div><br>"
    for line in tips:
        if line.strip():
            tips_html += f"<p style='margin:16px 0; font-size:17px;'>{line.strip()}</p>"

    footer = (
        '<div style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>报告由KataChat的AI系统生成：</strong><br>'
        '1. 我们的专有匿名专业档案数据库，涵盖新加坡、马来西亚和台湾的行业数据<br>'
        '2. 来自OpenAI研究和领导力趋势数据集的全球商业基准数据<br>'
        '<em>所有数据都通过我们的AI模型进行处理，以识别统计学上显著的模式，并保持严格的PDPA合规。</em>'
        '</div>'
        "<p style=\"background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;\">"
        "<strong>PS:</strong> 您的个性化报告将在24–48小时内送达您的邮箱。"
        "如果您希望进一步讨论，请随时联系我们，我们愿意为您安排15分钟的电话会议。"
        "</p>"
    )

    # Combine all elements for the email
    email_output = raw_info + bar_html + summary + tips_html + footer
    send_email(email_output)
    
    # === START OF CHANGE ===
    # Create structured data for the JSON response to the frontend
    
    summary_dict = {
        "text": f"在{country}，具有{experience}年经验的{sector}行业的专业人士，经常在内部期望和市场变化之间找到平衡。沟通效果的表现（{metrics[0][1]}%）对于管理团队和跨部门合作至关重要，尤其在{department}等部门中。",
        "text2": f"领导准备度在这个行业越来越被情商和适应力所定义。类似职位的基准数据显示，区域平均为{metrics[1][2]}%，显示了大家对清晰、应对压力时的冷静和尊重权威的共同追求。",
        "text3": f"可靠完成任务的能力（{metrics[2][1]}%）仍然是晋升潜力的一个信号。对于{position}等角色来说，这不仅仅体现了速度，还体现了选择正确的工作执行的洞察力。",
        "text4": f"您选择的关注领域——{focus}——反映了我们在新加坡、马来西亚和台湾的管理者角色中的一个更广泛的转变。投资于这一领域可能为您的团队带来新的韧性、影响力和可持续增长的路径。"
    }

    # The tips are already a list, which is what the frontend expects
    tips_list = [line.strip() for line in tips if line.strip()]

    # Return the structured JSON that the frontend script expects
    return jsonify({
        "metrics": [
            {"title": t, "labels": ["Segment", "Regional", "Global"], "values": [s, r, g]}
            for t, s, r, g, _ in metrics
        ],
        "summary": summary_dict,
        "suggestions": tips_list
    })
    # === END OF CHANGE ===


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
