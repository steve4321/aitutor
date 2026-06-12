"""Seed KET (Cambridge A2 Key) question bank for all 4 skills.

Populates:
  - Knowledge points for KET English (vocabulary, grammar, reading, writing, listening, speaking)
  - KETQuestion (Reading & Listening — multiple-choice, true/false, matching)
  - KETWritingTask (Part 6 short message, Part 7 story/letter)
  - KETSpeakingTask (Part 1 personal questions, Part 2 discussion)

Note: Course structure (Course → Unit → Lesson) is managed by curriculum_ket.py
      via seed_data.py. This script only seeds the question bank data.

Usage:
    cd backend && python -m scripts.seed_ket_questions
    cd backend && python -m scripts.seed_ket_questions --dry-run
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from uuid import uuid4, UUID

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.db.session import async_session_factory, engine
from app.models.knowledge import KnowledgePoint
from app.models.ket import KETQuestion, KETWritingTask, KETSpeakingTask

logger = logging.getLogger(__name__)

# ============================================================
# KNOWLEDGE POINTS
# ============================================================

KET_KNOWLEDGE_POINTS: list[dict] = [
    # -- Vocabulary pillar --
    {"code": "KET-VOC-01", "subject": "ket_english", "name": "日常生活词汇", "name_en": "Daily Life Vocabulary",
     "description": "Food, drink, clothes, colours, weather, family, rooms, furniture", "pillar": "vocabulary", "difficulty_level": 1},
    {"code": "KET-VOC-02", "subject": "ket_english", "name": "学校与学习词汇", "name_en": "School & Study Vocabulary",
     "description": "Subjects, classroom objects, school places, study actions", "pillar": "vocabulary", "difficulty_level": 1},
    {"code": "KET-VOC-03", "subject": "ket_english", "name": "交通与出行词汇", "name_en": "Transport & Travel Vocabulary",
     "description": "Transport, directions, places in town, travel, tickets", "pillar": "vocabulary", "difficulty_level": 2},
    {"code": "KET-VOC-04", "subject": "ket_english", "name": "健康与身体词汇", "name_en": "Health & Body Vocabulary",
     "description": "Body parts, illness, at the doctor, sport, healthy living", "pillar": "vocabulary", "difficulty_level": 2},
    {"code": "KET-VOC-05", "subject": "ket_english", "name": "娱乐与爱好词汇", "name_en": "Entertainment & Hobbies Vocabulary",
     "description": "Free-time activities, films, music, sport, hobbies", "pillar": "vocabulary", "difficulty_level": 1},
    # -- Grammar pillar --
    {"code": "KET-GRAM-01", "subject": "ket_english", "name": "一般现在时", "name_en": "Present Simple",
     "description": "Affirmative, negative, questions; third-person -s/-es", "pillar": "grammar", "difficulty_level": 1},
    {"code": "KET-GRAM-02", "subject": "ket_english", "name": "现在进行时", "name_en": "Present Continuous",
     "description": "be + verb-ing; contrast with present simple", "pillar": "grammar", "difficulty_level": 1},
    {"code": "KET-GRAM-03", "subject": "ket_english", "name": "一般过去时", "name_en": "Past Simple",
     "description": "Regular -ed, common irregulars, was/were", "pillar": "grammar", "difficulty_level": 2},
    {"code": "KET-GRAM-04", "subject": "ket_english", "name": "将来时表达", "name_en": "Future: going to / will",
     "description": "be going to for plans; will for predictions", "pillar": "grammar", "difficulty_level": 2},
    {"code": "KET-GRAM-05", "subject": "ket_english", "name": "情态动词", "name_en": "Modal Verbs (can, must, should)",
     "description": "can/can't for ability/permission; must/mustn't; should/shouldn't", "pillar": "grammar", "difficulty_level": 2},
    {"code": "KET-GRAM-06", "subject": "ket_english", "name": "比较级与最高级", "name_en": "Comparatives & Superlatives",
     "description": "Short/long adjectives; irregular (good/better/best)", "pillar": "grammar", "difficulty_level": 2},
    {"code": "KET-GRAM-07", "subject": "ket_english", "name": "冠词与量词", "name_en": "Articles & Quantifiers",
     "description": "a/an/the; some/any; much/many/a lot of", "pillar": "grammar", "difficulty_level": 1},
    # -- Reading skill --
    {"code": "KET-RDG-01", "subject": "ket_english", "name": "阅读理解-短文本", "name_en": "Reading: Short Texts (signs, notices)",
     "description": "Understand signs, notices, short messages (Part 1-2)", "pillar": "reading", "difficulty_level": 1},
    {"code": "KET-RDG-02", "subject": "ket_english", "name": "阅读理解-细节匹配", "name_en": "Reading: Matching Details",
     "description": "Match people to texts based on specific details (Part 2)", "pillar": "reading", "difficulty_level": 2},
    {"code": "KET-RDG-03", "subject": "ket_english", "name": "阅读理解-长文本", "name_en": "Reading: Longer Texts",
     "description": "Multiple-choice questions on factual texts (Part 4)", "pillar": "reading", "difficulty_level": 2},
    # -- Writing skill --
    {"code": "KET-WRT-01", "subject": "ket_english", "name": "写作-短消息", "name_en": "Writing: Short Message (25-35 words)",
     "description": "Write a short email, note or message with 3 content points (Part 6)", "pillar": "writing", "difficulty_level": 2},
    {"code": "KET-WRT-02", "subject": "ket_english", "name": "写作-故事或信件", "name_en": "Writing: Story or Letter (35-45 words)",
     "description": "Write a short story based on pictures or an informal letter (Part 7)", "pillar": "writing", "difficulty_level": 2},
    # -- Listening skill --
    {"code": "KET-LST-01", "subject": "ket_english", "name": "听力-识别信息", "name_en": "Listening: Identifying Information",
     "description": "Identify specific information in short dialogues (Part 1-2)", "pillar": "listening", "difficulty_level": 1},
    {"code": "KET-LST-02", "subject": "ket_english", "name": "听力-对话理解", "name_en": "Listening: Understanding Dialogues",
     "description": "Understand main points and details in monologues/dialogues (Part 3-4)", "pillar": "listening", "difficulty_level": 2},
    # -- Speaking skill --
    {"code": "KET-SPK-01", "subject": "ket_english", "name": "口语-个人问答", "name_en": "Speaking: Personal Questions",
     "description": "Answer personal questions about daily life, hobbies, family (Part 1)", "pillar": "speaking", "difficulty_level": 1},
    {"code": "KET-SPK-02", "subject": "ket_english", "name": "口语-情景对话", "name_en": "Speaking: Discussion & Interaction",
     "description": "Discuss preferences, make suggestions, agree/disagree (Part 2)", "pillar": "speaking", "difficulty_level": 2},
]

# ============================================================
# READING QUESTIONS (KETQuestion, skill="Reading")
# ============================================================

READING_QUESTIONS: list[dict] = [
    # --- Part 1: Notices & Signs ---
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You see this sign at a swimming pool:\n\n\"Children under 8 must be with an adult.\"\n\nWhat does the sign mean?",
        "options": {
            "choices": [
                {"label": "A", "content": "Children under 8 cannot swim here."},
                {"label": "B", "content": "Children under 8 must swim with an adult."},
                {"label": "C", "content": "Only adults can use the pool."},
            ]
        },
        "correct_answer": "B",
        "explanation": "'Must be with an adult' means children under 8 need an adult with them. It does NOT say they cannot swim. / must be with an adult 意思是8岁以下儿童必须有成人陪同。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You read this notice in a shop window:\n\n\"Closed for lunch. Open again at 2 p.m.\"\n\nWhen is the shop closed?",
        "options": {
            "choices": [
                {"label": "A", "content": "In the morning."},
                {"label": "B", "content": "In the afternoon before 2 p.m."},
                {"label": "C", "content": "In the evening."},
            ]
        },
        "correct_answer": "B",
        "explanation": "The shop is closed for lunch and opens again at 2 p.m., so it is closed in the early afternoon. / 商店午休，下午2点重新营业，所以下午2点前是关门的。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You see this message on a classroom door:\n\n\"Exam in progress. Please do not enter.\"\n\nWhat should you do?",
        "options": {
            "choices": [
                {"label": "A", "content": "Go in quietly."},
                {"label": "B", "content": "Knock and wait."},
                {"label": "C", "content": "Do not go into the room."},
            ]
        },
        "correct_answer": "C",
        "explanation": "'Please do not enter' means you should stay out of the room. / Please do not enter 意思是请不要进入。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You read this sign at a bus stop:\n\n\"Last bus to the city centre: 23:30\"\n\nWhat does this tell you?",
        "options": {
            "choices": [
                {"label": "A", "content": "There is only one bus every day."},
                {"label": "B", "content": "The final bus leaves at 11:30 p.m."},
                {"label": "C", "content": "Buses run every 23 minutes."},
            ]
        },
        "correct_answer": "B",
        "explanation": "'Last bus' means the final bus of the day. 23:30 is 11:30 p.m. / Last bus 表示末班车，23:30 就是晚上11:30。",
        "points": 1,
    },
    # --- Part 2: Matching / details ---
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "Five people want to do an evening class. Read their descriptions and choose the correct class.\n\n"
            "Anna wants to learn to make Italian food. She is free on Wednesday evenings.\n\n"
            "Which class is best for Anna?\n\n"
            "A. French Cooking — Monday 7 p.m.\n"
            "B. Italian Kitchen — Wednesday 7 p.m.\n"
            "C. Chinese Cooking — Thursday 6 p.m."
        ),
        "options": {
            "choices": [
                {"label": "A", "content": "French Cooking — Monday 7 p.m."},
                {"label": "B", "content": "Italian Kitchen — Wednesday 7 p.m."},
                {"label": "C", "content": "Chinese Cooking — Thursday 6 p.m."},
            ]
        },
        "correct_answer": "B",
        "explanation": "Anna wants Italian food AND is free on Wednesday. Option B matches both requirements. / Anna想学意大利菜，且周三晚上有空。选项B完全匹配。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "Marco is looking for a summer job. He can work weekends only and likes working with children.\n\n"
            "Which job is best for Marco?\n\n"
            "A. Shop assistant — weekdays 9-5\n"
            "B. Camp helper — Saturdays and Sundays, ages 6-12\n"
            "C. Restaurant waiter — Friday and Saturday evenings"
        ),
        "options": {
            "choices": [
                {"label": "A", "content": "Shop assistant — weekdays 9-5"},
                {"label": "B", "content": "Camp helper — Saturdays and Sundays, ages 6-12"},
                {"label": "C", "content": "Restaurant waiter — Friday and Saturday evenings"},
            ]
        },
        "correct_answer": "B",
        "explanation": "Marco wants weekends AND children. Option B is weekend work with children ages 6-12. / Marco想周末工作且喜欢和孩子在一起。选项B符合。",
        "points": 1,
    },
    # --- Part 3: Vocabulary in context ---
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Choose the correct word to complete the sentence:\n\n\"I usually ________ to school by bus.\"",
        "options": {
            "choices": [
                {"label": "A", "content": "go"},
                {"label": "B", "content": "goes"},
                {"label": "C", "content": "going"},
            ]
        },
        "correct_answer": "A",
        "explanation": "With 'I' (first person), we use the base form 'go'. 'Goes' is for he/she/it. / 第一人称I后面用动词原形go。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Choose the correct word:\n\n\"There aren't ________ apples in the fridge.\"",
        "options": {
            "choices": [
                {"label": "A", "content": "some"},
                {"label": "B", "content": "any"},
                {"label": "C", "content": "much"},
            ]
        },
        "correct_answer": "B",
        "explanation": "In negative sentences we use 'any', not 'some'. 'Much' is for uncountable nouns. / 否定句中用any而不是some。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Choose the correct word:\n\n\"She ________ her homework every evening at 7 o'clock.\"",
        "options": {
            "choices": [
                {"label": "A", "content": "do"},
                {"label": "B", "content": "does"},
                {"label": "C", "content": "doing"},
            ]
        },
        "correct_answer": "B",
        "explanation": "With 'she' (third person singular), present simple uses 'does'. / 第三人称单数she后面用does。",
        "points": 1,
    },
    # --- Part 4: Longer text ---
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "Read the text and answer the question:\n\n"
            "\"Hi Sam, I'm going to have a birthday party next Saturday at my house. "
            "It starts at 3 p.m. Could you bring some fruit? We're going to play games "
            "and have a barbecue in the garden. I hope you can come! — Emma\"\n\n"
            "When does the party start?"
        ),
        "options": {
            "choices": [
                {"label": "A", "content": "At 3 a.m."},
                {"label": "B", "content": "At 3 p.m. on Saturday."},
                {"label": "C", "content": "Next Sunday at 3 p.m."},
            ]
        },
        "correct_answer": "B",
        "explanation": "The text says 'next Saturday at 3 p.m.' / 文中明确写道 next Saturday at 3 p.m.。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "Read the text again:\n\n"
            "\"Hi Sam, I'm going to have a birthday party next Saturday at my house. "
            "It starts at 3 p.m. Could you bring some fruit? We're going to play games "
            "and have a barbecue in the garden. I hope you can come! — Emma\"\n\n"
            "What does Emma ask Sam to bring?"
        ),
        "options": {
            "choices": [
                {"label": "A", "content": "Games."},
                {"label": "B", "content": "Fruit."},
                {"label": "C", "content": "A barbecue."},
            ]
        },
        "correct_answer": "B",
        "explanation": "Emma writes 'Could you bring some fruit?' / Emma写道 Could you bring some fruit?",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "Read this advertisement:\n\n"
            "\"Greenfield Sports Centre\n"
            "Swimming pool, gym, tennis courts\n"
            "Open: Mon–Fri 6 a.m.–10 p.m., Sat–Sun 8 a.m.–8 p.m.\n"
            "First visit FREE! Under 16s must be with an adult.\"\n\n"
            "What is free?"
        ),
        "options": {
            "choices": [
                {"label": "A", "content": "Every visit."},
                {"label": "B", "content": "The first visit."},
                {"label": "C", "content": "Weekend visits."},
            ]
        },
        "correct_answer": "B",
        "explanation": "'First visit FREE!' means only your first time is free. / First visit FREE 表示只有第一次免费。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "Read this email:\n\n"
            "\"Dear Mr Brown, I'm sorry I can't come to class tomorrow because "
            "I have a dentist's appointment. I'll bring my homework on Thursday. "
            "Best wishes, Lily\"\n\n"
            "Why can't Lily go to class?"
        ),
        "options": {
            "choices": [
                {"label": "A", "content": "She is on holiday."},
                {"label": "B", "content": "She has a dentist's appointment."},
                {"label": "C", "content": "She doesn't like the class."},
            ]
        },
        "correct_answer": "B",
        "explanation": "Lily says 'I have a dentist's appointment'. / Lily说她有牙医预约。",
        "points": 1,
    },
    # --- Part 5: Gap fill (cloze) presented as MC ---
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Complete the sentence:\n\n\"My brother is ________ than me. He's 16 and I'm 14.\"",
        "options": {
            "choices": [
                {"label": "A", "content": "old"},
                {"label": "B", "content": "older"},
                {"label": "C", "content": "oldest"},
            ]
        },
        "correct_answer": "B",
        "explanation": "Comparing two people → use the comparative form 'older'. / 两人比较用比较级older。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Complete the sentence:\n\n\"We ________ to the cinema last night.\"",
        "options": {
            "choices": [
                {"label": "A", "content": "go"},
                {"label": "B", "content": "went"},
                {"label": "C", "content": "are going"},
            ]
        },
        "correct_answer": "B",
        "explanation": "'Last night' indicates past simple. The past of 'go' is 'went'. / last night表示过去时，go的过去式是went。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Complete the sentence:\n\n\"Look! It ________ outside. The ground is getting wet.\"",
        "options": {
            "choices": [
                {"label": "A", "content": "rains"},
                {"label": "B", "content": "is raining"},
                {"label": "C", "content": "rained"},
            ]
        },
        "correct_answer": "B",
        "explanation": "'Look!' tells us it is happening now → present continuous 'is raining'. / Look! 表示正在发生，用现在进行时。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Complete the sentence:\n\n\"________ you like some more tea?\"",
        "options": {
            "choices": [
                {"label": "A", "content": "Do"},
                {"label": "B", "content": "Would"},
                {"label": "C", "content": "Are"},
            ]
        },
        "correct_answer": "B",
        "explanation": "'Would you like...?' is the polite way to offer something. / Would you like...? 是礼貌地提供东西的表达。",
        "points": 1,
    },
    {
        "skill": "Reading", "level": "A2", "question_type": "multiple_choice",
        "prompt": "Complete the sentence:\n\n\"I ________ visit my grandmother next Sunday.\"",
        "options": {
            "choices": [
                {"label": "A", "content": "am going to"},
                {"label": "B", "content": "was going to"},
                {"label": "C", "content": "have gone to"},
            ]
        },
        "correct_answer": "A",
        "explanation": "'Next Sunday' is future → use 'am going to' for plans. / next Sunday是将来时间，用be going to表示计划。",
        "points": 1,
    },
]

# ============================================================
# LISTENING QUESTIONS (KETQuestion, skill="Listening")
# ============================================================

LISTENING_QUESTIONS: list[dict] = [
    # --- Part 1: Short extracts (identify information) ---
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You hear a woman talking to a friend. Where is she?\n\n\"I'd like a return ticket to Oxford, please.\"\n\nWhere is the woman?",
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "At a bus station."},
                {"label": "B", "content": "At a train station."},
                {"label": "C", "content": "At an airport."},
            ]
        },
        "correct_answer": "B",
        "explanation": "'A return ticket' is most commonly used at a train station. / return ticket（往返票）最常用于火车站。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You hear a man leaving a phone message. What does he want to do?\n\n\"Hi, it's Tom. I'd like to book a table for four this Saturday at 7 p.m.\"\n\nWhat does Tom want to do?",
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "Buy tickets for a show."},
                {"label": "B", "content": "Reserve a table at a restaurant."},
                {"label": "C", "content": "Book a hotel room."},
            ]
        },
        "correct_answer": "B",
        "explanation": "'Book a table' means reserve a place at a restaurant. / book a table 意思是在餐厅预订座位。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You hear a teacher talking to a class. What should the students do?\n\n\"Please open your books to page 42 and read the text.\"\n\nWhat should the students do?",
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "Open their books to page 42."},
                {"label": "B", "content": "Write in their books."},
                {"label": "C", "content": "Close their books."},
            ]
        },
        "correct_answer": "A",
        "explanation": "The teacher says 'open your books to page 42'. / 老师说 open your books to page 42。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": "You hear two friends talking. What time will they meet?\n\n\"Shall we meet at half past six? — No, let's make it seven, I have to finish work first.\"\n\nWhat time will they meet?",
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "6:00."},
                {"label": "B", "content": "6:30."},
                {"label": "C", "content": "7:00."},
            ]
        },
        "correct_answer": "C",
        "explanation": "They change the time from 6:30 to 7:00. / 他们把时间从6:30改到了7:00。",
        "points": 1,
    },
    # --- Part 2: Gap fill ---
    {
        "skill": "Listening", "level": "A2", "question_type": "fill_blank",
        "prompt": "Listen to a message about a school trip. Fill in the blank:\n\n\"The school trip to the ________ is on Friday.\"",
        "audio_url": "placeholder",
        "options": {"suggestions": ["museum", "park", "zoo", "beach"]},
        "correct_answer": "museum",
        "explanation": "The audio says 'school trip to the museum'. / 听力中说 school trip to the museum。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "fill_blank",
        "prompt": "Listen to an announcement. Fill in the blank:\n\n\"The train to London leaves from platform ________.\"",
        "audio_url": "placeholder",
        "options": {"suggestions": ["3", "5", "7", "9"]},
        "correct_answer": "5",
        "explanation": "The announcement says 'platform 5'. / 广播中说的是 platform 5。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "fill_blank",
        "prompt": "Listen to a girl talking about her holiday. Fill in the blank:\n\n\"We stayed in a small hotel near the ________.\"",
        "audio_url": "placeholder",
        "options": {"suggestions": ["beach", "mountains", "lake", "city"]},
        "correct_answer": "beach",
        "explanation": "She says they stayed near the beach. / 她说他们住在海滩附近。",
        "points": 1,
    },
    # --- Part 3: Multiple choice from longer dialogue ---
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a girl talking about her weekend. What did she do on Sunday?\n\n"
            "\"On Saturday I went shopping with my mum. On Sunday, I stayed home and "
            "watched a film. I wanted to go to the park but it rained all day.\""
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "She went to the park."},
                {"label": "B", "content": "She watched a film at home."},
                {"label": "C", "content": "She went shopping."},
            ]
        },
        "correct_answer": "B",
        "explanation": "On Sunday she stayed home and watched a film. Shopping was Saturday. / 周日她在家看了电影，购物是周六的事。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a boy talking about his new hobby. What hobby did he start?\n\n"
            "\"Last month I started playing the guitar. My dad bought me one for my birthday. "
            "I practice every evening for half an hour.\""
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "Playing the piano."},
                {"label": "B", "content": "Playing the guitar."},
                {"label": "C", "content": "Playing football."},
            ]
        },
        "correct_answer": "B",
        "explanation": "He says he 'started playing the guitar'. / 他说他 started playing the guitar。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a woman talking about a restaurant. What didn't she like?\n\n"
            "\"The food was delicious and the waiter was very friendly, but it took "
            "a long time to get our food — about 45 minutes!\""
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "The food."},
                {"label": "B", "content": "The waiter."},
                {"label": "C", "content": "The waiting time."},
            ]
        },
        "correct_answer": "C",
        "explanation": "She says 'it took a long time to get our food'. / 她说等餐时间太长。",
        "points": 1,
    },
    # --- Part 4-5: Monologue & matching ---
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a guide talking to tourists. Where are they?\n\n"
            "\"On your left you can see the cathedral, which was built in 1205. "
            "If you look to your right, that's the old market square.\"\n\n"
            "Where is the group?"
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "In a museum."},
                {"label": "B", "content": "On a city tour."},
                {"label": "C", "content": "In a school."},
            ]
        },
        "correct_answer": "B",
        "explanation": "A guide showing a cathedral and market square = a city tour. / 导游在介绍大教堂和集市广场，这是城市游览。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a radio announcement about the weather. What will the weather be like tomorrow?\n\n"
            "\"Tomorrow will be cloudy in the morning with some rain, but it will be sunny "
            "and warm in the afternoon.\""
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "Rainy all day."},
                {"label": "B", "content": "Sunny all day."},
                {"label": "C", "content": "Cloudy in the morning and sunny in the afternoon."},
            ]
        },
        "correct_answer": "C",
        "explanation": "Cloudy + rain in the morning, sunny in the afternoon. / 上午多云有雨，下午晴朗。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a conversation at a clothes shop. How much does the jacket cost?\n\n"
            "\"How much is this jacket? — It was £60 but it's on sale now for £45.\""
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "£45."},
                {"label": "B", "content": "£60."},
                {"label": "C", "content": "£15."},
            ]
        },
        "correct_answer": "A",
        "explanation": "It's on sale for £45 now. The original price was £60. / 打折后价格是45英镑。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "fill_blank",
        "prompt": "Listen to a voicemail message. Fill in the blank:\n\n\"Please call me back at ________ before 5 o'clock.\"",
        "audio_url": "placeholder",
        "options": {"suggestions": ["07700 900123", "07700 900456", "07700 900789", "07700 900321"]},
        "correct_answer": "07700 900456",
        "explanation": "The caller leaves the number 07700 900456. / 来电者留下的号码是 07700 900456。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a teacher telling students about homework. When is the homework due?\n\n"
            "\"Your homework is due on Wednesday, not Friday. Please remember to bring it to class.\""
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "Monday."},
                {"label": "B", "content": "Wednesday."},
                {"label": "C", "content": "Friday."},
            ]
        },
        "correct_answer": "B",
        "explanation": "The teacher changed the deadline to Wednesday. / 老师把截止日期改到了周三。",
        "points": 1,
    },
    {
        "skill": "Listening", "level": "A2", "question_type": "multiple_choice",
        "prompt": (
            "You hear a girl calling her friend. Why is she calling?\n\n"
            "\"Hi Sarah, it's Lisa. I can't find my history book. Did I leave it at your house yesterday?\""
        ),
        "audio_url": "placeholder",
        "options": {
            "choices": [
                {"label": "A", "content": "To invite Sarah to go out."},
                {"label": "B", "content": "To ask about a missing book."},
                {"label": "C", "content": "To return a book to Sarah."},
            ]
        },
        "correct_answer": "B",
        "explanation": "Lisa can't find her history book and thinks it may be at Sarah's house. / Lisa找不到她的历史书，觉得可能忘在Sarah家了。",
        "points": 1,
    },
]

# ============================================================
# WRITING TASKS (KETWritingTask)
# ============================================================

WRITING_TASKS: list[dict] = [
    # --- Part 6: Short messages (25-35 words, 3 content points) ---
    {
        "task_type": "short_message",
        "prompt": (
            "You want to go swimming with your English friend, Sam. Write an email to Sam (25-35 words).\n\n"
            "In your email, you should:\n"
            "• suggest going swimming\n"
            "• say when you want to go\n"
            "• ask Sam to bring something\n\n"
            "Write your email."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Hi Sam,\n\n"
            "Do you want to go swimming with me this Saturday afternoon? "
            "We can meet at the sports centre at 2 p.m. Can you bring your goggles?\n\n"
            "See you!"
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "You are going to have a party. Write an email to your English friend, Alex (25-35 words).\n\n"
            "In your email, you should:\n"
            "• invite Alex to the party\n"
            "• say when and where the party is\n"
            "• tell Alex what to bring\n\n"
            "Write your email."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Hi Alex,\n\n"
            "I'm having a party at my house this Saturday at 6 p.m.! "
            "Could you bring some drinks? It would be great to see you.\n\n"
            "Best wishes!"
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "You forgot to return a book to your English teacher. Write a note to your teacher (25-35 words).\n\n"
            "In your note, you should:\n"
            "• apologise for forgetting the book\n"
            "• say when you will bring it\n"
            "• explain why you forgot\n\n"
            "Write your note."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Dear Mr Smith,\n\n"
            "I'm sorry I forgot to bring my library book today. "
            "I will bring it tomorrow. I left it at home because I was rushing this morning.\n\n"
            "Best wishes, Kim"
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "You want to go to the cinema with your English friend, Jo. Write a text message to Jo (25-35 words).\n\n"
            "In your message, you should:\n"
            "• suggest which film to see\n"
            "• say what time to meet\n"
            "• tell Jo how to get there\n\n"
            "Write your message."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Hi Jo! Shall we see the new superhero film at the Odeon? "
            "We could meet at 5 p.m. outside the cinema. Take bus number 12 from your house."
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "You are ill and can't go to your English class today. Write an email to your teacher, Mrs Green (25-35 words).\n\n"
            "In your email, you should:\n"
            "• say you can't come to class\n"
            "• explain why\n"
            "• ask about the homework\n\n"
            "Write your email."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Dear Mrs Green,\n\n"
            "I'm sorry but I can't come to class today. I have a bad cold and a temperature. "
            "Could you tell me what the homework is, please?\n\n"
            "Thank you, Anna"
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "Your English friend, Ben, has a new baby sister. Write a message to Ben (25-35 words).\n\n"
            "In your message, you should:\n"
            "• congratulate Ben\n"
            "• ask about the baby\n"
            "• suggest visiting soon\n\n"
            "Write your message."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Hi Ben! Congratulations on your new baby sister! What's her name? "
            "Is she sleeping well? I'd love to come and visit you both this weekend if that's OK!"
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "You want to join a sports club. Write an email to the club manager (25-35 words).\n\n"
            "In your email, you should:\n"
            "• say which sport you want to do\n"
            "• ask about the price\n"
            "• ask about opening times\n\n"
            "Write your email."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Dear Sir/Madam,\n\n"
            "I'd like to join your tennis club. Could you please tell me how much it costs per month? "
            "Also, what are your opening hours on weekends?\n\n"
            "Thank you, Peter"
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "You lost your wallet in a shop. Write a notice for the shop (25-35 words).\n\n"
            "In your notice, you should:\n"
            "• describe the wallet\n"
            "• say when you lost it\n"
            "• give your contact details\n\n"
            "Write your notice."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "LOST WALLET — I lost a black leather wallet in this shop on Tuesday afternoon. "
            "It has my student card inside. If found, please call 07700 900123. Thank you!"
        ),
    },
    # --- Part 7: Story / Letter (35-45 words) ---
    {
        "task_type": "story",
        "prompt": (
            "Your English teacher has asked you to write a story. Your story must begin with this sentence:\n\n"
            "\"It was a beautiful sunny morning when Sarah woke up.\"\n\n"
            "Write your story (35-45 words)."
        ),
        "word_limit_min": 35,
        "word_limit_max": 45,
        "sample_response": (
            "It was a beautiful sunny morning when Sarah woke up. She looked out of the window "
            "and saw a small puppy in the garden. She ran outside and played with it all day. "
            "She decided to call it Lucky."
        ),
    },
    {
        "task_type": "story",
        "prompt": (
            "Write a story about a day you will never forget.\n\n"
            "Your story must include:\n"
            "• where you went\n"
            "• what happened\n"
            "• how you felt\n\n"
            "Write your story (35-45 words)."
        ),
        "word_limit_min": 35,
        "word_limit_max": 45,
        "sample_response": (
            "Last summer, I went to the beach with my family. Suddenly, I saw a dolphin "
            "jumping out of the water! It was amazing. I felt so happy that I will never "
            "forget that magical day."
        ),
    },
    {
        "task_type": "informal_letter",
        "prompt": (
            "This is part of a letter you receive from your English friend, Paul:\n\n"
            "\"In my town there's a new sports centre. What sports do you like? "
            "Where do you usually do them?\"\n\n"
            "Write a letter to Paul, answering his questions (35-45 words)."
        ),
        "word_limit_min": 35,
        "word_limit_max": 45,
        "sample_response": (
            "Dear Paul,\n\n"
            "That sounds great! I really enjoy playing basketball and swimming. "
            "I usually play basketball at school with my friends, and I go swimming "
            "at the local pool on Saturdays. What about you?\n\n"
            "Write back soon!"
        ),
    },
    {
        "task_type": "informal_letter",
        "prompt": (
            "This is part of an email from your English friend, Lucy:\n\n"
            "\"Next month I'm coming to visit your town. What's the best time to come? "
            "What places should I visit? What clothes should I bring?\"\n\n"
            "Write an email to Lucy, answering her questions (35-45 words)."
        ),
        "word_limit_min": 35,
        "word_limit_max": 45,
        "sample_response": (
            "Hi Lucy!\n\n"
            "Come in July — the weather is lovely then. You should visit the old castle "
            "and the market square. Bring comfortable shoes and a light jacket for the evenings. "
            "I can't wait to see you!\n\n"
            "Lots of love"
        ),
    },
    {
        "task_type": "story",
        "prompt": (
            "Your teacher has asked you to write a story. Your story must begin with:\n\n"
            "\"Tom looked at the map and knew they were lost.\"\n\n"
            "Write your story (35-45 words)."
        ),
        "word_limit_min": 35,
        "word_limit_max": 45,
        "sample_response": (
            "Tom looked at the map and knew they were lost. His sister started to cry, "
            "but Tom said 'Don't worry!' He saw a sign for the railway station and they "
            "walked there. Soon they were safely on the train home."
        ),
    },
    {
        "task_type": "short_message",
        "prompt": (
            "You want to borrow a book from your English friend, Mark. Write a message to Mark (25-35 words).\n\n"
            "In your message, you should:\n"
            "• say which book you want to borrow\n"
            "• explain why you need it\n"
            "• promise when to return it\n\n"
            "Write your message."
        ),
        "word_limit_min": 25,
        "word_limit_max": 35,
        "sample_response": (
            "Hi Mark! Can I borrow your English dictionary, please? I need it for my homework "
            "this week. I promise to give it back on Monday. Thank you so much!"
        ),
    },
    {
        "task_type": "story",
        "prompt": (
            "Your teacher has asked you to write a story about a surprise. Your story must begin with:\n\n"
            "\"When Maria opened the door, she couldn't believe her eyes.\"\n\n"
            "Write your story (35-45 words)."
        ),
        "word_limit_min": 35,
        "word_limit_max": 45,
        "sample_response": (
            "When Maria opened the door, she couldn't believe her eyes. All her friends were "
            "there with balloons and a big cake. It was her birthday and she had no idea! "
            "They sang and danced all evening."
        ),
    },
]

# ============================================================
# SPEAKING TASKS (KETSpeakingTask)
# ============================================================

SPEAKING_TASKS: list[dict] = [
    # --- Part 1: Personal questions ---
    {
        "topic": "Daily routine / 日常生活",
        "question": "What time do you usually get up in the morning? What do you have for breakfast?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "School / 学校生活",
        "question": "Tell me about your school. What is your favourite subject and why?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Family / 家庭",
        "question": "How many people are in your family? What does your family usually do at the weekend?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Free time / 空闲时间",
        "question": "What do you like doing in your free time? Do you prefer staying at home or going out?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Sport / 运动",
        "question": "Do you like sport? What sports do you play? How often do you play?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Food / 食物",
        "question": "What kind of food do you like? Can you cook? What is your favourite meal?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Travel / 旅行",
        "question": "Where did you go on your last holiday? What did you do there?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Music / 音乐",
        "question": "Do you like listening to music? What kind of music do you enjoy? Who is your favourite singer?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Friends / 朋友",
        "question": "Tell me about your best friend. What do you like doing together?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    {
        "topic": "Weather / 天气",
        "question": "What is the weather like today? What kind of weather do you like best?",
        "difficulty": "easy",
        "expected_duration_sec": 30,
    },
    # --- Part 2: Discussion / interaction (medium difficulty) ---
    {
        "topic": "Planning a trip / 计划旅行",
        "question": (
            "I'm going to visit your city for the weekend. Where should I go? "
            "What should I see? Where can I eat? Suggest some places and explain why."
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Choosing a gift / 选择礼物",
        "question": (
            "It's your friend's birthday next week. Let's talk about what to buy. "
            "What does your friend like? What gift would you choose and why?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Weekend plans / 周末计划",
        "question": (
            "Let's talk about what we could do this weekend. We could go to the cinema, "
            "the park, or a museum. What do you think? Give your opinion and reasons."
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Learning English / 学英语",
        "question": (
            "Why are you learning English? What is easy or difficult for you? "
            "What do you do to practise English outside class?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Shopping preferences / 购物偏好",
        "question": (
            "Do you prefer shopping in big shopping centres or small local shops? Why? "
            "Tell me about something you bought recently. Were you happy with it?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Healthy living / 健康生活",
        "question": (
            "How can people stay healthy? Talk about food, exercise, and sleep. "
            "What do you do to stay healthy? Is there anything you would like to change?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Future plans / 未来计划",
        "question": (
            "What are you going to do next summer? What job would you like to have in the future? Why?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Technology / 科技",
        "question": (
            "How often do you use a computer or phone? What do you use them for? "
            "Do you think people spend too much time on their phones?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Pets / 宠物",
        "question": (
            "Do you have a pet? If yes, tell me about it. If not, would you like one? "
            "What pet would you choose and why?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
    {
        "topic": "Reading / 阅读",
        "question": (
            "Do you enjoy reading? What kind of books or stories do you like? "
            "Tell me about a book you read recently. Would you recommend it?"
        ),
        "difficulty": "medium",
        "expected_duration_sec": 60,
    },
]


# ============================================================
# SEED LOGIC
# ============================================================

async def seed_knowledge_points(session, dry_run: bool) -> dict[str, UUID]:
    """Create KET knowledge points. Returns {code: UUID}."""
    kp_map: dict[str, UUID] = {}
    for kp_data in KET_KNOWLEDGE_POINTS:
        code = kp_data["code"]
        stmt = select(KnowledgePoint).where(KnowledgePoint.code == code)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            kp_map[code] = existing.id
            logger.info("  KP exists: %s", code)
            continue

        kp = KnowledgePoint(
            id=uuid4(),
            code=code,
            subject=kp_data["subject"],
            name=kp_data["name"],
            name_en=kp_data["name_en"],
            description=kp_data["description"],
            pillar=kp_data["pillar"],
            difficulty_level=kp_data["difficulty_level"],
            amc_level=0,
        )
        if not dry_run:
            session.add(kp)
            await session.flush()
        kp_map[code] = kp.id
        logger.info("  KP created: %s", code)
    return kp_map


async def seed_ket_questions(session, dry_run: bool) -> None:
    """Insert KET reading and listening questions."""
    all_questions = READING_QUESTIONS + LISTENING_QUESTIONS
    count = 0
    for q_data in all_questions:
        # Check for duplicate by prompt + skill
        stmt = select(KETQuestion).where(
            KETQuestion.prompt == q_data["prompt"],
            KETQuestion.skill == q_data["skill"],
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            continue
        q = KETQuestion(
            id=uuid4(),
            skill=q_data["skill"],
            level=q_data["level"],
            question_type=q_data["question_type"],
            prompt=q_data["prompt"],
            audio_url=q_data.get("audio_url"),
            image_url=q_data.get("image_url"),
            options=q_data.get("options"),
            correct_answer=q_data["correct_answer"],
            explanation=q_data.get("explanation"),
            points=q_data.get("points", 1),
        )
        if not dry_run:
            session.add(q)
        count += 1
    logger.info("  KETQuestions seeded: %d new", count)


async def seed_writing_tasks(session, dry_run: bool) -> None:
    """Insert KET writing tasks."""
    count = 0
    for t_data in WRITING_TASKS:
        stmt = select(KETWritingTask).where(KETWritingTask.prompt == t_data["prompt"])
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            continue
        t = KETWritingTask(
            id=uuid4(),
            task_type=t_data["task_type"],
            prompt=t_data["prompt"],
            image_url=t_data.get("image_url"),
            word_limit_min=t_data["word_limit_min"],
            word_limit_max=t_data["word_limit_max"],
            sample_response=t_data.get("sample_response"),
        )
        if not dry_run:
            session.add(t)
        count += 1
    logger.info("  KETWritingTasks seeded: %d new", count)


async def seed_speaking_tasks(session, dry_run: bool) -> None:
    """Insert KET speaking tasks."""
    count = 0
    for t_data in SPEAKING_TASKS:
        stmt = select(KETSpeakingTask).where(KETSpeakingTask.question == t_data["question"])
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            continue
        t = KETSpeakingTask(
            id=uuid4(),
            topic=t_data["topic"],
            question=t_data["question"],
            difficulty=t_data["difficulty"],
            expected_duration_sec=t_data["expected_duration_sec"],
        )
        if not dry_run:
            session.add(t)
        count += 1
    logger.info("  KETSpeakingTasks seeded: %d new", count)


# ============================================================
# MAIN
# ============================================================

async def main() -> None:
    parser = argparse.ArgumentParser(description="Seed KET question bank")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("=" * 60)
    logger.info("KET Question Bank Seeding — dry_run=%s", args.dry_run)
    logger.info("=" * 60)

    async with async_session_factory() as session:
        # 1. Knowledge Points
        logger.info("[1/4] Seeding knowledge points...")
        kp_map = await seed_knowledge_points(session, args.dry_run)
        logger.info("  → %d knowledge points resolved", len(kp_map))

        # 2. Questions (Reading + Listening)
        logger.info("[2/4] Seeding KET questions (Reading + Listening)...")
        await seed_ket_questions(session, args.dry_run)

        # 3. Writing tasks
        logger.info("[3/4] Seeding KET writing tasks...")
        await seed_writing_tasks(session, args.dry_run)

        # 4. Speaking tasks
        logger.info("[4/4] Seeding KET speaking tasks...")
        await seed_speaking_tasks(session, args.dry_run)

        if not args.dry_run:
            await session.commit()
            logger.info("All changes committed.")
        else:
            logger.info("DRY RUN — no changes written to DB.")

    logger.info("Done.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
