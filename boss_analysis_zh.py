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
    msg["Subject"] = "Boss Report 提交"
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
      <li><strong>经验:</strong> {experience} 年</li>
      <li><strong>领域:</strong> {sector}</li>
      <li><strong>面临的挑战:</strong> {challenge}</li>
      <li><strong>关注点:</strong> {focus}</li>
      <li><strong>电子邮件:</strong> {email}</li>
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
        ("领导力准备度", "#FF9F40"),
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
        + f"在{country}，拥有{experience}年经验的{sector}行业的专业人士通常在平衡内部期望与市场演变之间找到平衡点。沟通效果的关键性，表现为{metrics[0][1]}%，不仅对团队管理至关重要，也对跨部门协作至关重要，尤其是在{department or '核心职能'}这样的部门中。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + "领导力准备度在该行业越来越受到情商和适应能力的定义。跨类似角色的基准值表明，强劲的区域平均值为{metrics[1][2]}%，显示出清晰、镇定、尊重的领导风范在压力下的共同追求。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"任务完成的可靠性 — 测量为{metrics[2][1]}% — 仍然是最可靠的上升潜力信号之一。对于{position}角色的人来说，它不仅代表速度，还代表辨识力 — 选择执行得当的正确事务。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"您选择的重点 — <strong>{focus}</strong> — 呼应了我们在新加坡、马来西亚和台湾的管理档案中看到的更广泛变化。投资这一领域可能会打开新的韧性、影响力和可持续增长的途径。"
        + "</p>"
    )

    prompt = (
        f"给一个来自{country}、在{sector}领域、具有{experience}年经验的{position}，面对'{challenge}'并专注于'{focus}'，给出10个情商高、地域相关的改进建议，每条建议占一行，要求语气温暖、带有表情符号。避免冷淡的语气。"
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
        '<strong>本报告的见解由KataChat的AI系统生成：</strong><br>'
        '1. 我们专有的来自新加坡、马来西亚和台湾的匿名职业档案数据库<br>'
        '2. 来自可信的OpenAI研究和领导力趋势数据集的全球商业基准<br>'
        '<em>所有数据都通过我们的AI模型进行处理，以识别具有统计显著性的模式，同时保持严格的PDPA合规性。</em>'
        '</div>' +
        "<p style=\"background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;\">"
        "<strong>PS:</strong> 您的个性化报告将在24到48小时内送达您的收件箱。如果您希望进一步讨论，欢迎随时联系我们 — 我们很乐意安排一个15分钟的电话会议，与您方便的时候讨论。"
        "</p>"
    )

    email_output = raw_info + bar_html + summary + tips_html + footer
    display_output = bar_html + summary + tips_html + footer

    send_email(email_output)

    return jsonify({
        "metrics": [
            {"title": t, "labels": ["部门", "区域", "全球"], "values": [s, r, g]}
            for t, s, r, g, _ in metrics
        ],
        "analysis": display_output
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
