import time
import os
import winsound  # For Windows, use 'os.system("afplay tone.mp3")' for macOS

def set_alarm():
    print("Enter the alarm time in 24-hour format (HH:MM):")
    alarm_time = input("Time: ")
    
    print("Enter the path to your custom tone (e.g., tone.mp3):")
    tone_path = input("Tone path: ")
    
    print("Set snooze duration in minutes (e.g., 5):")
    snooze_duration = int(input("Snooze time: "))
    
    while True:
        current_time = time.strftime("%H:%M")
        if current_time == alarm_time:
            print("Alarm ringing!")
            play_tone(tone_path)
            if snooze_option(snooze_duration):
                alarm_time = add_snooze(alarm_time, snooze_duration)
            else:
                break
        time.sleep(30)  # Check every 30 seconds

def play_tone(tone_path):
    if os.path.exists(tone_path):
        if os.name == 'nt':  # Windows
            winsound.PlaySound(tone_path, winsound.SND_FILENAME)
        else:  # macOS/Linux
            os.system(f"afplay {tone_path} &")
    else:
        print("Tone file not found!")

def snooze_option(snooze_duration):
    while True:
        print(f"Snooze for {snooze_duration} minutes? (yes/no):")
        choice = input().lower()
        if choice in ['yes', 'no']:
            return choice == 'yes'
        print("Please enter 'yes' or 'no'.")

def add_snooze(alarm_time, snooze_duration):
    hours, minutes = map(int, alarm_time.split(':'))
    total_minutes = hours * 60 + minutes + snooze_duration
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60
    return f"{new_hours:02d}:{new_minutes:02d}"

if __name__ == "__main__":
    print("Alarm Clock Program")
    set_alarm()