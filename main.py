from flask import Flask, request, jsonify, render_template, session
import mysql.connector
from openai import OpenAI
import random
import os

# Initialize Chatbot API

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Connect to MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        password="zahab",
        database="medBot"
    )

# Fetch a random case study from any cancer type
def fetch_case_study_with_images():
    db = connect_to_db()
    cursor = db.cursor(dictionary=True)

    # List of tables containing different cancer case studies
    tables = ["lungCancer", "colonCancer", "leukemia", "brainTumor"]  # Add more tables if needed
    random_table = random.choice(tables)

    sql_query = f"SELECT casereport, imageAddress, diagnosis FROM {random_table} ORDER BY RAND() LIMIT 1"
    cursor.execute(sql_query)
    case = cursor.fetchone()
    db.close()

    if not case:
        return {"text": "No case study found.", "images": [], "diagnosis": "Unknown."}
    
    # Read the case study text
    try:
        with open(case['casereport'], 'r', encoding='utf-8') as file:
            case_text = file.read()
    except FileNotFoundError:
        case_text = case['casereport']

    images = case['imageAddress'].split(',') if case['imageAddress'] else []
    return {"text": case_text, "images": images, "diagnosis": case['diagnosis']}

# Generate a chatbot response based on the case study
def generate_chat_response(case_text, user_input):
    prompt = f"""
    Patient case: {case_text}

    You are the patient. The doctor (user) is diagnosing you.
    - Do **not** offer information unless directly asked.
    - Keep answers **brief** unless the doctor asks for details.
    - If asked for test names, only list them.
    - If asked for a diagnosis, say you don’t know.
    - If the doctor diagnoses you, accept it normally.
    - Do **not** start the conversation. Wait for the doctor.
    - If the doctor says \"diagnosis complete\", provide a final response and then generate feedback.
    
    Doctor: {user_input}
    Patient:
    """
    
    response = client.chat.completions.create(
        model="gpt-4o", temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a medical chatbot simulating a patient. The user is a medical student diagnosing you. Respond realistically as a patient, but do not offer additional details unless asked."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

# Generate feedback summary
def generate_feedback_summary(conversation, diagnosis):
    feedback_prompt = f"""
    Below is a conversation between a medical student (doctor) and a chatbot (patient) based on a real medical case.
    The chatbot acted as a patient, and the student attempted to diagnose the condition.
    
    Conversation:
    {conversation}
    
    The correct diagnosis was: {diagnosis}
    
    
    Please evaluate the student's performance. Consider:
    - Did the student ask the right diagnostic questions?
    - Did they correctly diagnose the patient?
    
    
    Give a performance rating out of 10 and provide constructive feedback.
    """
    response = client.chat.completions.create(
        model="gpt-4o", temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a medical evaluator providing feedback on medical student consultations."},
            {"role": "user", "content": feedback_prompt}
        ]
    )
    return response.choices[0].message.content

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')  # Ensure 'index.html' is in the 'templates' folder

@app.route('/get_case')
def get_case():
    session['case_study'] = fetch_case_study_with_images()
    case = session['case_study']
    session['conversation_log'] = ""  # Initialize conversation log
    formatted_images = [f"/static/{img.strip()}" for img in case['images'] if img.strip()]
    return jsonify({"case_text": case['text'], "image_path": formatted_images})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    
    case = session.get('case_study')
    if not case:
        return jsonify({"error": "Case study not found. Please start the simulation first."}), 500

     # Check if user ends the session
    if user_input == "diagnosis complete":
        print("diagnosis complete")
        conversation_log = session.get('conversation_log', "")
        print("Conversation Log:\n", conversation_log)
        feedback = generate_feedback_summary(conversation_log, case['diagnosis'])
        print("✅ Generated Feedback:\n", feedback)

        return jsonify({
            "response": "Consultation complete. Generating feedback...",
            "feedback": feedback
        })

    case_text = case['text']
    response = generate_chat_response(case_text, user_input)
    
    # Log conversation
    session['conversation_log'] += f"Doctor: {user_input}\nPatient: {response}\n\n"
    
    return jsonify({"response": response})

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    """Generate AI-based suggestions for diagnostic questioning."""
    conversation_history = request.json.get('conversation_history', [])
    case_source = session.get('case_source')  # Get the case type

    # General-purpose diagnostic questions
    general_questions = [
        "What brings you in today? Can you describe what's been bothering you?",
        "When did you first notice these symptoms, and have they changed over time?",
        "Have you experienced anything like this before?",
        "On a scale of 1 to 10, how would you rate your pain or discomfort?",
        "Does anything make your symptoms better or worse?",
        "Have you had any recent illnesses, injuries, or stressful events?",
        "Are you currently taking any medications or supplements?",
        "Do you have any allergies, especially to medications or foods?",
        "Has anyone in your family had similar symptoms or any medical conditions I should know about?",
        "How has this been affecting your daily life—work, sleep, appetite?"
    ]

    # Disease-specific questions
    disease_questions = {
        "leukemia": [
            "Have you been feeling unusually tired or weak lately, even after resting?",
            "Have you noticed any unexplained bruising or bleeding, like frequent nosebleeds or bleeding gums?",
            "Have you had any persistent fevers, night sweats, or chills without an obvious cause?",
            "Have you been experiencing frequent infections or feeling sick more often than usual?",
            "Have you noticed any swollen lymph nodes, especially in your neck, armpits, or groin?",
            "Have you had any unexplained weight loss or a loss of appetite recently?",
            "Do you ever feel short of breath or lightheaded, even during mild activity?",
            "Have you had any persistent bone or joint pain that doesn’t seem to go away?",
            "Have you noticed tiny red or purple spots on your skin that weren’t there before?",
            "Has anyone in your family ever been diagnosed with blood disorders or leukemia?"
        ],
        "colonCancer": [
            "Have you noticed any changes in your bowel habits, like persistent diarrhea or constipation?",
            "Have you seen blood in your stool or noticed it looking darker than usual?",
            "Do you often feel bloated, gassy, or like your stomach is cramping without a clear reason?",
            "Have you been experiencing any unexplained weight loss recently?",
            "Do you feel like you’re not completely emptying your bowels after using the restroom?",
            "Have you noticed your stools becoming thinner or more narrow than usual?",
            "Have you been feeling more tired or weak than usual, even after getting enough rest?",
            "Do you experience any persistent nausea, vomiting, or loss of appetite?",
            "Has anyone in your family been diagnosed with colon cancer or polyps before?",
            "Have you had a colonoscopy before, and if so, when was your last one?"
        ],
        "lungCancer": [
            "Have you had a persistent cough that hasn’t gone away or has worsened over time?",
            "Have you noticed any coughing up of blood or rust-colored mucus?",
            "Do you often feel short of breath, even when doing simple activities?",
            "Have you had any chest pain that gets worse with deep breathing, coughing, or laughing?",
            "Have you experienced unexplained weight loss or a loss of appetite recently?",
            "Do you often feel unusually tired or weak, even after resting?",
            "Have you had frequent lung infections, like pneumonia or bronchitis, that don’t seem to fully clear up?",
            "Have you noticed any hoarseness or changes in your voice that have lasted for weeks?",
            "Have you ever been exposed to heavy smoking, secondhand smoke, or harmful chemicals at work?",
            "Has anyone in your family been diagnosed with lung cancer before?"
        ],
        "brainTumor": [
            "Have you been experiencing frequent or worsening headaches, especially in the morning or at night?",
            "Have you noticed any changes in your vision, like blurred or double vision?",
            "Have you had any episodes of dizziness, balance problems, or unexplained falls?",
            "Have you been feeling unusually weak or numb in any part of your body, like your arms or legs?",
            "Have you had any trouble speaking, understanding words, or remembering things lately?",
            "Have you experienced any seizures, even if you’ve never had them before?",
            "Do you feel nauseous or vomit frequently without an obvious reason?",
            "Have you noticed any personality changes, mood swings, or difficulty concentrating?",
            "Do you feel unusually tired or drowsy, even when you’ve had enough sleep?",
            "Has anyone in your family ever been diagnosed with brain tumors or neurological disorders?"
        ]
    }

    suggestions = []

    # Check conversation history for keywords to tailor suggestions
    if conversation_history:
        last_message = conversation_history[-1].lower()

        if "headache" in last_message:
            suggestions.append("Have you experienced any changes in vision or dizziness?")
        elif "fatigue" in last_message:
            suggestions.append("Have you noticed any changes in your appetite or weight?")
        elif "cough" in last_message:
            suggestions.append("Do you have any chest pain, shortness of breath, or coughing up blood?")
        else:
            suggestions.append("Can you provide more details on the patient's medical history?")

    # If the case type is known, mix general and specific questions
    if case_source in disease_questions:
        selected_questions = random.sample(disease_questions[case_source], min(3, len(disease_questions[case_source])))
        suggestions.extend(selected_questions)

    # Add general questions if no specific ones were suggested
    if len(suggestions) < 3:
        additional_questions = random.sample(general_questions, min(3 - len(suggestions), len(general_questions)))
        suggestions.extend(additional_questions)

    return jsonify({"suggestions": suggestions})


@app.route('/end_chat')
def end_chat():
    case = session.get('case_study')
    conversation_log = session.get('conversation_log', "")
    
    if not case:
        return jsonify({"error": "No case study found. Cannot generate feedback."}), 500
    
    feedback = generate_feedback_summary(conversation_log, case['diagnosis'])
    return jsonify({"feedback": feedback})

if __name__ == "__main__":
    app.run(debug=True)
