
# pip install pywhatkit, luego cerrar visual studio code y volver a abrir
# pip install --upgrade --no-deps --force-reinstall pywhatkit
# dependency conflicts.
# pyppeteer 1.0.2 requires urllib3<2.0.0,>=1.25.8, but you have urllib3 2.1.0 which is incompatible.

import pywhatkit as kit

# Specify the phone number (with country code) and the message
phone_number = "+542657448534"
message = "Hello from Python! This is an instant WhatsApp message."

# Send the message instantly
kit.sendwhatmsg_instantly(phone_number, message)