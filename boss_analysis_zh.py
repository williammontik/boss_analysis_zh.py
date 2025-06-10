import os
import smtplib
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "kata.chatbot@gmail.com"
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email(html_body: str):
    try:
        msg = MIMEText(html_body, 'html')
        msg["Subject"] = "Boss Report Submission"
        msg["From"] = SMTP_USERNAME
        msg["To"] = SMTP_USERNAME
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

def compute_age(data):
    d, m, y = data.get("dob_day"), data.get("dob_month"), data.get("dob_year")
    try:
        if d and m and y:
            month = int(m) if m.isdigit() else datetime.strptime(m, "%B").month
            bd = datetime(int(y), month, int(d))
        else:
            bd = datetime.today()
    except Exception:
        bd = datetime.today()
    today = datetime.today()
    return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))

@app.route('/boss_analyze', methods=['POST'])
def boss_analyze():
    data = request.get_json(force=True)

    memberName = data.get('memberName')
    position = data.get('position')
    sector = data.get('sector')
    experience = data.get('experience')
    challenge = data.get('challenge')
    email = data.get('email')
    country = data.get('country')
    dob_day = data.get('dob_day')
    dob_month = data.get('dob_month')
    dob_year = data.get('dob_year')
    referrer = data.get('referrer')
    contactNumber = data.get('contactNumber')

    # Example dynamic chart data (replace with actual logic)
    chart_data = {
        'Communication Efficiency': {
            'label': '沟通效率',
            'values': [84, 80, 58]  # Values for each user/region/sector, dynamically calculated
        },
        'Leadership Readiness': {
            'label': '领导准备度',
            'values': [73, 73, 65]
        },
        'Task Completion Reliability': {
            'label': '任务完成可靠性',
            'values': [84, 61, 58]
        }
    }

    # Example dynamic summary text based on user input (translated)
    analysis_summary = f"""
        在{country}，从事{sector}行业，拥有{experience}年经验的专业人士，常常需要平衡内部期望与市场发展趋势。例如，沟通效率（得分{chart_data['Communication Efficiency']['values'][0]}%）是管理团队和跨职能合作（如招聘）中至关重要的因素。

        领导力的准备度越来越被情商和适应能力所定义。与类似职位的基准对比，显示出强劲的区域平均水平，表明人们正在追求更清晰的目标、沉着冷静的压力应对能力和尊重的领导力。

        可靠的任务完成率（得分{chart_data['Task Completion Reliability']['values'][0]}%）是向上发展的重要信号，尤其对销售总监职位而言，这不仅意味着速度，还需要具备做出正确决策的能力。
    """

    # Example dynamic creative suggestions based on user input
    creative_suggestions = [
        "展现对候选人背景和经验的真正兴趣 🌟",
        "为所有候选人提供一个友好且包容的招聘过程 🤝",
        "在招聘过程中提供清晰透明的沟通 📩",
        "为未被录用的候选人提供个性化反馈，帮助他们改进 💬",
        "庆祝多样性，积极寻求来自不同背景的候选人 🌍",
    ]

    # Example result
    result = {
        'analysis': analysis_summary,
        'creative_suggestions': creative_suggestions,
        'chart_data': chart_data,
        'error': None
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
