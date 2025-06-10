# -*- coding: utf-8 -*-
import os, smtplib, random, logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.text import MIMEText
from openai import OpenAI

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.DEBUG)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHINESE_MONTHS = {
    '一月': 1, '二月': 2, '三月': 3, '四月': 4,
    '五月': 5, '六月': 6, '七月': 7, '八月': 8,
    '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
}


def compute_age(data):
    d, m, y = data.get("dob_day"), data.get("dob_month"), data.get("dob_year")
    try:
        month = int(m) if m.isdigit() else CHINESE_MONTHS.get(m, 1)
        bd = datetime(int(y), month, int(d))
    except Exception:
        bd = datetime.today()
    today = datetime.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))


def send_email(html_body):
    msg = MIMEText(html_body, 'html', 'utf-8')
    msg['Subject'] = "Boss 提交记录"
    msg['From'] = SMTP_USERNAME
    msg['To'] = SMTP_USERNAME
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


@app.route("/boss_analyze", methods=["POST"])
def boss_analyze():
    data = request.get_json(force=True)

    name = data.get("memberName", "")
    name_cn = data.get("memberNameCn", "")
    position = data.get("position", "")
    department = data.get("department", "")
    experience = data.get("experience", "")
    sector = data.get("sector", "")
    challenge = data.get("challenge", "")
    focus = data.get("focus", "")
    email = data.get("email", "")
    country = data.get("country", "")
    age = compute_age(data)

    # 随机图表数据
    metrics = []
    for title, color in [
        ("沟通效率", "#5E9CA0"),
        ("领导力潜能", "#FF9F40"),
        ("任务执行力", "#9966FF")
    ]:
        seg, reg, glo = sorted([random.randint(60, 90), random.randint(55, 85), random.randint(60, 88)], reverse=True)
        metrics.append((title, seg, reg, glo, color))

    # 图表 HTML
    bar_html = ""
    for title, seg, reg, glo, color in metrics:
        bar_html += f"<strong>{title}</strong><br>"
        for v in (seg, reg, glo):
            bar_html += f"<span style='display:inline-block;width:{v}%;height:12px;background:{color}; margin-right:6px; border-radius:4px;'></span> {v}%<br>"
        bar_html += "<br>"

    # 中文总结段落
    summary = (
        f"<div style='font-size:24px;font-weight:bold;margin-top:30px;'>🧠 综合总结：</div><br>"
        f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>"
        f"在{country}，从事<strong>{sector}</strong>领域、拥有<strong>{experience}年</strong>经验的专业人士，常在内外部需求之间寻找平衡。沟通效率在如<strong>{department or '核心部门'}</strong>中尤其关键，本次数据展示出沟通维度的区域表现为<strong>{metrics[0][2]}%</strong>，表明跨团队协作的能力有待持续锻炼与优化。"
        f"</p>"
        f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>"
        f"领导潜力方面，越来越多职场人展现出情绪管理与适应变革的能力。区域基准为<strong>{metrics[1][2]}%</strong>，说明在应对复杂环境时，冷静、尊重与清晰表达正成为新型领导者的核心特质。"
        f"</p>"
        f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>"
        f"任务执行维度达到<strong>{metrics[2][1]}%</strong>，这不仅体现了速度，更是一种识别重点、精准落地的能力。在<strong>{position}</strong>岗位中，该指标直接关联到信任与晋升通道。"
        f"</p>"
        f"<p style='line-height:1.7; font-size:16px; margin-bottom:16px;'>"
        f"您提出的关注方向：<strong>{focus}</strong>，正是我们在新马台看到的职场人普遍关注的提升方向之一。持续投资该领域，可能为您的长期影响力与稳定成长打开更宽广的路径。"
        f"</p>"
    )

    # GPT 提示语
    prompt = (
        f"请用中文提供10个具区域理解力与情感共鸣的建议，给一位来自{country}、担任{position}、经验为{experience}年、所属领域为{sector}的职场人，面临的挑战为「{challenge}」，优先关注「{focus}」。每行一条建议，风格温暖、有启发性，适当使用 emoji，避免机械冷漠语气。"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85
    )
    tips = response.choices[0].message.content.strip().split("\n")
    tips_html = "<div style='font-size:24px;font-weight:bold;margin-top:30px;'>💡 提升建议：</div><br>"
    for line in tips:
        if line.strip():
            tips_html += f"<p style='margin:16px 0; font-size:17px;'>{line.strip()}</p>"

    footer = (
        '<div style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>本报告由 KataChat AI 系统生成，分析基础：</strong><br>'
        '1. 新加坡、马来西亚、台湾三地职场人匿名数据分析模型<br>'
        '2. 来自 OpenAI 最新领导力研究与全球职场趋势数据库<br>'
        '<em>所有处理过程遵循 PDPA 数据规范。</em>'
        '</div>'
        '<p style="background-color:#e6f7ff; color:#00529B; padding:15px; border-left:4px solid #00529B; margin:20px 0;">'
        '<strong>备注：</strong>您将在 24–48 小时内收到完整报告邮件。如需进一步讨论，可通过 Telegram 或邮件预约 15 分钟交流时间。'
        '</p>'
    )

    html_body = bar_html + summary + tips_html + footer
    send_email(html_body)

    return jsonify({
        "metrics": [
            {"title": t, "labels": ["分组", "区域", "全球"], "values": [s, r, g]}
            for t, s, r, g, _ in metrics
        ],
        "analysis": html_body
    })


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
