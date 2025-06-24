




from flask import Flask, jsonify,  render_template
from flask_mail import Mail, Message
from datetime import date
import mysql.connector
from flask import Flask, render_template_string
import re

app = Flask(__name__)


app.config["MAIL_SERVER"] = "mail.remarkhr.com"  
app.config["MAIL_PORT"] = 465                    
app.config["MAIL_USE_SSL"] = True                
app.config["MAIL_USE_TLS"] = False               
app.config["MAIL_USERNAME"] = "info@remarkhr.com"  
app.config["MAIL_PASSWORD"] = "Remark#2023" 
app.config["MAIL_DEFAULT_SENDER"] = "info@remarkhr.com"

mail = Mail(app)
# app.config["MAIL_SERVER"] = "smtp.gmail.com"
# app.config["MAIL_PORT"] = 587
# app.config["MAIL_USE_TLS"] = True
# app.config["MAIL_USERNAME"] = "hema.visko@gmail.com"
# app.config["MAIL_PASSWORD"] = "hktr cprr fyvl ehlk"  
# app.config['MAIL_DEFAULT_SENDER'] = 'hema.visko@gmail.com'
# mail = Mail(app)

db = mysql.connector.connect(
        host="remark-db.cus0iutxtxoy.ap-south-1.rds.amazonaws.com",
        database="remarkhr",
        user="remarkawsdb",
        password="nHDL]&<P9Oj-~lKvre5d#rUSJKH?",
        port=3306
    )

cursor = db.cursor(dictionary=True)

@app.route('/candidate_suggestions', methods=['GET'])
def candidate_suggestions():
    sent_emails = []

    # Step 1: Get users from last 3 days
    recent_users_query = """
        SELECT user_id, user_name, user_email, user_profile
        FROM users
        WHERE user_created_at >= CURDATE() - INTERVAL 3 DAY
    """
    cursor.execute(recent_users_query)
    recent_users = cursor.fetchall()
    user_profiles = list(set([user['user_profile'] for user in recent_users]))

    if not user_profiles:
        return jsonify({"message": "No recent users found"}), 200

 
    format_strings = ','.join(['%s'] * len(user_profiles))
    matching_jobs_query = f"""
        SELECT j.job_id, j.job_title, j.company_id, c.company_name, c.company_email
        FROM jobs j
        JOIN company c ON j.company_id = c.company_id
        WHERE j.job_status = 1 AND j.job_title IN ({format_strings})
    """
    cursor.execute(matching_jobs_query, user_profiles)
    jobs = cursor.fetchall()

    if not jobs:
        return jsonify({"message": "No matching jobs found"}), 200

    suggestions = []

    for job in jobs:
        job_title = job['job_title']

        # Step 3: For each job title, find top 5 users who match
        top_users = [user for user in recent_users if user['user_profile'] == job_title][:5]

        if not top_users:
            continue

        email_body = render_template(
            "employer_industry.html.",
            company_name=job['company_name'], job_title=job_title,
            # user_name = top_users['user_name'], user_profile=top_users['user_profile']
            top_candidates=top_users
        )

        msg = Message(
            subject=f"Top Candidates for {job_title}",
            # recipients=[job['company_email']],
            recipients=['lalitpatidar23102002@gmail.com'],
            html=email_body
        )

        try:
            mail.send(msg)
            sent_emails.append({"company_email": job['company_email'], "status": "sent"})
        except Exception as e:
            sent_emails.append({"company_email": job['company_email'], "status": f"failed - {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)
