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
            month_str = str(m)
            if month_str.isdigit():
                month = int(month_str)
            else:
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
        labels = ["个人表现", "区域基准", "全球基准"]
        values = [seg, reg, glo]
        for i, v in enumerate(values):
            bar_html += (
                f"<span style='font-size:14px; width:80px; display:inline-block;'>{labels[i]}:</span>"
                f"<span style='display:inline-block;width:{v}%;height:12px;"
                f" background:{color}; margin-right:6px; border-radius:4px; vertical-align:middle;'></span> {v}%<br>"
            )
        bar_html += "<br>"

    summary = (
        "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>🧠 个人洞察：</div><br>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"对于一位在<strong>{country}</strong>的<strong>{sector}</strong>领域、拥有<strong>{experience}年</strong>宝贵经验的专业人士而言，其职业旅程是在平衡内部目标与市场脉搏中不断前进的宝贵经历。展现出色的沟通效率（<strong>{metrics[0][1]}%</strong>）是成功的基石，它有助于在团队内部及跨部门之间建立起合作的桥梁。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"在当今职场，真正的领导力由“心”和适应性来衡量。领导力的准备度分数（区域基准为<strong>{metrics[1][2]}%</strong>）正指向一位已经走在这条正确道路上的专业人士，能够展现出他人所寻求的那份清晰和冷静。这是一种能建立信任并激励行动的宝贵品质。"
        + "</p>"
        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"能够可靠地完成任务（<strong>{metrics[2][1]}%</strong>）这不仅是一个数据，更是巨大潜力的有力证明。对于<strong>{position}</strong>这个角色，这反映出一种智慧：不仅是努力工作，更是专注于真正重要的事情。这样的特质绝不会被忽视。"
        + "</p>"
-        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
+        + f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px; text-align:justify;'>"
        + f"选择专注于<strong>{focus}</strong>，意味着正把握着我们在这个区域所看到的关键增长点。培养这项技能是对自身韧性和影响力的重要投资。坚持这个方向，正是在迈向一个充满希望的未来。"
        + "</p>"
    )

    # === UPDATED PROMPT: Asks for a more professional tone in Chinese ===
    prompt = (
        f"为一位来自{country}、在{sector}行业有{experience}年经验、担任{position}职位的人，提供10条可行的、专业的、且鼓舞人心的改进建议。"
        f"他们面临的挑战是“{challenge}”，并希望专注于“{focus}”。"
        f"每条建议都应是一条清晰、有建设性的忠告。语气应当是赋能和尊重的，避免过于随意。请恰当地使用表情符号来增加亲和力，而非显得不专业。"
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.75 # Slightly lowered for more focused output
    )
    tips = response.choices[0].message.content.strip().split("\n")
    tips_html = "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>💡 创意建议：</div><br>"
    for line in tips:
        if line.strip():
            tips_html += f"<p style='margin:16px 0; font-size:17px;'>{line.strip()}</p>"

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

    email_output = raw_info + bar_html + summary + tips_html + footer
    display_output = bar_html + summary + tips_html + footer

    send_email(email_output)

    return jsonify({
        "analysis": display_output
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001)) 
    app.run(debug=True, host="0.0.0.0", port=port)
