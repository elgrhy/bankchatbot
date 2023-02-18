import csv
import datetime
from datetime import datetime, timedelta

from flask import Flask, request
from twilio.rest import Client

app = Flask(__name__)

#Twilio Account Information
account_sid = 'ACa95e8e0a5d0a63ef1e66ba97e196049e'
auth_token = '09522274cb7b6ed1d2e1721f0ac7ff08'
client = Client(account_sid, auth_token)

# define cities and available time slots
cities = ["Dubai", "RAK", "Sharjah"]
available_time_slots = ["10:00 AM", "11:00 PM","12:00 PM"]

# define name of the CSV file to save appointments
file_name = "appointments.csv"

# define the URL route for the WhatsApp webhook
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    # get the incoming message
    incoming_message = request.values.get("Body", "").lower().strip()

    # get the customer's phone number
    phone_number = request.values.get("From", "")


    # check if message is about company profile change
    if "company profile change" in incoming_message:
        # create a message with list of cities
        city_list = "\n".join(cities)
        message = client.messages.create(
            body=f"Please select a city from the list below for your appointment:\n{city_list}",
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{phone_number}'
            )
        print(message.sid)

    # check if message is a city selection
    elif incoming_message in cities:
        # get the selected city
        city = incoming_message

        # create a message with available time slots
        time_slot_list = "\n".join(available_time_slots)
        message = client.messages.create(
            body=f"Please select a time slot for your appointment in {city}:\n{time_slot_list}",
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{phone_number}'
            )

    # check if message is a time slot selection
    elif incoming_message in available_time_slots:
        # get the selected time slot
        time_slot = incoming_message

        # convert the selected time slot to a datetime object
        scheduled_time = datetime.strptime(time_slot, "%I:%M %p").strftime("%H:%M")

        # check the appointments.csv file and give the next available date
        with open(file_name) as csv_file:
            reader = csv.DictReader(csv_file)
            appointments = [row for row in reader if row['city'] == city and row['time'] == scheduled_time]
            appointment_date = datetime.now().date()
            while len(appointments) > 0:
                appointment_date += timedelta(days=1)
                appointments = [row for row in appointments if row['date'] != appointment_date.strftime("%Y-%m-%d")]
            message = client.messages.create(
            body=f"Appointment scheduled for {appointment_date.strftime('%m/%d/%Y')} at {time_slot} in {city}.",
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{phone_number}'
            )

            # save appointment to CSV file
            with open(file_name, mode='a') as csv_file:
                fieldnames = ['phone_number', 'city', 'time', 'date']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'phone_number': phone_number, 'city': city, 'time': scheduled_time, 'date': appointment_date.strftime("%Y-%m-%d")})

    # handle unrecognized messages
    else:
        message = client.messages.create(
            body="We're sorry, we couldn't understand your message. Please try again.",
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{phone_number}'
            )

    # return the response object
    return

if __name__ == "__main__":
    app.run(debug=True, port=5000)
