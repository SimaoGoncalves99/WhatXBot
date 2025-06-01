import pywhatkit as kit
import datetime

def send_to_group(group_id: str, message: str):
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute + 1  # give time to open browser
    kit.sendwhatmsg_to_group(group_id, message, hour, minute)