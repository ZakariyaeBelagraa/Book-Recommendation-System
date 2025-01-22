import smtplib
from email.message import EmailMessage
import os

def send_email(sender_email, sender_password, recipient_email, subject, message, attachment_path=None):

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        email = EmailMessage()
        email["From"] = sender_email
        email["To"] = recipient_email
        email["Subject"] = subject

        email.set_content(message, subtype="html")

        if attachment_path and os.path.isfile(attachment_path):
            with open(attachment_path, "rb") as file:
                email.add_attachment(
                    file.read(),
                    maintype="application",
                    subtype="octet-stream",
                    filename=os.path.basename(attachment_path),
                )

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(email)
            print("Email sent successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_book_recommendation_email(user_name, book_title, recommended_books):

    recommendations_list = "<ul>"
    for book in recommended_books:
        recommendations_list += f"<li>{book}</li>"
    recommendations_list += "</ul>"

    message = f"""
    <html>
        <body>
            <h2>Hello {user_name},</h2>
            <p>We noticed you were interested in the book: <strong>{book_title}</strong>.</p>
            <p>Based on that, we thought you might like these recommendations:</p>
            {recommendations_list}
            <p>Happy reading!</p>
            <p>Best regards,<br>Your Book Recommendation Team</p>
        </body>
    </html>
    """
    return message


def send_book_recommendations(recipient_email, user_name, book_title, recommended_books):
    sender_email="EmailGoesHere" # put your email here
    sender_password="PasswordGoesHere" # put your password here
    subject = f"Book Recommendations based on your interest in '{book_title}'"
    message = generate_book_recommendation_email(user_name, book_title, recommended_books)
    send_email(sender_email, sender_password, recipient_email, subject, message)


