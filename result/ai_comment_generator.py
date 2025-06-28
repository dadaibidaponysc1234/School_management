# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# # Globals, initialized as None
# flan_tokenizer = None
# flan_model = None
# grammar_corrector = None

# def load_models():
#     global flan_tokenizer, flan_model, grammar_corrector
#     if flan_tokenizer is None or flan_model is None:
#         flan_tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
#         flan_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
#     if grammar_corrector is None:
#         grammar_corrector = pipeline("text2text-generation", model="prithivida/grammar_error_correcter_v1")

# descriptions = {
#     "Excellent": "shows exceptional commitment",
#     "Very Good": "demonstrates strong ability",
#     "Good": "performs well",
#     "Fair": "shows steady progress",
#     "Average": "is developing steadily"
# }
# priority = ["Excellent", "Very Good", "Good", "Fair", "Average"]

# def generate_teacher_comment(student_skills: dict, gender: str):
    
#     load_models()  # load only when needed

#     pronoun = 'He' if gender.lower() == 'male' else 'She'
#     sorted_skills = sorted(student_skills.items(), key=lambda x: priority.index(x[1]))
#     top_skills = sorted_skills[:3]
#     phrases = [f"{skill} {descriptions[level]}" for skill, level in top_skills]
#     traits_summary = ", ".join(phrases[:-1]) + f", and {phrases[-1]}." if len(phrases) > 1 else phrases[0]

#     prompt = f"""
# You are a teacher writing short, encouraging comments for student report cards.

# 🧠 Guidelines:
# - The comment should reflect **at least two or one specific traits** such as neatness, punctuality, empathy, teamwork, honesty, or leadership.
# - NEVER describe the student as a teacher or mention teaching.
# - Avoid vague phrases like "doing well", "a good student", or "making good use of time".
# - Write in a clear, concise sentence using the correct pronoun: {"He" if gender == "male" else "She"}.
# - Use skill names or their meanings (e.g., "responsible", "neat", "respectful", "hardworking", etc.).
# - Base the comment on the student's traits below.
# - Avoid vague phrases like “doing well”, “a good student”, or “makes good use of time”.
# - Be concise (1 sentence), encouraging, and use correct grammar.
# - Use the correct pronoun: {"He" if gender == "male" else "She"}.
# - Do NOT use generic terms like "person", "student", or "individual".

# Traits: {traits_summary}
# Comment:
# """

#     inputs = flan_tokenizer(prompt, return_tensors="pt", truncation=True)
#     outputs = flan_model.generate(
#         **inputs,
#         max_length=60,
#         do_sample=True,
#         top_k=50,
#         top_p=0.92,
#         temperature=0.8,
#         num_return_sequences=1
#     )
#     raw_comment = flan_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

#     if "The student" in raw_comment:
#         raw_comment = raw_comment.replace("The student", pronoun)
#     elif not (raw_comment.startswith("He") or raw_comment.startswith("She")):
#         raw_comment = f"{pronoun} {raw_comment[0].lower() + raw_comment[1:]}"

#     corrected = grammar_corrector(raw_comment, max_length=64, clean_up_tokenization_spaces=True)[0]['generated_text']
#     return corrected

def generate_teacher_comment(student_skills: dict, gender: str):
    print("Good ")