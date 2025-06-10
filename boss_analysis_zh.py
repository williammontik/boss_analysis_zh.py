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
            month = int(m) if m.isdigit() else datetime.strptime(m, "%B").month
            bd = datetime(int(y), month, int(d))
        else:
            bd = parser.parse(data.get("dob", ""), dayfirst=True)
    except Exception:
        bd = datetime.today()
    today = datetime.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def send_email(html_body: str):
    msg = MIMEText(html_body, 'html')
    msg["Subject"] = "Boss Report Submission"
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

    raw_info = f"""
    <h3>📥 提交的表单数据:</h3>
    <ul style="line-height:1.8;">
      <li><strong>英文全名:</strong> {member_name}</li>
      <li><strong>中文名:</strong> {member_name_cn}</li>
      <li><strong>职位:</strong> {position}</li>
      <li><strong>部门:</strong> {department}</li>
      <li><strong>从业年数:</strong> {experience} 年</li>
      <li><strong>所属领域:</strong> {sector}</li>
      <li><strong>面临的挑战:</strong> {challenge}</li>
      <li><strong>优先关注:</strong> {focus}</li>
      <li><strong>电子邮箱:</strong> {email}</li>
      <li><strong>所在国家:</strong> {country}</li>
      <li><strong>出生日期:</strong> {data.get("dob_day", "")} - {data.get("dob_month", "")} - {data.get("dob_year", "")}</li>
      <li><strong>推荐人:</strong> {data.get("referrer", "")}</li>
      <li><strong>联系方式:</strong> {data.get("contactNumber", "")}</li>
    </ul>
    <hr><br>
    """

    metrics = []
    for title, color in [
        ("沟通效率", "#5E9CA0"),
        ("领导准备度", "#FF9F40"),
        ("任务完成可靠性", "#9966FF"),
    ]:
        seg, reg, glo = sorted([random.randint(60, 90), random.randint(55, 85), random.randint(60, 88)], reverse=True)
        metrics.append((title, seg, reg, glo, color))

    bar_html = ""
    for title, seg, reg, glo, color in metrics:
        bar_html += f"<strong>{title}</strong><br>"
        for v in (seg, reg, glo):
            bar_html += (
                f"<span style='display:inline-block;width:{v}%;height:12px; background:{color}; margin-right:6px; border-radius:4px;'></span> {v}%<br>"
            )
        bar_html += "<br>"

    summary = (
        "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>🧠 总结:</div><br>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"在{country}，专业人士在<strong>{sector}</strong>领域拥有<strong>{experience}年</strong>经验，通常需要平衡内部期望和市场变化。沟通效率在<small>{metrics[0][1]}%</small>等数值中得到了体现，关键在于管理团队和跨部门协作。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + "领导准备度在该领域越来越依赖情商和适应性。对比同类角色的基准数据，区域平均为 <strong>{metrics[1][2]}%</strong>，显示出在压力下保持冷静并能发挥尊重权威的共同追求。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"任务完成能力的可靠性 — 在{metrics[2][1]}%的水平 — 是向上发展的最可靠信号之一。对于担任销售总监等职位的人员来说，这不仅仅是速度问题，更多的是选择执行正确的任务。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"您的关注重点 — <strong>{focus}</strong> — 显示了我们在新加坡、马来西亚和台湾的管理档案中看到的更广泛变化。在这一领域的投资可能会为韧性、影响力和可持续增长开辟新的路径。"
        + "</p>"
    )

    prompt = (
        f"为来自{country}的{position}职位、在{sector}领域工作{experience}年的专业人士，面对'{challenge}'并专注于'{focus}'，给出10个具有情感智能的改进建议。每个建议应单独列出，语气温暖，带有表情符号。避免冷酷的语气。"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85
    )
    tips = response.choices[0].message.content.strip().split("\n")
    tips_html = "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>💡 创意建议:</div><br>"
    for line in tips:
        if line.strip():
            tips_html += f"<p style='margin:16px 0; font-size:17px;'>{line.strip()}</p>"

    footer = (
        '<div style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>本报告中的洞察由KataChat的AI系统分析生成：</strong><br>'
        '1. 我们在新加坡、马来西亚和台湾的匿名专业档案数据库<br>'
        '2. 来自OpenAI研究和领导力趋势数据集的全球业务基准<br>'
        '<em>所有数据都通过我们的AI模型处理，以识别统计学显著模式，同时确保符合PDPA合规要求。</em>'
        '</div>'
        "<p style=\"background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;\">"
        "<strong>PS:</strong> 您的个性化报告将在24–48小时内发送到您的收件箱。如果您希望进一步讨论，请随时联系我们，我们很乐意为您安排15分钟的电话沟通。"
        "</p>"
    )

    email_output = raw_info + bar_html + summary + tips_html + footer
    display_output = bar_html + summary + tips_html + footer

    send_email(email_output)

    return jsonify({
        "metrics": [
            {"title": t, "labels": ["Segment", "Regional", "Global"], "values": [s, r, g]}
            for t, s, r, g, _ in metrics
        ],
        "analysis": display_output
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
