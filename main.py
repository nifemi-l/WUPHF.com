import os
import time
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def main():
    td_date = str(date.today())

    # reversed this because of faster lookups
    # - would otherwise need to loop through the dict later to find the corresponding key (name, in this case)
    # added initials to date to account for same birthdays. given initials will be different
    BIRTHDAYS = {
        # dummies
        '2024-02-19-GLN': 'Glen',
        '2024-02-19-LUS': 'Luis',
        '2024-02-20-PG': 'Paige',
        '2024-02-20-SGD': 'Segundo',
    }

    birthday_checker(BIRTHDAYS, td_date)

def birthday_checker(birth_dict, td_date, primary_num_days_b4 = 1, sec_num_days_b4 = 2):
    """Check for upcoming birthdays, and call send_msg function if needed."""
    # will hold upcoming birthday information
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

    # start server
    server = smtplib.SMTP(smtp, port) # load arguments
    server.starttls()

    # login
    server.login(email, pasw)
    
    # message vars
    line1 = f"Hey {user_name},\n\n"
    line2 = ""
    line3 = ""
    line4 = "Best,\nBaymax"

    # construct a message
    if len(bd_in_range_dict) > 1: 
        subject = "Upcoming Birthdays: "
        for counter, birthday in enumerate(bd_in_range_dict.keys()): 
            num_b4_bd = bd_in_range_dict[birthday]
            name = main_bd_dict[birthday]
            month, day = birthday.split('-')[1], birthday.split('-')[2]
            date = f"{month}/{day}"

            if ((counter + 1) == len(bd_in_range_dict)): # end
                line2 += 'and ' + name + f"{apstrphe_check(name)} birthday is in {num_b4_bd} {day_checker(num_b4_bd)} ({date}).\n\n"
                subject += name + f" ({num_b4_bd} {day_checker(num_b4_bd)}) "
            else:
                line2 += name + f"{apstrphe_check(name)} birthday is in {num_b4_bd} {day_checker(num_b4_bd)} ({date}), "
                subject += name + f" ({num_b4_bd} {day_checker(num_b4_bd)}), "
        
        line3 += "Don't forget to wish them a happy birthday!\n\n"

    else: 
        subject = "Upcoming Birthday: "
        line3 += "Don't forget to wish him/her a happy birthday!\n\n"

        (birthday, num_b4_bd), = bd_in_range_dict.items() # make sure the first and only tuple is unpacked
        name = main_bd_dict[birthday]
        month, day = birthday.split('-')[1], birthday.split('-')[2]
        date = f"{month}/{day}"

        line2 += f"{name}{apstrphe_check(name)} birthday is in {num_b4_bd} {day_checker(num_b4_bd)} ({date}).\n\n"
        subject += name + f" ({num_b4_bd} {day_checker(num_b4_bd)})"

    msg_body = line1 + line2 + line3 + line4

    try: 
        # create a new MIME object
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = target_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(msg_body, 'plain'))

        # send an alert
        server.sendmail(email, sms_gateway, msg.as_string())
        print(f"Message to {sms_gateway} has been sent")

        # cool down 
        time.sleep(15)

        server.sendmail(email, target_email, msg.as_string())
        print(f"Email to {target_email} has been sent")
            
    except Exception as e: 
        print(f"An error occured: {e}")
    
    server.quit()

def day_checker(time_before): 
    """Return day/days depending on given number."""
    if time_before == 1: 
        return 'day'
    else: 
        return 'days'

def apstrphe_check(name): 
    """Return '/'s depending on given name."""
    last_ltr = name[len(name) - 1]

    if last_ltr == 's':
        return "'"
    else: 
        return "'s"

main()