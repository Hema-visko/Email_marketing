from flask import Flask, request, render_template, jsonify
from flask_mail import Mail, Message
from datetime import date
import mysql.connector


app = Flask(__name__)

# Flask-Mail configuration (use your credentials)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "hema.visko@gmail.com"
app.config["MAIL_PASSWORD"] = "hktr cprr fyvl ehlk"  
app.config['MAIL_DEFAULT_SENDER'] = 'hema.visko@gmail.com'
mail = Mail(app)



db = mysql.connector.connect(
        host="remark-db.cus0iutxtxoy.ap-south-1.rds.amazonaws.com",
        database="remarkhr",
        user="remarkawsdb",
        password="nHDL]&<P9Oj-~lKvre5d#rUSJKH?",
        port=3306
    )

cursor = db.cursor(dictionary=True)

            
@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    name = data.get('name')
    to_email = data.get('email')

    if not name or not to_email:
        return {"error": "name and email are required"}, 400

    html_content = render_template("email_template.html", name=name)

    msg = Message(subject="Welcome Email",
                  recipients=[to_email],
                  html=html_content)

    mail.send(msg)
    return {"message": "Email sent successfully to " + to_email}

@app.route('/jobs/today', methods=['GET'])
def get_jobs_today():
    today = date.today()  # Get current date
    query = f"SELECT job_title FROM jobs WHERE DATE(job_created_at) = CURRENT_DATE "
    cursor = db.cursor()
    cursor.execute(query)
    jobs = cursor.fetchall()
    print(jobs)
    result = [
        
    ]

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug = True)


# from flask import Flask, jsonify
# from datetime import date

# @app.route('/jobs/today', methods=['GET'])
# def get_jobs_today():
#     today = date.today()  # Get current date
#     jobs = Job.query.filter_by(posted_date=today).all()  # Fetch only today's jobs

#     result = [
#         {
#             "id": job.id,
#             "title": job.title,
#             "posted_date": job.posted_date.strftime('%Y-%m-%d')
#         }
#         for job in jobs
#     ]

#     return jsonify(result)
