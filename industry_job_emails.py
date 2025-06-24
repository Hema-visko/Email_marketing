




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

@app.route('/job_suggestions', methods=['GET'])
def job_suggestions():
    sent_emails = []
    # Step 1: Get jobs from last 3 days
    recent_jobs_query = """
        SELECT job_title FROM jobs
        WHERE job_created_at >= CURDATE() - INTERVAL 3 DAY
        AND job_status = 1
    """
    cursor.execute(recent_jobs_query)
    recent_jobs = cursor.fetchall()
    print(recent_jobs)
    job_titles = [job['job_title'] for job in recent_jobs]

    if not job_titles:
        return jsonify({"message": "No jobs found in the last 3 days"}), 200

    # Step 2: Find users matching those job titles
    format_strings = ','.join(['%s'] * len(job_titles))
    matching_users_query = f"""
        SELECT DISTINCT user_id, user_name, user_email, user_profile
        FROM users
        WHERE user_profile IN ({format_strings})
    """
    cursor.execute(matching_users_query, job_titles)
    users = cursor.fetchall()
    # print(users)
    # Step 3: For each user, find 5 jobs based on their title (any date)
    suggestions = []

    for user in users:
        user_profile = user['user_profile']

        top_jobs_query = """
            SELECT j.job_id, j.job_title, j.job_created_at, c.company_name
            FROM jobs j
            JOIN company c ON j.company_id = c.company_id
            WHERE j.job_status = 1 AND j.job_title = %s
            ORDER BY j.job_created_at DESC
           limit 5
        """
        cursor.execute(top_jobs_query, (user_profile,))
        top_jobs = cursor.fetchall()
        email_body = render_template(
            "candidate_email.html",
            user_email=user['user_email'], user_name=user['user_name'], user_profile= user['user_profile'],
            top_jobs = top_jobs
        )

        msg = Message(
            subject="Top Jobs Just for You!",
            recipients= 'hemay7192gmail.com',
            html=email_body
        )

        try:
            mail.send(msg)
            sent_emails.append({"user_email": user['user_email'], "status": "sent"})
        except Exception as e:
            sent_emails.append({"user_email": user['user_email'], "status": f"failed - {str(e)}"})

        suggestions.append({
            "user_id": user['user_id'],
            "user_name": user['user_name'],
            "user_email": user['user_email'],
            "user_profile": user['user_profile'],
            "recommended_jobs": top_jobs
        })

    return jsonify({"suggestions  for candidates" : suggestions})

if __name__ == "__main__":
    app.run(debug=True)
