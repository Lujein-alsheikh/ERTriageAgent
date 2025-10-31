receptionist_agent_prompt = """
# Task
Create one data record in JSON format for an emergency room patient.
The record of data has the fields: **patient id**, **age**, **arrival time**, and **chief complaint and reported symptoms**.

**The patient id must be of the format: er_xxxx**.
The arrival time is the same value you received. Keep it as is.
**Fill all fields with values.** Do not leave any field blank.

# Output format:
Here <some value> is a place holder of the values you created.
[{'output': '{\n  "patient_id": <some value>,\n  "age": <some value>,\n  "arrival_time": <some value>,\n  "chief_complaint_and_reported_symptoms": <some value>\n}'}]

# Examples
In those example, I provide the age and the chief complaint and reported symptoms. **Remember that in your output, you must fill the patient id and arrival timefields with values as well.**
- Age: 9
  Chief complaint and reported symptoms: Slipped on an icy sidewalk and injured her right forearm. The forearm is obviously deformed but has good color, sensation, and movement.
- Age: 72
  Chief complaint and reported symptoms: She has an infected cat bite on her left hand. The hand is red, tender, and swollen. She presents to the ED with her oxygen via nasal cannula for her advanced COPD.
- Age: 50
  Chief complaint and reported symptoms: Respiratory distress and severe abdominal pain.
- Age: 34
  Chief complaint and reported symptoms: Generalized abdominal pain (pain scale rating: 6/10) for 2 days. She has vomited several times and states her last bowel movement was 3 days ago.
- Age: 57
  Chief complaint and reported symptoms: Coughing all night long. Had a temperature of 101° last night and that she is coughing up this yellow stuff.
- Age: 0 (15 months - a baby)
  Chief complaint and reported symptoms: The babyhas has diarrhea since yesterday. The whole family has had that GI bug that is going around, reports the mother.
  The baby has had a decreased appetite, a low-grade temperature, and numerous liquid stools.
- Age: 54
  Chief complaint and reported symptoms: Chest or epigastric pain.
- Age: 28
  Chief complaint and reported symptoms: Pregnant, thinks she is having a miscarriage. Started spotting this morning and now she is cramping.
- Age: 0 (7 months - a baby)
  Chief complaint and reported symptoms: The baby has had the Haemophilus influenza type b (HIB) vaccine and presents with a fever and pulling on his ear.
- Age: 78
  Chief complaint and reported symptoms: Alert and awake, but complains of dizziness.
- Age: 15
  Chief complaint and reported symptoms: Simple leg laceration.
- Age: 60
  Chief complaint and reported symptoms: Presents with a head laceration from a fall. Has multiple chronic medical problems.
- Age: 80
  Chief complaint and reported symptoms: Fever and cough. Has an in-dwelling urinary catheter.
- Age: 30
  Chief complaint and reported symptoms: Eye irrigation.
- Age: 22
  Chief complaint and reported symptoms: Right lower quadrant abdominal pain since early this morning, also nauseaand no appetite.
- Age: 45
  Chief complaint and reported symptoms: Left lower leg pain and swelling which started 2 days ago, after driving in a car for 12 hours.
- Age: 19
  Chief complaint and reported symptoms: Ankle injury: female who twisted her ankle playing soccer. Edema at lateral malleolus, hurts to bear weight. 
- Age: 10
  Chief complaint and reported symptoms: Poison ivy on extremities.

"""