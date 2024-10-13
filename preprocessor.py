import re
import pandas as pd
import streamlit as st


def preprocess(data):
    # Replace non-breaking spaces and handle lowercase am/pm
    data = data.replace('\u202f', ' ')  # Replace non-breaking spaces
    data = data.replace('am', 'AM').replace('pm', 'PM')  # Handle lowercase AM/PM

    # Pattern to split date and messages in the chat (handles single and double digits)
    pattern = r'\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}\s[APM]{2}\s+-\s'

    # Split messages and extract dates
    messages = re.split(pattern, data)[1:]  # Skip the first empty split
    dates = re.findall(pattern, data)

    # Check if messages and dates are extracted correctly
    # st.write("Messages:", messages)
    # st.write("Dates:", dates)

    # Create a DataFrame for messages and dates
    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date to datetime format with 'dayfirst=True' for ambiguous date formats
    df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%y, %I:%M %p - ', errors='coerce',
                                        dayfirst=True)
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Extract users and messages
    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:  # If the entry has a username
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            if "Messages and calls are end-to-end encrypted" in message or "added" in message or "changed" in message:
                users.append('system_notification')  # System messages
            else:
                users.append('group_notification')  # Other notifications
            messages.append(message)

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Add additional columns for analysis
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create time period for analysis (e.g., 10-11, 11-12, etc.)
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append(str(hour) + "-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{hour}-{hour + 1}")

    df['period'] = period

    # Display the processed DataFrame (optional)

    return df