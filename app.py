from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app) 



def get_wednesday_in_range(date_str):
    # ... (same as before, omitted for brevity)
    try:
        date_str = date_str.replace('^', '').replace('*', '').strip()
        parts = re.split(r'-', date_str)
        if len(parts) == 2:
            start = parts[0].strip()
            end = parts[1].strip()
            start_month_day = start.split()
            if len(start_month_day) == 2:
                start_month, start_day = start_month_day
            else:
                return None
            if any(month in end for month in [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ]):
                end_month_day = end.split()
                if len(end_month_day) == 2:
                    end_month, end_day = end_month_day
                else:
                    return None
            else:
                end_month = start_month
                end_day = end
            print(start_month, start_day, end_month, end_day) #remove this line just for testing
            year = 2025
            start_date = datetime.strptime(f"{start_month} {start_day} {year}", "%b %d %Y")
            end_date = datetime.strptime(f"{end_month} {end_day} {year}", "%b %d %Y")
            for i in range((end_date - start_date).days + 1):
                d = start_date + timedelta(days=i)
                if d.weekday() == 2:
                    return d.strftime("%Y-%m-%d")
        else:
            parts = date_str.split()
            if len(parts) == 2:
                month, day = parts
                year = 2025
                d = datetime.strptime(f"{month} {day} {year}", "%b %d %Y")
                return d.strftime("%Y-%m-%d")
    except Exception as e:
        return None
    return None

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    import pdfplumber
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    lines = text.splitlines()
    events = []
    event_keywords = r"(quiz\s*\d+|midterm|final|assignment\s*\d+|project|exam|test)"
    date_pattern = r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*\d{1,2}(?:\s*-\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)?\s*\d{1,2})?(?:\^|\*)?"

    for idx, line in enumerate(lines):
        event_match = re.search(event_keywords, line, re.IGNORECASE)
        if event_match:
            event = event_match.group(0)
            # 1. Try to find a date after the event keyword in the line
            after_event = line[event_match.end():]
            after_date = None
            for m in re.finditer(date_pattern, after_event, re.IGNORECASE):
                after_date = m.group(0)
                break  # take the first date after the event
            # 2. If not found, try to find a date before the event keyword in the line
            before_event = line[:event_match.start()]
            before_date = None
            for m in re.finditer(date_pattern, before_event, re.IGNORECASE):
                before_date = m.group(0)
            # 3. If neither, check the previous line
            prev_date = None
            if not after_date and not before_date and idx > 0:
                prev_line = lines[idx-1]
                prev_date_match = re.search(date_pattern, prev_line, re.IGNORECASE)
                if prev_date_match:
                    prev_date = prev_date_match.group(0)
            # Choose the best date
            date = after_date or before_date or prev_date
            if date:
                date_clean = date.replace('^', '').replace('*', '').strip()
                # For quizzes, get the Wednesday in the week
                if "quiz" in event.lower():
                    quiz_date = get_wednesday_in_range(date_clean)
                    if quiz_date:
                        date_clean = quiz_date
                events.append({
                    "date": date_clean,
                    "event": event.strip(),
                    "full_line": line.strip()
                })

    return jsonify({
        'events': events,
        'matching_lines': [l for l in lines if re.search(event_keywords, l, re.IGNORECASE)],
        'lines': lines[:80],
        'raw_text': text[:1000] + ("..." if len(text) > 1000 else "")
    })

if __name__ == '__main__':
    app.run(debug=True)