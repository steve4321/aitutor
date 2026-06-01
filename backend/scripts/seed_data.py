"""Seed the database with sample data for development.

Usage: cd backend && python -m scripts.seed_data
"""
import asyncio
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Add parent dir to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.security import hash_password
from app.models import (
    Base,
    Course,
    KnowledgePoint,
    LearningSession,
    Lesson,
    Problem,
    StudentProfile,
    Unit,
    User,
)


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        # Check if data already exists
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already has data. Skipping seed.")
            await engine.dispose()
            return

        # ============================================================
        # 1. USERS
        # ============================================================
        student = User(
            name="teststudent",
            email="student@test.com",
            password_hash=hash_password("test123"),
            role="student",
        )
        db.add(student)
        await db.flush()

        profile = StudentProfile(
            user_id=student.id,
            grade_level=5,
            target_exam="AMC8",
            target_date=date(2026, 11, 15),
            daily_goal_minutes=20,
            diagnostic_done=True,
            xp_total=150,
            streak_days=3,
            longest_streak=7,
        )
        db.add(profile)

        parent = User(
            name="testparent",
            email="parent@test.com",
            password_hash=hash_password("test123"),
            role="parent",
        )
        db.add(parent)
        await db.flush()

        # ============================================================
        # 2. COURSES (index: 0=AMC8-A, 1=AMC8-B, 2=KET-A, 3=CN-B5, 4=CN-C4)
        # ============================================================
        courses_data = [
            {
                "code": "AMC8-A",
                "subject": "math",
                "name": "AMC 8 基础班",
                "description": "AMC 8 竞赛基础训练，涵盖算术、代数、几何与计数四大模块",
                "target_exam": "AMC8",
                "estimated_hours": 40,
                "is_published": True,
            },
            {
                "code": "AMC8-B",
                "subject": "math",
                "name": "AMC 8 提高班",
                "description": "AMC 8 竞赛提高训练，深入数论、代数技巧、几何证明与组合策略",
                "target_exam": "AMC8",
                "estimated_hours": 60,
                "is_published": True,
            },
            {
                "code": "KET-A",
                "subject": "english",
                "name": "KET 基础班",
                "description": "剑桥 KET (A2 Key) 考试备考课程，涵盖听说读写四项技能",
                "target_exam": "KET",
                "estimated_hours": 30,
                "is_published": True,
            },
            {
                "code": "CN-B5",
                "subject": "chinese",
                "name": "语文·作文五年级",
                "description": "小学五年级作文训练，从记叙文到描写文到应用文，全面提升写作能力",
                "target_exam": None,
                "estimated_hours": 20,
                "is_published": True,
            },
            {
                "code": "CN-C4",
                "subject": "chinese",
                "name": "语文·古诗词四年级",
                "description": "小学四年级古诗词赏析与背诵，精选唐诗宋词，培养文学素养",
                "target_exam": None,
                "estimated_hours": 15,
                "is_published": True,
            },
        ]

        courses = []
        for c in courses_data:
            course = Course(**c)
            db.add(course)
            courses.append(course)
        await db.flush()

        # ============================================================
        # 3. KNOWLEDGE POINTS (all subjects)
        # ============================================================
        kp_data = [
            # --- AMC8-A math basics kps[0..3] ---
            {"code": "math-arith-01", "subject": "math", "name": "整除与余数", "name_en": "Divisibility and Remainders", "pillar": "数论", "difficulty_level": 2, "amc_level": 8},
            {"code": "math-alg-01", "subject": "math", "name": "一元一次方程", "name_en": "Linear Equations", "pillar": "代数", "difficulty_level": 2, "amc_level": 8},
            {"code": "math-geo-01", "subject": "math", "name": "三角形面积", "name_en": "Triangle Area", "pillar": "几何", "difficulty_level": 2, "amc_level": 8},
            {"code": "math-count-01", "subject": "math", "name": "排列组合基础", "name_en": "Permutations and Combinations", "pillar": "组合", "difficulty_level": 3, "amc_level": 8},
            # --- AMC8-B math advanced kps[4..11] ---
            {"code": "math-num-02", "subject": "math", "name": "质因数分解", "name_en": "Prime Factorization", "pillar": "数论", "difficulty_level": 3, "amc_level": 8},
            {"code": "math-num-03", "subject": "math", "name": "同余与模运算", "name_en": "Modular Arithmetic", "pillar": "数论", "difficulty_level": 3, "amc_level": 8},
            {"code": "math-alg-02", "subject": "math", "name": "方程组与不等式", "name_en": "Systems of Equations", "pillar": "代数", "difficulty_level": 3, "amc_level": 8},
            {"code": "math-alg-03", "subject": "math", "name": "数列与规律", "name_en": "Sequences and Patterns", "pillar": "代数", "difficulty_level": 3, "amc_level": 8},
            {"code": "math-geo-02", "subject": "math", "name": "圆与扇形", "name_en": "Circles and Sectors", "pillar": "几何", "difficulty_level": 3, "amc_level": 8},
            {"code": "math-geo-03", "subject": "math", "name": "立体几何", "name_en": "3D Geometry", "pillar": "几何", "difficulty_level": 3, "amc_level": 8},
            {"code": "math-comb-02", "subject": "math", "name": "进阶计数", "name_en": "Advanced Counting", "pillar": "组合", "difficulty_level": 4, "amc_level": 8},
            {"code": "math-comb-03", "subject": "math", "name": "概率与期望", "name_en": "Probability and Expected Value", "pillar": "组合", "difficulty_level": 4, "amc_level": 8},
            # --- KET english kps[12..19] ---
            {"code": "eng-voc-01", "subject": "english", "name": "KET核心词汇", "name_en": "KET Core Vocabulary", "pillar": "词汇", "difficulty_level": 1, "amc_level": 0},
            {"code": "eng-voc-02", "subject": "english", "name": "日常场景用语", "name_en": "Everyday Expressions", "pillar": "词汇", "difficulty_level": 1, "amc_level": 0},
            {"code": "eng-gram-01", "subject": "english", "name": "时态基础", "name_en": "Basic Tenses", "pillar": "语法", "difficulty_level": 2, "amc_level": 0},
            {"code": "eng-gram-02", "subject": "english", "name": "句型结构", "name_en": "Sentence Structures", "pillar": "语法", "difficulty_level": 2, "amc_level": 0},
            {"code": "eng-listen-01", "subject": "english", "name": "听力理解", "name_en": "Listening Comprehension", "pillar": "听力", "difficulty_level": 2, "amc_level": 0},
            {"code": "eng-read-01", "subject": "english", "name": "阅读理解", "name_en": "Reading Comprehension", "pillar": "阅读", "difficulty_level": 2, "amc_level": 0},
            {"code": "eng-write-01", "subject": "english", "name": "短文写作", "name_en": "Short Writing", "pillar": "写作", "difficulty_level": 2, "amc_level": 0},
            {"code": "eng-speak-01", "subject": "english", "name": "口语交际", "name_en": "Oral Communication", "pillar": "口语", "difficulty_level": 2, "amc_level": 0},
            # --- CN-B5 essay kps[20..24] ---
            {"code": "chn-essay-01", "subject": "chinese", "name": "记叙文六要素", "name_en": "Narrative Elements", "pillar": "写作", "difficulty_level": 2, "amc_level": 0},
            {"code": "chn-essay-02", "subject": "chinese", "name": "人物描写方法", "name_en": "Character Description", "pillar": "写作", "difficulty_level": 2, "amc_level": 0},
            {"code": "chn-essay-03", "subject": "chinese", "name": "景物描写技巧", "name_en": "Scene Description", "pillar": "写作", "difficulty_level": 3, "amc_level": 0},
            {"code": "chn-essay-04", "subject": "chinese", "name": "书信与日记格式", "name_en": "Letter and Diary Format", "pillar": "写作", "difficulty_level": 2, "amc_level": 0},
            {"code": "chn-essay-05", "subject": "chinese", "name": "作文结构布局", "name_en": "Essay Structure", "pillar": "写作", "difficulty_level": 3, "amc_level": 0},
            # --- CN-C4 poetry kps[25..29] ---
            {"code": "chn-poem-01", "subject": "chinese", "name": "唐诗经典赏析", "name_en": "Tang Poetry Appreciation", "pillar": "古诗", "difficulty_level": 2, "amc_level": 0},
            {"code": "chn-poem-02", "subject": "chinese", "name": "宋词基本特点", "name_en": "Song Ci Features", "pillar": "古诗", "difficulty_level": 2, "amc_level": 0},
            {"code": "chn-poem-03", "subject": "chinese", "name": "诗歌意象理解", "name_en": "Poetic Imagery", "pillar": "古诗", "difficulty_level": 3, "amc_level": 0},
            {"code": "chn-poem-04", "subject": "chinese", "name": "韵律与对仗", "name_en": "Rhythm and Antithesis", "pillar": "古诗", "difficulty_level": 3, "amc_level": 0},
            {"code": "chn-poem-05", "subject": "chinese", "name": "古诗文背诵默写", "name_en": "Recitation and Dictation", "pillar": "古诗", "difficulty_level": 2, "amc_level": 0},
        ]

        kps = []
        for kp in kp_data:
            point = KnowledgePoint(**kp)
            db.add(point)
            kps.append(point)
        await db.flush()

        # ============================================================
        # 4. UNITS (all courses)
        # ============================================================
        units_data = [
            # AMC8-A units[0..3]
            {"course_id": courses[0].id, "code": "AMC8-A-U1", "name": "算术与数论", "description": "整除性、余数、因数与倍数", "sort_order": 1, "required_mastery": 0.8},
            {"course_id": courses[0].id, "code": "AMC8-A-U2", "name": "代数基础", "description": "一元一次方程、代数式化简", "sort_order": 2, "required_mastery": 0.8},
            {"course_id": courses[0].id, "code": "AMC8-A-U3", "name": "几何入门", "description": "三角形、四边形面积计算", "sort_order": 3, "required_mastery": 0.8},
            {"course_id": courses[0].id, "code": "AMC8-A-U4", "name": "计数与概率", "description": "排列组合基础、简单概率", "sort_order": 4, "required_mastery": 0.8},
            # AMC8-B units[4..7]
            {"course_id": courses[1].id, "code": "AMC8-B-U1", "name": "数论进阶", "description": "质因数分解、最大公约数、最小公倍数、同余", "sort_order": 1, "required_mastery": 0.85},
            {"course_id": courses[1].id, "code": "AMC8-B-U2", "name": "代数进阶", "description": "方程组、不等式、数列与规律发现", "sort_order": 2, "required_mastery": 0.85},
            {"course_id": courses[1].id, "code": "AMC8-B-U3", "name": "几何进阶", "description": "圆与扇形、勾股定理、立体几何", "sort_order": 3, "required_mastery": 0.85},
            {"course_id": courses[1].id, "code": "AMC8-B-U4", "name": "组合与概率进阶", "description": "容斥原理、进阶计数、几何概率与期望值", "sort_order": 4, "required_mastery": 0.85},
            # KET-A units[8..11]
            {"course_id": courses[2].id, "code": "KET-A-U1", "name": "日常词汇与表达", "description": "KET 核心词汇、日常场景对话用语", "sort_order": 1, "required_mastery": 0.8},
            {"course_id": courses[2].id, "code": "KET-A-U2", "name": "基础语法", "description": "一般现在时、一般过去时、将来时、基本句型结构", "sort_order": 2, "required_mastery": 0.8},
            {"course_id": courses[2].id, "code": "KET-A-U3", "name": "听力与口语", "description": "KET 听力题型训练、日常口语交际", "sort_order": 3, "required_mastery": 0.8},
            {"course_id": courses[2].id, "code": "KET-A-U4", "name": "阅读与写作", "description": "短文阅读理解、KET 写作题型训练", "sort_order": 4, "required_mastery": 0.8},
            # CN-B5 units[12..14]
            {"course_id": courses[3].id, "code": "CN-B5-U1", "name": "记叙文写作", "description": "记叙文六要素、叙事顺序、详略安排", "sort_order": 1, "required_mastery": 0.8},
            {"course_id": courses[3].id, "code": "CN-B5-U2", "name": "描写技巧", "description": "人物描写、景物描写、心理描写", "sort_order": 2, "required_mastery": 0.8},
            {"course_id": courses[3].id, "code": "CN-B5-U3", "name": "应用文写作", "description": "书信、日记、读后感的格式与写法", "sort_order": 3, "required_mastery": 0.8},
            # CN-C4 units[15..17]
            {"course_id": courses[4].id, "code": "CN-C4-U1", "name": "唐诗精选", "description": "经典唐诗朗读、理解与赏析", "sort_order": 1, "required_mastery": 0.8},
            {"course_id": courses[4].id, "code": "CN-C4-U2", "name": "宋词入门", "description": "宋词基本特点与经典篇目", "sort_order": 2, "required_mastery": 0.8},
            {"course_id": courses[4].id, "code": "CN-C4-U3", "name": "诗韵与意境", "description": "诗歌意象、韵律对仗、背诵默写", "sort_order": 3, "required_mastery": 0.8},
        ]

        units = []
        for u in units_data:
            unit = Unit(**u)
            db.add(unit)
            units.append(unit)
        await db.flush()

        # ============================================================
        # 5. LESSONS (all units)
        # ============================================================
        # unit indices: 0..3=AMC8-A, 4..7=AMC8-B, 8..11=KET, 12..14=CN-B5, 15..17=CN-C4
        # kp indices:   0..3=AMC8-A, 4..11=AMC8-B, 12..19=KET, 20..24=CN-B5, 25..29=CN-C4
        lessons_data = [
            # --- AMC8-A ---
            {"unit_id": units[0].id, "knowledge_point_id": kps[0].id, "code": "AMC8-A-L01", "title": "整除性判定", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "学习 2、3、4、5、6、8、9、10、11 的整除判定法则"}, {"type": "text", "content": "例题：判断 12345 能否被 3 整除？能否被 9 整除？"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 1, "is_published": True},
            {"unit_id": units[0].id, "knowledge_point_id": kps[0].id, "code": "AMC8-A-L02", "title": "余数问题", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "学习余数的性质与运算技巧"}, {"type": "text", "content": "例题：一个数除以 7 余 3，除以 5 余 2，求满足条件的最小正整数"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},
            {"unit_id": units[1].id, "knowledge_point_id": kps[1].id, "code": "AMC8-A-L03", "title": "方程求解", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "一元一次方程的解法：移项、合并同类项"}, {"type": "text", "content": "例题：解方程 3(x-2) + 5 = 2x + 7"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 1, "is_published": True},
            {"unit_id": units[1].id, "knowledge_point_id": kps[1].id, "code": "AMC8-A-L04", "title": "应用题列方程", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "将实际问题转化为方程求解"}, {"type": "text", "content": "例题：小明有 15 元，买了 3 支笔后还剩 3 元，每支笔多少钱？"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},
            {"unit_id": units[2].id, "knowledge_point_id": kps[2].id, "code": "AMC8-A-L05", "title": "三角形面积计算", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "三角形面积公式及应用，底与高的对应关系"}, {"type": "text", "content": "例题：三角形底边长 10，高为 6，求面积"}], "steps": []},
             "estimated_minutes": 15, "sort_order": 1, "is_published": True},
            {"unit_id": units[2].id, "knowledge_point_id": kps[2].id, "code": "AMC8-A-L06", "title": "四边形面积", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "长方形、正方形、平行四边形、梯形面积公式"}, {"type": "text", "content": "例题：梯形上底 4、下底 8、高 5，求面积"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 2, "is_published": True},
            {"unit_id": units[3].id, "knowledge_point_id": kps[3].id, "code": "AMC8-A-L07", "title": "排列与组合", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "排列组合的基本概念与公式"}, {"type": "text", "content": "例题：从 5 个同学中选 3 个站成一排，有多少种站法？"}], "steps": []},
             "estimated_minutes": 30, "sort_order": 1, "is_published": True},
            {"unit_id": units[3].id, "knowledge_point_id": kps[3].id, "code": "AMC8-A-L08", "title": "简单概率", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "等可能事件概率计算，树状图和列表法"}, {"type": "text", "content": "例题：同时掷两个骰子，点数之和为 7 的概率是多少？"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},

            # --- AMC8-B ---
            {"unit_id": units[4].id, "knowledge_point_id": kps[4].id, "code": "AMC8-B-L01", "title": "质因数分解与约数个数", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "算术基本定理：每个正整数可以唯一分解为质数的乘积"}, {"type": "text", "content": "约数个数公式：若 n = p₁^a₁ × p₂^a₂ × ...，则约数个数 = (a₁+1)(a₂+1)..."}, {"type": "text", "content": "例题：求 360 有多少个正约数？"}], "steps": []},
             "estimated_minutes": 30, "sort_order": 1, "is_published": True},
            {"unit_id": units[4].id, "knowledge_point_id": kps[5].id, "code": "AMC8-B-L02", "title": "同余与模运算", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "同余的定义与性质：加减乘在同余下保持"}, {"type": "text", "content": "例题：求 2^100 除以 7 的余数"}], "steps": []},
             "estimated_minutes": 35, "sort_order": 2, "is_published": True},
            {"unit_id": units[5].id, "knowledge_point_id": kps[6].id, "code": "AMC8-B-L03", "title": "方程组求解", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "二元一次方程组的代入消元法与加减消元法"}, {"type": "text", "content": "例题：解方程组 2x + 3y = 13, 4x - y = 5"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 1, "is_published": True},
            {"unit_id": units[5].id, "knowledge_point_id": kps[7].id, "code": "AMC8-B-L04", "title": "数列与规律发现", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "等差数列与等比数列的通项公式与求和"}, {"type": "text", "content": "例题：1 + 2 + 3 + ... + 100 = ?"}], "steps": []},
             "estimated_minutes": 30, "sort_order": 2, "is_published": True},
            {"unit_id": units[6].id, "knowledge_point_id": kps[8].id, "code": "AMC8-B-L05", "title": "圆与扇形面积", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "圆的面积与周长、扇形面积、弧长公式"}, {"type": "text", "content": "例题：半径为 6 的圆中，60° 扇形的面积是多少？"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 1, "is_published": True},
            {"unit_id": units[6].id, "knowledge_point_id": kps[9].id, "code": "AMC8-B-L06", "title": "立体几何基础", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "长方体、正方体、圆柱、圆锥的表面积与体积"}, {"type": "text", "content": "例题：长方体长 3、宽 4、高 5，求表面积和体积"}], "steps": []},
             "estimated_minutes": 30, "sort_order": 2, "is_published": True},
            {"unit_id": units[7].id, "knowledge_point_id": kps[10].id, "code": "AMC8-B-L07", "title": "容斥原理与进阶计数", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "容斥原理：|A∪B| = |A| + |B| - |A∩B|"}, {"type": "text", "content": "例题：1到100中能被3或5整除的数有多少个？"}], "steps": []},
             "estimated_minutes": 35, "sort_order": 1, "is_published": True},
            {"unit_id": units[7].id, "knowledge_point_id": kps[11].id, "code": "AMC8-B-L08", "title": "概率与期望值", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "条件概率与期望值的概念和计算"}, {"type": "text", "content": "例题：袋子有3红球2蓝球，连续摸两个不返回，第二个是红球的概率？"}], "steps": []},
             "estimated_minutes": 35, "sort_order": 2, "is_published": True},

            # --- KET-A ---
            {"unit_id": units[8].id, "knowledge_point_id": kps[12].id, "code": "KET-A-L01", "title": "KET Core Vocabulary: Personal Info", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Learn vocabulary about personal information: name, age, family, hobbies, school subjects"}, {"type": "text", "content": "Practice: Introduce yourself using at least 5 sentences"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 1, "is_published": True},
            {"unit_id": units[8].id, "knowledge_point_id": kps[13].id, "code": "KET-A-L02", "title": "Everyday Expressions: Shopping & Food", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Learn expressions for shopping: How much is...? Can I have...? I'd like..."}, {"type": "text", "content": "Learn expressions for ordering food: I'll have..., a table for two, the bill please"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 2, "is_published": True},
            {"unit_id": units[8].id, "knowledge_point_id": kps[13].id, "code": "KET-A-L03", "title": "Everyday Expressions: Directions", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Learn directions vocabulary: turn left/right, go straight, opposite, next to"}, {"type": "text", "content": "Practice: How do I get to the station? It's on the corner of..."}], "steps": []},
             "estimated_minutes": 20, "sort_order": 3, "is_published": True},
            {"unit_id": units[9].id, "knowledge_point_id": kps[14].id, "code": "KET-A-L04", "title": "Present Simple & Past Simple", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Present Simple: habits, routines (I play tennis every day)"}, {"type": "text", "content": "Past Simple: completed actions (I went to the park yesterday)"}, {"type": "text", "content": "Practice: Convert sentences between present and past tense"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 1, "is_published": True},
            {"unit_id": units[9].id, "knowledge_point_id": kps[15].id, "code": "KET-A-L05", "title": "Sentence Structures", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "SVO (Subject + Verb + Object): I like pizza"}, {"type": "text", "content": "Questions: Do you...? Does he...? Did she...?"}, {"type": "text", "content": "Negatives: I don't like..., She doesn't play..."}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},
            {"unit_id": units[10].id, "knowledge_point_id": kps[16].id, "code": "KET-A-L06", "title": "Listening: Short Dialogues", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Practice listening to short dialogues and answering questions"}, {"type": "text", "content": "Key skills: identify speaker intention, time, location, and quantity"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 1, "is_published": True},
            {"unit_id": units[10].id, "knowledge_point_id": kps[19].id, "code": "KET-A-L07", "title": "Speaking: Self Introduction", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Practice introducing yourself: name, age, where you live, hobbies"}, {"type": "text", "content": "Common patterns: What do you like? I enjoy..., My favorite... is..."}], "steps": []},
             "estimated_minutes": 20, "sort_order": 2, "is_published": True},
            {"unit_id": units[11].id, "knowledge_point_id": kps[17].id, "code": "KET-A-L08", "title": "Reading: Short Texts", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Practice reading short notices, emails, and messages"}, {"type": "text", "content": "Key skills: identify main idea, find specific information, understand purpose"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 1, "is_published": True},
            {"unit_id": units[11].id, "knowledge_point_id": kps[18].id, "code": "KET-A-L09", "title": "Writing: Short Messages & Emails", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "Writing short messages (25-35 words): invite, suggest, apologise, thank"}, {"type": "text", "content": "Writing an informal email: greeting, body, closing"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},

            # --- CN-B5 (作文) ---
            {"unit_id": units[12].id, "knowledge_point_id": kps[20].id, "code": "CN-B5-L01", "title": "记叙文六要素", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "记叙文六要素：时间、地点、人物、起因、经过、结果"}, {"type": "text", "content": "练习：用六要素分析一篇范文《一件难忘的事》"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 1, "is_published": True},
            {"unit_id": units[12].id, "knowledge_point_id": kps[20].id, "code": "CN-B5-L02", "title": "叙事顺序与详略安排", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "顺叙、倒叙、插叙三种叙事顺序的特点和运用"}, {"type": "text", "content": "练习：将一件事用倒叙的方式重新组织，突出重点部分"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},
            {"unit_id": units[12].id, "knowledge_point_id": kps[24].id, "code": "CN-B5-L03", "title": "开头与结尾的写法", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "精彩开头的五种方法：开门见山、设问引入、环境描写、回忆开头、引用名言"}, {"type": "text", "content": "结尾技巧：首尾呼应、点题收束、抒情升华"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 3, "is_published": True},
            {"unit_id": units[13].id, "knowledge_point_id": kps[21].id, "code": "CN-B5-L04", "title": "人物外貌与动作描写", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "外貌描写：抓住特征，不要面面俱到"}, {"type": "text", "content": "动作描写：用准确的动词，写出动作的细节"}, {"type": "text", "content": "练习：写一段同学做操时的动作描写（不少于100字）"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 1, "is_published": True},
            {"unit_id": units[13].id, "knowledge_point_id": kps[21].id, "code": "CN-B5-L05", "title": "人物语言与心理描写", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "语言描写：符合人物身份，注意语气和标点"}, {"type": "text", "content": "心理描写：内心独白、联想想象、侧面烘托"}, {"type": "text", "content": "练习：写一段考试前紧张的心理活动"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},
            {"unit_id": units[13].id, "knowledge_point_id": kps[22].id, "code": "CN-B5-L06", "title": "景物描写技巧", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "多感官描写：视觉、听觉、嗅觉、触觉"}, {"type": "text", "content": "动静结合、虚实相生、借景抒情"}, {"type": "text", "content": "练习：用多感官描写校园的秋天（不少于150字）"}], "steps": []},
             "estimated_minutes": 30, "sort_order": 3, "is_published": True},
            {"unit_id": units[14].id, "knowledge_point_id": kps[23].id, "code": "CN-B5-L07", "title": "书信的格式与写法", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "书信六部分：称呼、问候语、正文、祝语、署名、日期"}, {"type": "text", "content": "练习：给远方的朋友写一封信，介绍你的校园生活"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 1, "is_published": True},
            {"unit_id": units[14].id, "knowledge_point_id": kps[23].id, "code": "CN-B5-L08", "title": "日记与读后感", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "日记格式：日期、天气、正文（真实感受）"}, {"type": "text", "content": "读后感结构：引（引述材料）→议（分析议论）→联（联系实际）→结（总结升华）"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},

            # --- CN-C4 (古诗词) ---
            {"unit_id": units[15].id, "knowledge_point_id": kps[25].id, "code": "CN-C4-L01", "title": "《静夜思》李白", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "床前明月光，疑是地上霜。举头望明月，低头思故乡。"}, {"type": "text", "content": "学习要点：理解「明月」意象寄托思乡之情，体会诗歌简洁而深远的意境"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 1, "is_published": True},
            {"unit_id": units[15].id, "knowledge_point_id": kps[25].id, "code": "CN-C4-L02", "title": "《春晓》孟浩然", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "春眠不觉晓，处处闻啼鸟。夜来风雨声，花落知多少。"}, {"type": "text", "content": "学习要点：感受诗人对春天的喜爱与惜春之情，理解「花落知多少」的感叹"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 2, "is_published": True},
            {"unit_id": units[15].id, "knowledge_point_id": kps[25].id, "code": "CN-C4-L03", "title": "《望庐山瀑布》李白", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "日照香炉生紫烟，遥看瀑布挂前川。飞流直下三千尺，疑是银河落九天。"}, {"type": "text", "content": "学习要点：夸张手法的运用，「三千尺」「银河」展现壮美景象"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 3, "is_published": True},
            {"unit_id": units[15].id, "knowledge_point_id": kps[25].id, "code": "CN-C4-L04", "title": "《绝句》杜甫", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "两个黄鹂鸣翠柳，一行白鹭上青天。窗含西岭千秋雪，门泊东吴万里船。"}, {"type": "text", "content": "学习要点：对仗工整（黄鹂-白鹭、翠柳-青天），色彩鲜明，空间层次感"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 4, "is_published": True},
            {"unit_id": units[16].id, "knowledge_point_id": kps[26].id, "code": "CN-C4-L05", "title": "《清平乐·村居》辛弃疾", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "茅檐低小，溪上青青草。醉里吴音相媚好，白发谁家翁媪？大儿锄豆溪东，中儿正织鸡笼。最喜小儿亡赖，溪头卧剥莲蓬。"}, {"type": "text", "content": "学习要点：词与诗的区别，白描手法展现田园生活的悠闲美好"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 1, "is_published": True},
            {"unit_id": units[16].id, "knowledge_point_id": kps[26].id, "code": "CN-C4-L06", "title": "《渔歌子》张志和", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "西塞山前白鹭飞，桃花流水鳜鱼肥。青箬笠，绿蓑衣，斜风细雨不须归。"}, {"type": "text", "content": "学习要点：色彩搭配（白鹭、桃花、青、绿），人与自然和谐的画面"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},
            {"unit_id": units[17].id, "knowledge_point_id": kps[27].id, "code": "CN-C4-L07", "title": "常见诗歌意象", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "月亮 = 思乡，柳树 = 离别，梅花 = 坚强，菊花 = 高洁，竹子 = 正直"}, {"type": "text", "content": "练习：判断诗歌中意象所表达的情感"}], "steps": []},
             "estimated_minutes": 20, "sort_order": 1, "is_published": True},
            {"unit_id": units[17].id, "knowledge_point_id": kps[28].id, "code": "CN-C4-L08", "title": "韵律与对仗", "lesson_type": "lecture",
             "content": {"blocks": [{"type": "text", "content": "押韵：诗句末尾字的韵母相同或相近"}, {"type": "text", "content": "对仗：词性相同、结构相同、意义相对（如「两个黄鹂」对「一行白鹭」）"}, {"type": "text", "content": "练习：判断诗句中哪些是对仗句"}], "steps": []},
             "estimated_minutes": 25, "sort_order": 2, "is_published": True},
            {"unit_id": units[17].id, "knowledge_point_id": kps[29].id, "code": "CN-C4-L09", "title": "古诗文背诵与默写训练", "lesson_type": "practice",
             "content": {"blocks": [{"type": "text", "content": "背诵技巧：理解记忆法、联想记忆法、反复朗读法"}, {"type": "text", "content": "默写要点：注意同音字、形近字的区分"}, {"type": "text", "content": "练习：默写本单元学过的全部古诗"}], "steps": []},
             "estimated_minutes": 30, "sort_order": 3, "is_published": True},
        ]

        lessons = []
        for l in lessons_data:
            lesson = Lesson(**l)
            db.add(lesson)
            lessons.append(lesson)
        await db.flush()

        # ============================================================
        # 6. PROBLEMS (all subjects)
        # ============================================================
        problems_data = [
            # --- AMC8-A math ---
            {"source": "AMC8", "source_year": 2024, "source_code": "AMC8-2024-01", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem 1\n\nWhat is the value of $2 + 2 \\times 3$?",
             "options": {"A": "8", "B": "12", "C": "10", "D": "6"}, "correct_answer": "A", "difficulty": 1, "estimated_time_sec": 60,
             "knowledge_point_ids": [str(kps[0].id)]},
            {"source": "AMC8", "source_year": 2024, "source_code": "AMC8-2024-02", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem 2\n\nA rectangle has a length of 8 and a width of 5. What is its perimeter?",
             "options": {"A": "13", "B": "26", "C": "40", "D": "30"}, "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 45,
             "knowledge_point_ids": [str(kps[2].id)]},
            {"source": "AMC8", "source_year": 2024, "source_code": "AMC8-2024-03", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem 3\n\nHow many positive integers less than 100 are divisible by both 3 and 5?",
             "options": {"A": "5", "B": "6", "C": "7", "D": "8"}, "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 120,
             "knowledge_point_ids": [str(kps[0].id)]},
            {"source": "AMC8", "source_year": 2024, "source_code": "AMC8-2024-04", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem 4\n\nIf $3x + 7 = 22$, what is $x$?",
             "options": {"A": "3", "B": "4", "C": "5", "D": "6"}, "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 60,
             "knowledge_point_ids": [str(kps[1].id)]},
            {"source": "AMC8", "source_year": 2024, "source_code": "AMC8-2024-05", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem 5\n\nIn how many ways can 3 students be arranged in a line?",
             "options": {"A": "3", "B": "6", "C": "9", "D": "12"}, "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 90,
             "knowledge_point_ids": [str(kps[3].id)]},

            # --- AMC8-B math ---
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-01", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nHow many positive divisors does $360$ have?",
             "options": {"A": "20", "B": "24", "C": "30", "D": "36"}, "correct_answer": "B", "difficulty": 3, "estimated_time_sec": 120,
             "knowledge_point_ids": [str(kps[4].id)]},
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-02", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nWhat is the remainder when $2^{100}$ is divided by $7$?",
             "options": {"A": "1", "B": "2", "C": "3", "D": "4"}, "correct_answer": "B", "difficulty": 3, "estimated_time_sec": 150,
             "knowledge_point_ids": [str(kps[5].id)]},
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-03", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nSolve: $2x + 3y = 13$ and $4x - y = 5$. What is $x + y$?",
             "options": {"A": "3", "B": "4", "C": "5", "D": "6"}, "correct_answer": "B", "difficulty": 3, "estimated_time_sec": 120,
             "knowledge_point_ids": [str(kps[6].id)]},
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-04", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nWhat is the sum $1 + 2 + 3 + \\cdots + 100$?",
             "options": {"A": "4950", "B": "5000", "C": "5050", "D": "5100"}, "correct_answer": "C", "difficulty": 2, "estimated_time_sec": 60,
             "knowledge_point_ids": [str(kps[7].id)]},
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-05", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nA circle has radius 6. What is the area of a $60°$ sector?",
             "options": {"A": "$4\\pi$", "B": "$6\\pi$", "C": "$8\\pi$", "D": "$12\\pi$"}, "correct_answer": "B", "difficulty": 3, "estimated_time_sec": 90,
             "knowledge_point_ids": [str(kps[8].id)]},
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-06", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nA rectangular box has dimensions $3 \\times 4 \\times 5$. What is its surface area?",
             "options": {"A": "47", "B": "60", "C": "74", "D": "94"}, "correct_answer": "D", "difficulty": 2, "estimated_time_sec": 90,
             "knowledge_point_ids": [str(kps[9].id)]},
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-07", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nHow many integers from 1 to 100 are divisible by 3 or 5?",
             "options": {"A": "43", "B": "45", "C": "47", "D": "53"}, "correct_answer": "C", "difficulty": 3, "estimated_time_sec": 120,
             "knowledge_point_ids": [str(kps[10].id)]},
            {"source": "AMC8", "source_year": 2023, "source_code": "AMC8B-2023-08", "subject": "math", "format": "mcq",
             "question_markdown": "## Problem\n\nA fair coin is flipped 3 times. What is the probability of getting exactly 2 heads?",
             "options": {"A": "$\\frac{1}{8}$", "B": "$\\frac{3}{8}$", "C": "$\\frac{1}{2}$", "D": "$\\frac{1}{4}$"}, "correct_answer": "B", "difficulty": 3, "estimated_time_sec": 90,
             "knowledge_point_ids": [str(kps[11].id)]},

            # --- KET english ---
            {"source": "KET", "source_year": 2024, "source_code": "KET-2024-01", "subject": "english", "format": "mcq",
             "question_markdown": "## Vocabulary\n\nChoose the correct word:\n\nMy sister is very good ___ playing the piano.",
             "options": {"A": "in", "B": "at", "C": "on", "D": "with"}, "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[12].id)]},
            {"source": "KET", "source_year": 2024, "source_code": "KET-2024-02", "subject": "english", "format": "mcq",
             "question_markdown": "## Vocabulary\n\nChoose the correct word:\n\nI usually ___ breakfast at 7 o'clock.",
             "options": {"A": "eat", "B": "eats", "C": "eating", "D": "ate"}, "correct_answer": "A", "difficulty": 1, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[14].id)]},
            {"source": "KET", "source_year": 2024, "source_code": "KET-2024-03", "subject": "english", "format": "mcq",
             "question_markdown": "## Grammar\n\nChoose the correct sentence:",
             "options": {"A": "She don't like pizza.", "B": "She doesn't likes pizza.", "C": "She doesn't like pizza.", "D": "She not like pizza."},
             "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 30, "knowledge_point_ids": [str(kps[15].id)]},
            {"source": "KET", "source_year": 2024, "source_code": "KET-2024-04", "subject": "english", "format": "mcq",
             "question_markdown": "## Grammar\n\nChoose the correct answer:\n\nWe ___ to the cinema last Saturday.",
             "options": {"A": "go", "B": "goes", "C": "went", "D": "going"}, "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[14].id)]},
            {"source": "KET", "source_year": 2024, "source_code": "KET-2024-05", "subject": "english", "format": "mcq",
             "question_markdown": "## Reading\n\nRead the notice and answer:\n\n> **NOTICE: The school library will be closed on Monday for cleaning. Please return all books by Friday.**\n\nWhen should you return your books?",
             "options": {"A": "Monday", "B": "Friday", "C": "Saturday", "D": "Sunday"}, "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 60,
             "knowledge_point_ids": [str(kps[17].id)]},
            {"source": "KET", "source_year": 2024, "source_code": "KET-2024-06", "subject": "english", "format": "mcq",
             "question_markdown": "## Reading\n\n> Hi Tom, I can't come to your party on Saturday because I have a football match. Can we meet on Sunday instead? — Alex\n\nWhy can't Alex go to the party?",
             "options": {"A": "He is sick.", "B": "He has a football match.", "C": "He doesn't like parties.", "D": "He has to study."},
             "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 60, "knowledge_point_ids": [str(kps[17].id)]},
            {"source": "KET", "source_year": 2024, "source_code": "KET-2024-07", "subject": "english", "format": "mcq",
             "question_markdown": "## Listening\n\nYou hear: \"Excuse me, where is the nearest post office?\" \"Go straight ahead and turn left at the traffic lights.\"\n\nWhere is the post office?",
             "options": {"A": "On the right.", "B": "Straight ahead on the left.", "C": "Behind the traffic lights.", "D": "Next to the bank."},
             "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 45, "knowledge_point_ids": [str(kps[16].id)]},

            # --- CN-C4 (古诗词) ---
            {"source": "校内", "source_year": 2024, "source_code": "CN-C4-2024-01", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 古诗理解\n\n「床前明月光，疑是地上霜」中，诗人把月光比作了什么？",
             "options": {"A": "水", "B": "霜", "C": "雪", "D": "白云"}, "correct_answer": "B", "difficulty": 1, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[25].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-C4-2024-02", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 古诗理解\n\n「飞流直下三千尺，疑是银河落九天」使用了什么修辞手法？",
             "options": {"A": "比喻", "B": "拟人", "C": "排比", "D": "夸张"}, "correct_answer": "D", "difficulty": 2, "estimated_time_sec": 45,
             "knowledge_point_ids": [str(kps[25].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-C4-2024-03", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 古诗理解\n\n「两个黄鹂鸣翠柳，一行白鹭上青天」中，哪组词构成了对仗？",
             "options": {"A": "两个 — 青天", "B": "黄鹂 — 一行", "C": "黄鹂 — 白鹭", "D": "翠柳 — 上青"}, "correct_answer": "C", "difficulty": 2, "estimated_time_sec": 60,
             "knowledge_point_ids": [str(kps[28].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-C4-2024-04", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 诗歌意象\n\n古诗中「柳」通常代表什么含义？",
             "options": {"A": "春天", "B": "离别", "C": "坚强", "D": "高洁"}, "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[27].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-C4-2024-05", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 默写填空\n\n「春眠不觉晓，处处闻___鸟。」请填入正确的字。",
             "options": {"A": "啼", "B": "鸣", "C": "叫", "D": "唱"}, "correct_answer": "A", "difficulty": 1, "estimated_time_sec": 20,
             "knowledge_point_ids": [str(kps[29].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-C4-2024-06", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 词的特点\n\n以下哪一首是「词」而不是「诗」？",
             "options": {"A": "《静夜思》", "B": "《春晓》", "C": "《清平乐·村居》", "D": "《望庐山瀑布》"}, "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[26].id)]},

            # --- CN-B5 (作文) ---
            {"source": "校内", "source_year": 2024, "source_code": "CN-B5-2024-01", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 写作知识\n\n记叙文的六要素不包括以下哪一项？",
             "options": {"A": "时间", "B": "地点", "C": "人物", "D": "论点"}, "correct_answer": "D", "difficulty": 1, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[20].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-B5-2024-02", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 写作知识\n\n「他的脸红得像苹果」用了什么描写方法？",
             "options": {"A": "动作描写", "B": "语言描写", "C": "外貌描写", "D": "心理描写"}, "correct_answer": "C", "difficulty": 1, "estimated_time_sec": 30,
             "knowledge_point_ids": [str(kps[21].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-B5-2024-03", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 写作知识\n\n书信的正确格式顺序是？",
             "options": {"A": "称呼→正文→问候语→祝语→署名→日期", "B": "称呼→问候语→正文→祝语→署名→日期", "C": "正文→称呼→问候语→祝语→署名→日期", "D": "称呼→问候语→正文→日期→署名→祝语"},
             "correct_answer": "B", "difficulty": 2, "estimated_time_sec": 45, "knowledge_point_ids": [str(kps[23].id)]},
            {"source": "校内", "source_year": 2024, "source_code": "CN-B5-2024-04", "subject": "chinese", "format": "mcq",
             "question_markdown": "## 写作知识\n\n以下哪种不是景物描写的技巧？",
             "options": {"A": "多感官描写", "B": "动静结合", "C": "列数字说明", "D": "借景抒情"}, "correct_answer": "C", "difficulty": 2, "estimated_time_sec": 45,
             "knowledge_point_ids": [str(kps[22].id)]},
        ]

        for p in problems_data:
            problem = Problem(**p)
            db.add(problem)
        await db.flush()

        # ============================================================
        # 7. LEARNING SESSIONS
        # ============================================================
        now = datetime.now(timezone.utc)
        sessions_data = [
            {
                "student_id": student.id,
                "session_type": "practice",
                "subject": "math",
                "knowledge_point_id": kps[0].id,
                "started_at": now - timedelta(hours=2),
                "ended_at": now - timedelta(hours=2, minutes=-25),
                "duration_sec": 1500,
                "problems_total": 5,
                "problems_correct": 4,
                "score_pct": 80.0,
                "xp_earned": 40,
                "summary": "练习了整除与余数，正确率80%",
            },
            {
                "student_id": student.id,
                "session_type": "practice",
                "subject": "math",
                "knowledge_point_id": kps[1].id,
                "started_at": now - timedelta(days=1),
                "ended_at": now - timedelta(days=1, minutes=-20),
                "duration_sec": 1200,
                "problems_total": 4,
                "problems_correct": 3,
                "score_pct": 75.0,
                "xp_earned": 30,
                "summary": "方程求解练习",
            },
        ]

        for s in sessions_data:
            session = LearningSession(**s)
            db.add(session)

        await db.commit()

        # Print summary
        print("✅ Seed data created successfully!")
        print(f"  Users: teststudent (student), testparent (parent), password: test123")
        print(f"  Courses: {len(courses)}")
        for c in courses:
            cid = str(c.id)
            u_count = sum(1 for u in units if str(u.course_id) == cid)
            l_count = sum(1 for ld in lessons_data if any(str(u.id) == str(ld["unit_id"]) and str(u.course_id) == cid for u in units))
            print(f"    {c.code} ({c.name}): {u_count} units, {l_count} lessons")
        print(f"  Total Units: {len(units)}")
        print(f"  Total Lessons: {len(lessons_data)}")
        print(f"  Total Knowledge Points: {len(kps)}")
        print(f"  Total Problems: {len(problems_data)}")
        print(f"  Learning Sessions: {len(sessions_data)}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
