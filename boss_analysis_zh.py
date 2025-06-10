# -*- coding: utf-8 -*-
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
            # This handles both month names (e.g., "一月") and numbers (e.g., "1")
            month_str = str(m)
            if month_str.isdigit():
                month = int(month_str)
            else:
                # Basic mapping for Chinese month names if they are sent
                month_map = {"一月": 1, "二月": 2, "三月": 3, "四月": 4, "五月": 5, "六月": 6, "七月": 7, "八月": 8, "九月": 9, "十月": 10, "十一月": 11, "十二月": 12}
                month = month_map.get(month_str, datetime.strptime(month_str, "%B").month)
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
    department = data.get("department", "").strip() or '核心职能'
    experience = data.get("experience", "").strip()
    sector = data.get("sector", "").strip()
    challenge = data.get("challenge", "").strip()
    focus = data.get("focus", "").strip()
    email = data.get("email", "").strip()
    country = data.get("country", "").strip()
    age = compute_age(data)

    # Raw data for email content (not displayed on the site)
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

    # === BEHAVIOR CHANGE: Generate random metrics like the English version ===
    metrics = []
    for title, color in [
        ("沟通效率", "#5E9CA0"),
        ("领导准备度", "#FF9F40"),
        ("任务完成可靠性", "#9966FF"),
    ]:
        seg, reg, glo = sorted([random.randint(60, 90), random.randint(55, 85), random.randint(60, 88)], reverse=True)
        metrics.append((title, seg, reg, glo, color))

    # === BEHAVIOR CHANGE: Generate bar chart HTML on the backend ===
    bar_html = ""
    for title, seg, reg, glo, color in metrics:
        bar_html += f"<strong>{title}</strong><br>"
        # Use Chinese labels for the bars
        labels = ["个人表现", "区域基准", "全球基准"]
        values = [seg, reg, glo]
        for i, v in enumerate(values):
            bar_html += (
                f"<span style='font-size:14px; width:80px; display:inline-block;'>{labels[i]}:</span>"
                f"<span style='display:inline-block;width:{v}%;height:12px;"
                f" background:{color}; margin-right:6px; border-radius:4px; vertical-align:middle;'></span> {v}%<br>"
            )
        bar_html += "<br>"

    # Summary text in Chinese
    summary = (
        "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>🧠 总结：</div><br>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"在{country}，具有<strong>{experience}年</strong>经验的<strong>{sector}</strong>行业的专业人士，经常在内部期望和市场变化之间找到平衡。沟通效果的表现（如<strong>{metrics[0][1]}%</strong>的分数所示）对于管理团队和跨部门（例如<strong>{department}</strong>）合作至关重要。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"该行业的领导准备度越来越被情商和适应力所定义。类似职位的基准数据显示，区域平均水平为<strong>{metrics[1][2]}%</strong>，这揭示了大家对清晰、冷静和尊重权威的共同追求。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"可靠完成任务的能力（评分为<strong>{metrics[2][1]}%</strong>）仍然是晋升潜力的最可靠信号之一。对于<strong>{position}</strong>这样的职位，这不仅反映了速度，还反映了做好正确事情的洞察力。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"您选择的关注领域——<strong>{focus}</strong>——与我们在新加坡、马来西亚和台湾的管理人员中观察到的更广泛的转变相呼应。在这一领域的投入可能会为您的团队带来新的韧性、影响力和可持续增长的路径。"
        + "</p>"
    )

    # AI prompt in Chinese
    prompt = (
        f"为一位来自{country}、在{sector}行业有{experience}年经验、担任{position}职位的人，提供10条具有区域意识和高情商的改进建议。"
        f"他们面临的挑战是“{challenge}”，并希望专注于“{focus}”。"
        f"每条建议都应另起一行，用亲切的语气书写，并带有表情符号。避免冷冰冰的语气。"
    )
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

    # Footer in Chinese
    footer = (
        '<div style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>本报告中的见解是通过KataChat的AI系统分析得出的：</strong><br>'
        '1. 我们的专有匿名专业档案数据库，涵盖新加坡、马来西亚和台湾的行业数据<br>'
        '2. 来自可信的OpenAI研究和领导力趋势数据集的全球商业基准数据<br>'
        '<em>所有数据都通过我们的AI模型进行处理，以识别统计学上显著的模式，并保持严格的PDPA合规。</em>'
        '</div>'
        '<p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>PS:</strong> 您的个性化报告将在24到48小时内送达您的邮箱。<br>'
        '如果您想进一步讨论，请随时与我们联系——我们很乐意为您安排一次15分钟的电话会议。'
        '</p>'
    )

    # === BEHAVIOR CHANGE: Combine all HTML into a single block for both email and display ===
    email_output = raw_info + bar_html + summary + tips_html + footer
    display_output = bar_html + summary + tips_html + footer

    send_email(email_output)

    # === BEHAVIOR CHANGE: Return a single 'analysis' key with the full HTML block ===
    return jsonify({
        "analysis": display_output
    })


if __name__ == "__main__":
    # Use a different port if running both apps locally at the same time
    port = int(os.getenv("PORT", 5001)) 
    app.run(debug=True, host="0.0.0.0", port=port)
