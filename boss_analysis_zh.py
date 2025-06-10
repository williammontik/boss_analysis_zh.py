import os
import smtplib
from datetime import datetime
from dateutil import parser
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
        msg["Subject"] = "老板报告提交"
        msg["From"] = SMTP_USERNAME
        msg["To"] = SMTP_USERNAME
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"发送电子邮件时出错: {e}")

def compute_age(data):
    # 处理出生日期
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

@app.route('/boss_analyze', methods=['POST'])
def boss_analyze():
    data = request.get_json(force=True)

    # 获取请求数据
    memberName = data.get('memberName')
    memberNameCn = data.get('memberNameCn')
    position = data.get('position')
    department = data.get('department')
    experience = data.get('experience')
    sector = data.get('sector')
    challenge = data.get('challenge')
    focus = data.get('focus')
    email = data.get('email')
    country = data.get('country')
    dob_day = data.get('dob_day')
    dob_month = data.get('dob_month')
    dob_year = data.get('dob_year')
    referrer = data.get('referrer')
    contactNumber = data.get('contactNumber')

    # 示例分析（你可以根据实际情况替换分析逻辑）
    analysis = f"员工: {memberName}, 职位: {position}, 面临的挑战: {challenge}"

    # 返回分析结果
    return jsonify({
        'analysis': analysis,
        'error': None
    })

if __name__ == '__main__':
    app.run(debug=True)
