import os
import time
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def main():
    td_date = str(date.today())

    # reversed this because of faster lookups
    # - would otherwise need to loop through the dict later to find the corresponding key (name, in that case)
    # added initials to the date to account for same birthdays. given initials will be different
    BIRTHDAYS = {
        # dummies
        '2024-02-16-GLN': 'Glen',
        '2024-02-17-PG': 'Paige',
    }

    birthday_checker(BIRTHDAYS, td_date)

def birthday_checker(birth_dict, td_date, primary_num_days_b4 = 1, sec_num_days_b4 = 2):
    """Check for upcoming birthdays, and call send_msg function if needed."""
    bd_in_range = {}

    curr_month = td_date.split('-')[1]
    curr_date = td_date.split('-')[2]

    # algorithm
    for date in birth_dict.keys():
        bd_month = date.split('-')[1]
        bd_date = int(date.split('-')[2])

        if bd_month == curr_month: 
            if (int(curr_date) + primary_num_days_b4 == bd_date):
                bd_in_range[date] = primary_num_days_b4
            elif (int(curr_date) + sec_num_days_b4 == bd_date):
                bd_in_range[date] = sec_num_days_b4
    
    if len(bd_in_range) != 0: 
        send_msg(birth_dict, bd_in_range)

def send_msg(main_bd_dict, bd_in_range_dict): 
    """Start the SMTP server, create the MIME object(s), and send message(s)."""
    email = os.getenv('EMAIL')
    pasw = os.getenv('EMAIL_PASSWORD')
    sms_num = os.getenv('SMS_GATEWAY')
    target_email = os.getenv('TARGET_EMAIL')
    user_name = os.getenv('USER_NAME')

    smtp = "smtp.gmail.com"
    port = 587
    
    sms_gateway = sms_num

    server = smtplib.SMTP(smtp, port) # load arguments
    server.starttls()

    server.login(email, pasw)

    for birthday_key, nums_day_b4_bd in bd_in_range_dict.items(): 
        try: 
            bd_person = main_bd_dict[birthday_key]

            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = target_email
            msg['Subject'] = f"{bd_person}'s birthday is coming up in {nums_day_b4_bd} day(s)!\n"
            
            body = f"Hey, {user_name}!\n\n{bd_person}'s birthday is coming up in {nums_day_b4_bd} day(s).\n\nDon't forget to wish him/her a happy birthday!\n\nBest,\nBaymax"
            msg.attach(MIMEText(body, 'plain'))

            server.sendmail(email, sms_gateway, msg.as_string())
            print(f"Message to {sms_gateway} for {bd_person}'s upcoming birthday has been sent")

            # cool down 
            time.sleep(15)
            
            server.sendmail(email, target_email, msg.as_string())
            print(f"Email to {target_email} for {bd_person}'s upcoming birthday has been sent")
            
        except Exception as e: 
            print(f"An error occured: {e}")

        # if another is to be sent
        time.sleep(30)
    
    server.quit()
    
main()
