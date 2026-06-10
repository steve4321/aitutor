"""AMC Math curriculum data — parsed from course-catalog.md

This module defines all AMC 8 and AMC 10 curriculum data as pure Python
dicts/lists. A separate seed script will consume this data and insert
it into the database.

Structure:
  AMC_COURSES            → Course + nested Unit + nested Lesson dicts
  AMC_KNOWLEDGE_POINTS   → KnowledgePoint dicts (one per lesson code)
  AMC_KNOWLEDGE_DEPENDENCIES → prerequisite → target pairs
  AMC_PROBLEMS           → Problem dicts with AMC-style questions
"""

# ─────────────────────────────────────────────────────────────────────
# Helper: minimal valid lesson content JSON
# ─────────────────────────────────────────────────────────────────────
def _content(
    objectives: list[str],
    key_points: list[str],
    common_mistakes: list[str] | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "subject": "amc_math",
        "lesson_type": "concept",
        "steps": [],
        "objectives": objectives,
        "summary": {
            "key_points": key_points,
            "common_mistakes": common_mistakes or [],
        },
    }


def _assessment_content(title: str, description: str) -> dict:
    return {
        "schema_version": "1.0",
        "subject": "amc_math",
        "lesson_type": "assessment",
        "steps": [],
        "objectives": [description],
        "summary": {"key_points": [title], "common_mistakes": []},
    }


def _diagnostic_content() -> dict:
    return {
        "schema_version": "1.0",
        "subject": "amc_math",
        "lesson_type": "diagnostic",
        "steps": [],
        "objectives": [
            "评估学生对 AMC 8 各支柱的掌握程度",
            "生成知识画像",
            "判断可跳过的已掌握模块",
        ],
        "summary": {
            "key_points": ["10道跨领域诊断题", "覆盖代数、几何、计数、数论四大支柱"],
            "common_mistakes": [],
        },
    }



# ═══════════════════════════════════════════════════════════════════════
# AMC COURSES
# ═══════════════════════════════════════════════════════════════════════

AMC_COURSES = [
    # ── AMC 8 ──────────────────────────────────────────────────────
    {
        "code": "AMC8",
        "subject": "amc_math",
        "name": "AMC 8 数学竞赛",
        "description": "AMC 8 竞赛基础课程，涵盖代数、几何、计数与概率、数论四大支柱",
        "target_exam": "AMC8",
        "estimated_hours": 14,
        "is_published": True,
        "units": [
            {
                "code": "AMC8-DIAG",
                "name": "入学诊断",
                "description": "AMC 8 入学诊断测试，评估学生各支柱基础",
                "sort_order": 0,
                "required_mastery": 0.0,
                "lessons": [
                    {
                        "code": "DIAG-AMC",
                        "title": "入学诊断",
                        "lesson_type": "diagnostic",
                        "knowledge_point_code": None,
                        "estimated_minutes": 45,
                        "sort_order": 1,
                        "is_published": True,
                        "content": _diagnostic_content(),
                    },
                ],
            },
            {
                "code": "AMC8-ALGEBRA",
                "name": "代数 (Algebra)",
                "description": "AMC 8 代数基础：一次方程、方程组、函数入门、比例百分比、指数与根式",
                "sort_order": 1,
                "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "A1", "title": "一次方程与不等式",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A1",
                        "estimated_minutes": 40, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["理解一元一次方程的求解方法", "掌握移项和合并同类项", "能解含括号的一次方程", "理解一元一次不等式及其解法"],
                            key_points=["移项要变号", "合并同类项", "去括号时注意符号", "不等式两边乘除负数要变号"],
                            common_mistakes=["移项忘记变号", "去括号时括号前为负号未全部变号", "不等式方向忘记反转"],
                        ),
                    },
                    {
                        "code": "A2", "title": "方程组",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A2",
                        "estimated_minutes": 40, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["理解二元一次方程组的概念", "掌握代入消元法", "掌握加减消元法", "能解含参数的方程组"],
                            key_points=["代入法：用一个未知数表示另一个", "加减法：消去一个未知数", "选择使计算简单的消元方式"],
                            common_mistakes=["代入时忘记替换全部项", "加减法符号错误", "消元系数计算错误"],
                        ),
                    },
                    {
                        "code": "A3", "title": "函数入门(定义、图像、一次函数)",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A3",
                        "estimated_minutes": 40, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["理解函数的定义和表示", "掌握平面直角坐标系", "理解一次函数 y=kx+b 的图像与斜率", "能根据条件确定一次函数表达式"],
                            key_points=["函数：每个输入对应唯一输出", "斜率 k = Δy/Δx", "截距 b 的意义"],
                            common_mistakes=["混淆斜率和截距", "计算斜率时 x, y 差值顺序反了", "函数与方程混淆"],
                        ),
                    },
                    {
                        "code": "A4", "title": "比例、百分比、比率",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A4",
                        "estimated_minutes": 35, "sort_order": 4, "is_published": True,
                        "content": _content(
                            objectives=["掌握比例的基本性质", "熟练进行百分比的转换和运算", "理解比率的概念和应用"],
                            key_points=["比例的交叉相乘", "百分数转小数", "增长率 = (新-旧)/旧 × 100%"],
                            common_mistakes=["百分数加减直接运算", "基数搞错", "比例单位不统一"],
                        ),
                    },
                    {
                        "code": "A5", "title": "指数与根式",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A5",
                        "estimated_minutes": 40, "sort_order": 5, "is_published": True,
                        "content": _content(
                            objectives=["掌握指数运算法则", "理解零指数幂和负指数", "能化简根式", "掌握科学计数法"],
                            key_points=["a^m · a^n = a^(m+n)", "(a^m)^n = a^(mn)", "√a = a^(1/2)", "a^0 = 1"],
                            common_mistakes=["(a+b)² ≠ a² + b²", "负指数理解错误", "根式化简未化到最简"],
                        ),
                    },
                    {
                        "code": "TEST-A1", "title": "阶段测试A-1",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 30, "sort_order": 6, "is_published": True,
                        "content": _assessment_content("代数阶段测试 A-1", "综合 A1-A5，测试代数基础掌握程度"),
                    },
                ],
            },
            {
                "code": "AMC8-GEOMETRY",
                "name": "几何 (Geometry)",
                "description": "AMC 8 几何基础：角度与平行线、三角形、勾股定理、四边形与多边形、组合图形面积",
                "sort_order": 2, "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "B1", "title": "角度与平行线",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B1",
                        "estimated_minutes": 35, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["掌握对顶角、邻补角的概念", "理解平行线截线形成的角的关系", "掌握同位角、内错角、同旁内角"],
                            key_points=["对顶角相等", "两直线平行则同位角相等、内错角相等", "同旁内角互补"],
                            common_mistakes=["混淆同位角和内错角", "忘了'两直线平行'这个前提条件"],
                        ),
                    },
                    {
                        "code": "B2", "title": "三角形(面积、全等)",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B2",
                        "estimated_minutes": 40, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["掌握三角形面积公式", "理解三角形内角和为180°", "掌握SSS/SAS/ASA全等判定", "理解等腰三角形和等边三角形性质"],
                            key_points=["面积 S = (1/2)bh", "内角和180°", "全等判定：SSS, SAS, ASA, AAS"],
                            common_mistakes=["底和高对应关系搞错", "全等判定条件不够就用", "等腰三角形的底角和高混淆"],
                        ),
                    },
                    {
                        "code": "B3", "title": "勾股定理",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B3",
                        "estimated_minutes": 40, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["掌握勾股定理 a²+b²=c²", "记住常见勾股数 (3-4-5, 5-12-13, 8-15-17)", "能用逆定理判断直角三角形"],
                            key_points=["a²+b²=c²", "常见勾股数", "逆定理：若 a²+b²=c² 则为直角三角形"],
                            common_mistakes=["斜边和直角边搞反", "忘记勾股定理只适用于直角三角形", "不会在非直角三角形中构造直角"],
                        ),
                    },
                    {
                        "code": "B5", "title": "四边形与多边形",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B5",
                        "estimated_minutes": 40, "sort_order": 4, "is_published": True,
                        "content": _content(
                            objectives=["掌握平行四边形、梯形性质", "掌握正多边形内角和公式", "理解外角和恒为360°"],
                            key_points=["n边形内角和 = (n-2)×180°", "外角和 = 360°", "平行四边形对边相等、对角相等"],
                            common_mistakes=["内角和公式记错", "正多边形每个内角的度数算错", "梯形面积公式中上下底搞反"],
                        ),
                    },
                    {
                        "code": "B7", "title": "组合图形面积计算",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B7",
                        "estimated_minutes": 40, "sort_order": 5, "is_published": True,
                        "content": _content(
                            objectives=["掌握割补法求面积", "掌握差集法", "掌握网格面积（Pick's theorem）"],
                            key_points=["割补法：分割成已知图形", "差集法：大减小", "Pick定理: S = I + B/2 - 1"],
                            common_mistakes=["割补后重复计算", "忘记减去空白部分", "Pick定理边界点数错"],
                        ),
                    },
                    {
                        "code": "TEST-B", "title": "阶段测试B",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 30, "sort_order": 6, "is_published": True,
                        "content": _assessment_content("几何阶段测试 B", "综合几何全部内容 (B1-B7)"),
                    },
                ],
            },
            {
                "code": "AMC8-COUNTING",
                "name": "计数与概率 (Counting & Probability)",
                "description": "AMC 8 计数基础：加法乘法原理、排列、组合、基础概率",
                "sort_order": 3, "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "C1", "title": "加法原理与乘法原理",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C1",
                        "estimated_minutes": 35, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["理解分类计数（加法原理）", "理解分步计数（乘法原理）", "能用树形图辅助计数"],
                            key_points=["加法：分类 → 加", "乘法：分步 → 乘", "画树形图帮助理解"],
                            common_mistakes=["分类遗漏或重复", "混淆加法和乘法的使用场景", "分步时步骤不独立"],
                        ),
                    },
                    {
                        "code": "C2", "title": "排列",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C2",
                        "estimated_minutes": 40, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["理解排列的概念", "掌握排列数公式 P(n,k) = n!/(n-k)!", "能解决排列应用题"],
                            key_points=["排列：有序选取", "P(n,k) = n(n-1)…(n-k+1)", "n! = 1×2×…×n"],
                            common_mistakes=["排列组合混淆", "n! 计算错误", "有重复元素时未去重"],
                        ),
                    },
                    {
                        "code": "C3", "title": "组合基础",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C3",
                        "estimated_minutes": 40, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["理解组合的概念（无序选取）", "掌握基本组合数计算 C(n,k)=n!/(k!(n-k)!)", "能区分排列和组合的使用场景"],
                            key_points=["组合：无序选取", "C(n,k) = C(n,n-k)", "排列有序，组合无序"],
                            common_mistakes=["排列组合混淆", "组合数公式计算错误", "重复计数"],
                        ),
                    },
                    {
                        "code": "C5", "title": "基础概率",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C5",
                        "estimated_minutes": 40, "sort_order": 4, "is_published": True,
                        "content": _content(
                            objectives=["理解古典概型", "掌握互斥事件的概率加法", "掌握独立事件的概率乘法"],
                            key_points=["P(A) = |A|/|Ω|", "互斥：P(A∪B) = P(A)+P(B)", "独立：P(A∩B) = P(A)·P(B)"],
                            common_mistakes=["分母算错（样本空间遗漏）", "互斥和独立混淆", "不返回抽样时忘记调整分母"],
                        ),
                    },
                    {
                        "code": "TEST-C1", "title": "阶段测试C-1",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 30, "sort_order": 5, "is_published": True,
                        "content": _assessment_content("计数与概率阶段测试 C-1", "综合计数基础内容 (C1-C5)"),
                    },
                ],
            },
            {
                "code": "AMC8-NUMTHEORY",
                "name": "数论 (Number Theory)",
                "description": "AMC 8 数论基础：整除、质因数分解、GCD与LCM",
                "sort_order": 4, "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "D1", "title": "整除与整除规则",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-NT-D1",
                        "estimated_minutes": 40, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["掌握被 2, 3, 4, 5, 9 整除的判定法则", "掌握被 11 整除的判定法则", "能综合运用整除性质"],
                            key_points=["3的倍数：各位数字之和能被3整除", "9的倍数：各位数字之和能被9整除", "11的倍数：奇偶位数字和之差能被11整除"],
                            common_mistakes=["4和8的整除判定看整个数而不是末位", "11的判定法则方向搞反", "整除和因数的概念混淆"],
                        ),
                    },
                    {
                        "code": "D2", "title": "质数与质因数分解",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-NT-D2",
                        "estimated_minutes": 40, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["理解质数的定义", "掌握唯一分解定理", "能进行质因数分解", "掌握约数个数公式"],
                            key_points=["质数：大于1，只有1和自身两个因子", "唯一分解：n = p1^a1 · p2^a2 · …", "约数个数 = (a1+1)(a2+1)…"],
                            common_mistakes=["1不是质数", "忘记唯一分解中的指数", "约数个数公式中+1遗漏"],
                        ),
                    },
                    {
                        "code": "D3", "title": "GCD与LCM(辗转相除法)",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-NT-D3",
                        "estimated_minutes": 40, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["理解最大公约数和最小公倍数", "掌握辗转相除法", "掌握 gcd×lcm = a×b"],
                            key_points=["辗转相除法：gcd(a,b) = gcd(b, a mod b)", "gcd × lcm = a × b", "利用质因数分解求GCD/LCM"],
                            common_mistakes=["辗转相除法终止条件错误", "GCD和LCM搞反", "质因数分解时指数取错"],
                        ),
                    },
                    {
                        "code": "TEST-D1", "title": "阶段测试D-1",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 30, "sort_order": 4, "is_published": True,
                        "content": _assessment_content("数论阶段测试 D-1", "综合数论基础内容 (D1-D3)"),
                    },
                ],
            },
        ],
    },

    # ── AMC 10 ─────────────────────────────────────────────────────
    {
        "code": "AMC10",
        "subject": "amc_math",
        "name": "AMC 10 数学竞赛",
        "description": "AMC 10 竞赛进阶课程，在 AMC 8 基础上深入各大支柱",
        "target_exam": "AMC10",
        "estimated_hours": 16,
        "is_published": True,
        "units": [
            {
                "code": "AMC10-ALGEBRA",
                "name": "代数进阶 (Algebra Advanced)",
                "description": "AMC 10 代数进阶：二次方程、因式分解、函数进阶、数列",
                "sort_order": 0, "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "A6", "title": "二次方程 — 因式分解法",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A6",
                        "estimated_minutes": 45, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["理解二次方程的一般形式", "掌握十字相乘法", "能用因式分解法解二次方程"],
                            key_points=["ax²+bx+c = 0", "十字相乘：找 m,n 使得 m+n=b, mn=ac", "ax²+bx+c = a(x-r1)(x-r2)"],
                            common_mistakes=["十字相乘时符号错误", "忘记验证因式分解的正确性", "首项系数不为1时处理不当"],
                        ),
                    },
                    {
                        "code": "A7", "title": "二次方程 — 配方法与求根公式",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A7",
                        "estimated_minutes": 45, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["掌握配方法", "理解判别式 Δ=b²-4ac", "掌握求根公式"],
                            key_points=["配方法步骤", "Δ>0: 两个不等实根", "Δ=0: 两个相等实根", "Δ<0: 无实根"],
                            common_mistakes=["配方时系数处理错误", "判别式符号判断错", "求根公式中 2a 在分母忘记"],
                        ),
                    },
                    {
                        "code": "A8", "title": "特殊因式分解(差平方、立方和差)",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A8",
                        "estimated_minutes": 40, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["掌握平方差公式 a²-b²=(a+b)(a-b)", "掌握立方和 a³+b³=(a+b)(a²-ab+b²)", "掌握立方差 a³-b³=(a-b)(a²+ab+b²)"],
                            key_points=["a²-b²=(a+b)(a-b)", "a³+b³=(a+b)(a²-ab+b²)", "a³-b³=(a-b)(a²+ab+b²)"],
                            common_mistakes=["立方公式中间项符号搞反", "把立方和当成 (a+b)³", "多次运用时遗漏项"],
                        ),
                    },
                    {
                        "code": "A9", "title": "函数进阶(复合、反函数、二次函数图像)",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A9",
                        "estimated_minutes": 45, "sort_order": 4, "is_published": True,
                        "content": _content(
                            objectives=["理解复合函数 f(g(x))", "理解反函数的概念和求法", "掌握二次函数图像的顶点、对称轴"],
                            key_points=["复合函数：先内后外", "反函数：f⁻¹ 满足 f(f⁻¹(x)) = x", "y=ax²+bx+c 顶点 (-b/(2a), f(-b/(2a)))"],
                            common_mistakes=["复合函数顺序搞反", "反函数求解时忘记定义域限制", "顶点坐标公式记错"],
                        ),
                    },
                    {
                        "code": "A10", "title": "数列(等差、等比、求和、望远镜求和)",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-ALG-A10",
                        "estimated_minutes": 45, "sort_order": 5, "is_published": True,
                        "content": _content(
                            objectives=["掌握等差数列通项与求和", "掌握等比数列通项与求和", "理解裂项相消"],
                            key_points=["等差：an=a1+(n-1)d, Sn=n(a1+an)/2", "等比：an=a1·r^(n-1)", "裂项：1/(n(n+1)) = 1/n - 1/(n+1)"],
                            common_mistakes=["等比数列公比为1时公式不适用", "裂项相消后剩下哪些项搞不清", "求和公式中n的含义搞混"],
                        ),
                    },
                    {
                        "code": "TEST-A2", "title": "阶段测试A-2",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 35, "sort_order": 6, "is_published": True,
                        "content": _assessment_content("代数进阶阶段测试 A-2", "综合 AMC 10 代数进阶内容 (A6-A10)"),
                    },
                ],
            },
            {
                "code": "AMC10-GEOMETRY",
                "name": "几何进阶 (Geometry Advanced)",
                "description": "AMC 10 几何进阶：相似三角形、圆、坐标几何、立体几何",
                "sort_order": 1, "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "B4", "title": "相似三角形",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B4",
                        "estimated_minutes": 40, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["掌握AA/SSS/SAS相似判定", "理解相似比与面积比的关系", "能运用相似三角形解决综合题"],
                            key_points=["AA相似：两个角相等", "相似比 k → 面积比 k²", "相似比 k → 体积比 k³"],
                            common_mistakes=["面积比忘记平方", "相似判定条件不充分", "对应边找错"],
                        ),
                    },
                    {
                        "code": "B6", "title": "圆(圆心角、圆周角、切割线、Power of a Point)",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B6",
                        "estimated_minutes": 45, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["理解圆心角与圆周角的关系", "掌握切线性质", "理解割线定理和Power of a Point"],
                            key_points=["圆周角 = 圆心角的一半", "切线 ⊥ 半径", "Power of a Point: PA·PB = PC·PD"],
                            common_mistakes=["圆周角和圆心角关系记反", "切线性质应用时忘记直角", "Power of a Point中线段方向搞错"],
                        ),
                    },
                    {
                        "code": "B8", "title": "坐标几何",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B8",
                        "estimated_minutes": 45, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["掌握两点距离公式", "掌握中点公式", "能用坐标法证明几何命题", "理解直线方程的各种形式"],
                            key_points=["距离: d=√((x2-x1)²+(y2-y1)²)", "中点: M=((x1+x2)/2, (y1+y2)/2)", "斜率: m=(y2-y1)/(x2-x1)"],
                            common_mistakes=["距离公式忘记开方", "中点公式用错", "垂直直线斜率关系记错"],
                        ),
                    },
                    {
                        "code": "B9", "title": "立体几何",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-GEO-B9",
                        "estimated_minutes": 40, "sort_order": 4, "is_published": True,
                        "content": _content(
                            objectives=["掌握正方体、长方体的表面积与体积", "掌握圆柱、圆锥的表面积与体积", "理解展开图"],
                            key_points=["长方体表面积 = 2(ab+bc+ac)", "圆柱体积 = πr²h", "圆锥体积 = (1/3)πr²h"],
                            common_mistakes=["表面积和体积公式混淆", "圆锥体积忘记1/3", "展开图中扇形弧长计算错误"],
                        ),
                    },
                    {
                        "code": "TEST-B2", "title": "几何进阶阶段测试",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 35, "sort_order": 5, "is_published": True,
                        "content": _assessment_content("几何进阶阶段测试 B-2", "综合 AMC 10 几何进阶内容 (B4, B6, B8, B9)"),
                    },
                ],
            },
            {
                "code": "AMC10-COUNTING",
                "name": "计数进阶 (Counting Advanced)",
                "description": "AMC 10 计数进阶：组合、二项式定理、互补计数、容斥原理、递推、期望值",
                "sort_order": 2, "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "C3", "title": "组合",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C3",
                        "estimated_minutes": 40, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["理解组合的概念（无序选取）", "掌握组合数公式 C(n,k)", "能解决组合应用题"],
                            key_points=["组合：无序选取", "C(n,k) = C(n,n-k)", "P(n,k) = C(n,k)·k!"],
                            common_mistakes=["排列和组合混淆", "组合数公式计算错误", "重复计数"],
                        ),
                    },
                    {
                        "code": "C4", "title": "杨辉三角与二项式定理",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C4",
                        "estimated_minutes": 40, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["理解杨辉三角的构造与性质", "掌握二项式定理", "能求特定项系数"],
                            key_points=["杨辉三角每项 = C(n,k)", "第r项系数 = C(n,r-1)", "C(n,k) = C(n-1,k-1)+C(n-1,k)"],
                            common_mistakes=["项数和指数搞混", "通项公式中a,b的指数写反", "特定项是第几项算错"],
                        ),
                    },
                    {
                        "code": "C6", "title": "互补计数与分类讨论",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C6",
                        "estimated_minutes": 40, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["掌握正难则反的互补计数思想", "掌握补集思想", "能进行多情况分类讨论"],
                            key_points=["所求 = 全部 - 不满足的", "分类要不重不漏", "互补有时大幅简化计算"],
                            common_mistakes=["分类时遗漏情况", "互补时全集算错", "间接计数时边界条件遗漏"],
                        ),
                    },
                    {
                        "code": "C7", "title": "容斥原理",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C7",
                        "estimated_minutes": 40, "sort_order": 4, "is_published": True,
                        "content": _content(
                            objectives=["掌握两集合容斥公式", "掌握三集合容斥公式", "能用Venn图辅助理解"],
                            key_points=["|A∪B| = |A|+|B|-|A∩B|", "|A∪B∪C| = |A|+|B|+|C|-|A∩B|-|A∩C|-|B∩C|+|A∩B∩C|"],
                            common_mistakes=["三集合容斥忘记加回三交集", "符号搞反", "硬套公式"],
                        ),
                    },
                    {
                        "code": "C8", "title": "递推",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C8",
                        "estimated_minutes": 45, "sort_order": 5, "is_published": True,
                        "content": _content(
                            objectives=["理解递推关系的概念", "掌握斐波那契数列", "能用递推解决计数问题"],
                            key_points=["递推：an = f(a(n-1), …)", "斐波那契: Fn = F(n-1)+F(n-2)", "关键是找递推关系和初始条件"],
                            common_mistakes=["初始条件遗漏", "递推关系建立错误", "递推和通项公式混淆"],
                        ),
                    },
                    {
                        "code": "C9", "title": "期望值",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-CNT-C9",
                        "estimated_minutes": 40, "sort_order": 6, "is_published": True,
                        "content": _content(
                            objectives=["理解数学期望的定义", "掌握期望的线性性", "能解决期望值应用题"],
                            key_points=["E[X] = Σ xi·P(xi)", "E[X+Y] = E[X]+E[Y]", "E[aX] = aE[X]"],
                            common_mistakes=["期望和概率混淆", "线性性误用", "分母计算错误"],
                        ),
                    },
                    {
                        "code": "TEST-C2", "title": "计数进阶阶段测试",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 35, "sort_order": 7, "is_published": True,
                        "content": _assessment_content("计数进阶阶段测试 C-2", "综合 AMC 10 计数进阶内容 (C3-C9)"),
                    },
                ],
            },
            {
                "code": "AMC10-NUMTHEORY",
                "name": "数论进阶 (Number Theory Advanced)",
                "description": "AMC 10 数论进阶：余数与同余、进位制、不定方程、欧拉定理",
                "sort_order": 3, "required_mastery": 0.8,
                "lessons": [
                    {
                        "code": "D4", "title": "余数与同余基础",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-NT-D4",
                        "estimated_minutes": 40, "sort_order": 1, "is_published": True,
                        "content": _content(
                            objectives=["理解同余的定义 a≡b (mod m)", "掌握模运算的性质", "能解同余方程"],
                            key_points=["a≡b (mod m) 意味着 m|(a-b)", "同余可加、可乘", "模运算保持等式两边"],
                            common_mistakes=["同余中不能随便除", "负数的模运算方向搞反", "忘记同余只处理整数"],
                        ),
                    },
                    {
                        "code": "D5", "title": "进位制",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-NT-D5",
                        "estimated_minutes": 40, "sort_order": 2, "is_published": True,
                        "content": _content(
                            objectives=["理解二进制、八进制、十六进制", "掌握不同进位制之间的转换", "能进行进位制运算"],
                            key_points=["n进制按位权展开", "十进制转n进制：不断除以n取余", "n进制转十进制：按位权展开"],
                            common_mistakes=["转换方向搞反", "十六进制中A-F对应关系记错", "进位制加减忘记进位"],
                        ),
                    },
                    {
                        "code": "D6", "title": "不定方程",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-NT-D6",
                        "estimated_minutes": 45, "sort_order": 3, "is_published": True,
                        "content": _content(
                            objectives=["理解二元一次不定方程", "掌握整数解的判定条件", "能求不定方程的全部整数解"],
                            key_points=["ax+by=c 有解 ⟺ gcd(a,b)|c", "特解+通解结构", "x=x0+(b/d)t, y=y0-(a/d)t"],
                            common_mistakes=["忘记判定GCD整除条件", "通解公式中符号写反", "非负整数解的范围搞错"],
                        ),
                    },
                    {
                        "code": "D7", "title": "欧拉定理入门",
                        "lesson_type": "concept", "knowledge_point_code": "AMC-NT-D7",
                        "estimated_minutes": 45, "sort_order": 4, "is_published": True,
                        "content": _content(
                            objectives=["理解欧拉函数 φ(n) 的定义和计算", "掌握费马小定理", "理解欧拉定理"],
                            key_points=["φ(n) = n∏(1-1/pi)", "费马小定理: a^(p-1)≡1 (mod p)", "gcd(a,n)=1 时欧拉定理成立"],
                            common_mistakes=["费马小定理要求p是质数", "欧拉函数计算时遗漏质因子", "指数降幂时GCD条件不满足"],
                        ),
                    },
                    {
                        "code": "TEST-D2", "title": "数论进阶阶段测试",
                        "lesson_type": "assessment", "knowledge_point_code": None,
                        "estimated_minutes": 35, "sort_order": 5, "is_published": True,
                        "content": _assessment_content("数论进阶阶段测试 D-2", "综合 AMC 10 数论进阶内容 (D4-D7)"),
                    },
                ],
            },
        ],
    },
]


# ═══════════════════════════════════════════════════════════════════════
# AMC KNOWLEDGE POINTS
# ═══════════════════════════════════════════════════════════════════════

AMC_KNOWLEDGE_POINTS = [
    # ── AMC 8 — Algebra ──
    {"code": "AMC-ALG-A1", "subject": "amc_math", "name": "一次方程与不等式", "name_en": "Linear Equations and Inequalities", "description": "一元一次方程求解、不等式、移项", "pillar": "algebra", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 101, "estimated_minutes": 40},
    {"code": "AMC-ALG-A2", "subject": "amc_math", "name": "方程组", "name_en": "Systems of Equations", "description": "二元一次方程组、代入法、消元法", "pillar": "algebra", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 102, "estimated_minutes": 40},
    {"code": "AMC-ALG-A3", "subject": "amc_math", "name": "函数入门", "name_en": "Introduction to Functions", "description": "函数概念、坐标系、一次函数图像与斜率", "pillar": "algebra", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 103, "estimated_minutes": 40},
    {"code": "AMC-ALG-A4", "subject": "amc_math", "name": "比例、百分比、比率", "name_en": "Ratios, Percentages, and Proportions", "description": "比例运算、百分比转换、比率应用", "pillar": "algebra", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 104, "estimated_minutes": 35},
    {"code": "AMC-ALG-A5", "subject": "amc_math", "name": "指数与根式", "name_en": "Exponents and Radicals", "description": "指数法则、根式化简、科学计数法", "pillar": "algebra", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 105, "estimated_minutes": 40},
    # ── AMC 8 — Geometry ──
    {"code": "AMC-GEO-B1", "subject": "amc_math", "name": "角度与平行线", "name_en": "Angles and Parallel Lines", "description": "对顶角、同位角、内错角、互补角", "pillar": "geometry", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 201, "estimated_minutes": 35},
    {"code": "AMC-GEO-B2", "subject": "amc_math", "name": "三角形(面积、全等)", "name_en": "Triangles: Area and Congruence", "description": "三角形面积公式、SSS/SAS/ASA全等判定", "pillar": "geometry", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 202, "estimated_minutes": 40},
    {"code": "AMC-GEO-B3", "subject": "amc_math", "name": "勾股定理", "name_en": "Pythagorean Theorem", "description": "a²+b²=c²、勾股数、逆定理", "pillar": "geometry", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 203, "estimated_minutes": 40},
    {"code": "AMC-GEO-B5", "subject": "amc_math", "name": "四边形与多边形", "name_en": "Quadrilaterals and Polygons", "description": "平行四边形、梯形、正多边形内角和", "pillar": "geometry", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 205, "estimated_minutes": 40},
    {"code": "AMC-GEO-B7", "subject": "amc_math", "name": "组合图形面积计算", "name_en": "Composite Figure Areas", "description": "割补法、差集法、网格面积", "pillar": "geometry", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 207, "estimated_minutes": 40},
    # ── AMC 8 — Counting ──
    {"code": "AMC-CNT-C1", "subject": "amc_math", "name": "加法原理与乘法原理", "name_en": "Addition and Multiplication Principles", "description": "分类计数、分步计数、树形图", "pillar": "counting", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 301, "estimated_minutes": 35},
    {"code": "AMC-CNT-C2", "subject": "amc_math", "name": "排列", "name_en": "Permutations", "description": "排列数公式P(n,k)、排列应用", "pillar": "counting", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 302, "estimated_minutes": 40},
    {"code": "AMC-CNT-C5", "subject": "amc_math", "name": "基础概率", "name_en": "Basic Probability", "description": "古典概型、互斥事件、独立事件", "pillar": "counting", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 305, "estimated_minutes": 40},
    # ── AMC 8 — Number Theory ──
    {"code": "AMC-NT-D1", "subject": "amc_math", "name": "整除与整除规则", "name_en": "Divisibility Rules", "description": "整除判定、被2/3/4/5/9/11整除的特征", "pillar": "number_theory", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 401, "estimated_minutes": 40},
    {"code": "AMC-NT-D2", "subject": "amc_math", "name": "质数与质因数分解", "name_en": "Primes and Prime Factorization", "description": "质数判定、唯一分解定理、质因数分解", "pillar": "number_theory", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 402, "estimated_minutes": 40},
    {"code": "AMC-NT-D3", "subject": "amc_math", "name": "GCD与LCM", "name_en": "GCD and LCM", "description": "最大公约数、最小公倍数、辗转相除法", "pillar": "number_theory", "difficulty_level": 2, "amc_level": 8, "amc_levels": "8", "sort_order": 403, "estimated_minutes": 40},
    # ── AMC 10 — Algebra ──
    {"code": "AMC-ALG-A6", "subject": "amc_math", "name": "二次方程 — 因式分解法", "name_en": "Quadratic Equations: Factoring", "description": "二次方程、十字相乘、因式分解求解", "pillar": "algebra", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 106, "estimated_minutes": 45},
    {"code": "AMC-ALG-A7", "subject": "amc_math", "name": "二次方程 — 配方法与求根公式", "name_en": "Quadratic Equations: Completing the Square & Quadratic Formula", "description": "配方法、判别式、求根公式", "pillar": "algebra", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 107, "estimated_minutes": 45},
    {"code": "AMC-ALG-A8", "subject": "amc_math", "name": "特殊因式分解", "name_en": "Special Factoring: Difference of Squares, Sum/Difference of Cubes", "description": "平方差、立方和/差公式", "pillar": "algebra", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 108, "estimated_minutes": 40},
    {"code": "AMC-ALG-A9", "subject": "amc_math", "name": "函数进阶", "name_en": "Advanced Functions: Composition, Inverses, Quadratics", "description": "复合函数、反函数、二次函数顶点与对称轴", "pillar": "algebra", "difficulty_level": 4, "amc_level": 10, "amc_levels": "10", "sort_order": 109, "estimated_minutes": 45},
    {"code": "AMC-ALG-A10", "subject": "amc_math", "name": "数列", "name_en": "Sequences: Arithmetic, Geometric, and Telescoping", "description": "等差/等比数列通项与求和、裂项相消", "pillar": "algebra", "difficulty_level": 4, "amc_level": 10, "amc_levels": "10", "sort_order": 110, "estimated_minutes": 45},
    # ── AMC 10 — Geometry ──
    {"code": "AMC-GEO-B4", "subject": "amc_math", "name": "相似三角形", "name_en": "Similar Triangles", "description": "AA/SSS/SAS相似判定、相似比与面积比", "pillar": "geometry", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 204, "estimated_minutes": 40},
    {"code": "AMC-GEO-B6", "subject": "amc_math", "name": "圆", "name_en": "Circles: Angles, Tangents, Power of a Point", "description": "圆心角与圆周角关系、切线性质、割线定理", "pillar": "geometry", "difficulty_level": 4, "amc_level": 10, "amc_levels": "10", "sort_order": 206, "estimated_minutes": 45},
    {"code": "AMC-GEO-B8", "subject": "amc_math", "name": "坐标几何", "name_en": "Coordinate Geometry", "description": "两点距离、中点公式、直线方程、坐标法证几何", "pillar": "geometry", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 208, "estimated_minutes": 45},
    {"code": "AMC-GEO-B9", "subject": "amc_math", "name": "立体几何", "name_en": "Solid Geometry", "description": "表面积与体积、正方体/圆柱/圆锥、展开图", "pillar": "geometry", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 209, "estimated_minutes": 40},
    # ── AMC 10 — Counting ──
    {"code": "AMC-CNT-C3", "subject": "amc_math", "name": "组合", "name_en": "Combinations", "description": "组合数公式C(n,k)、组合应用", "pillar": "counting", "difficulty_level": 3, "amc_level": 10, "amc_levels": "8,10", "sort_order": 303, "estimated_minutes": 40},
    {"code": "AMC-CNT-C4", "subject": "amc_math", "name": "杨辉三角与二项式定理", "name_en": "Pascal's Triangle and Binomial Theorem", "description": "杨辉三角性质、二项式展开、系数", "pillar": "counting", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 304, "estimated_minutes": 40},
    {"code": "AMC-CNT-C6", "subject": "amc_math", "name": "互补计数与分类讨论", "name_en": "Complementary Counting and Casework", "description": "正难则反、补集思想、多情况分类", "pillar": "counting", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 306, "estimated_minutes": 40},
    {"code": "AMC-CNT-C7", "subject": "amc_math", "name": "容斥原理", "name_en": "Inclusion-Exclusion Principle", "description": "两集合/三集合容斥、Venn图", "pillar": "counting", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 307, "estimated_minutes": 40},
    {"code": "AMC-CNT-C8", "subject": "amc_math", "name": "递推", "name_en": "Recurrence Relations", "description": "递推关系、斐波那契、通项公式", "pillar": "counting", "difficulty_level": 4, "amc_level": 10, "amc_levels": "10", "sort_order": 308, "estimated_minutes": 45},
    {"code": "AMC-CNT-C9", "subject": "amc_math", "name": "期望值", "name_en": "Expected Value", "description": "数学期望定义、线性性、期望应用", "pillar": "counting", "difficulty_level": 4, "amc_level": 10, "amc_levels": "10", "sort_order": 309, "estimated_minutes": 40},
    # ── AMC 10 — Number Theory ──
    {"code": "AMC-NT-D4", "subject": "amc_math", "name": "余数与同余基础", "name_en": "Modular Arithmetic", "description": "同余定义、模运算、同余方程", "pillar": "number_theory", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 404, "estimated_minutes": 40},
    {"code": "AMC-NT-D5", "subject": "amc_math", "name": "进位制", "name_en": "Number Bases", "description": "二进制、八进制、十六进制转换", "pillar": "number_theory", "difficulty_level": 3, "amc_level": 10, "amc_levels": "10", "sort_order": 405, "estimated_minutes": 40},
    {"code": "AMC-NT-D6", "subject": "amc_math", "name": "不定方程", "name_en": "Diophantine Equations", "description": "二元一次不定方程、整数解、丢番图方程", "pillar": "number_theory", "difficulty_level": 4, "amc_level": 10, "amc_levels": "10", "sort_order": 406, "estimated_minutes": 45},
    {"code": "AMC-NT-D7", "subject": "amc_math", "name": "欧拉定理入门", "name_en": "Introduction to Euler's Theorem", "description": "欧拉函数、费马小定理、模逆元", "pillar": "number_theory", "difficulty_level": 4, "amc_level": 10, "amc_levels": "10", "sort_order": 407, "estimated_minutes": 45},
]


# ═══════════════════════════════════════════════════════════════════════
# AMC KNOWLEDGE DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════

AMC_KNOWLEDGE_DEPENDENCIES = [
    # ── Algebra ──
    {"prerequisite_code": "AMC-ALG-A1", "target_code": "AMC-ALG-A2"},
    {"prerequisite_code": "AMC-ALG-A1", "target_code": "AMC-ALG-A3"},
    {"prerequisite_code": "AMC-ALG-A1", "target_code": "AMC-ALG-A4"},
    {"prerequisite_code": "AMC-ALG-A1", "target_code": "AMC-ALG-A5"},
    {"prerequisite_code": "AMC-ALG-A2", "target_code": "AMC-ALG-A3"},
    {"prerequisite_code": "AMC-ALG-A5", "target_code": "AMC-ALG-A6"},
    {"prerequisite_code": "AMC-ALG-A6", "target_code": "AMC-ALG-A7"},
    {"prerequisite_code": "AMC-ALG-A6", "target_code": "AMC-ALG-A8"},
    {"prerequisite_code": "AMC-ALG-A5", "target_code": "AMC-ALG-A8"},
    {"prerequisite_code": "AMC-ALG-A5", "target_code": "AMC-ALG-A10"},
    {"prerequisite_code": "AMC-ALG-A3", "target_code": "AMC-ALG-A9"},
    {"prerequisite_code": "AMC-ALG-A7", "target_code": "AMC-ALG-A9"},
    {"prerequisite_code": "AMC-ALG-A3", "target_code": "AMC-ALG-A10"},
    # ── Geometry ──
    {"prerequisite_code": "AMC-GEO-B1", "target_code": "AMC-GEO-B2"},
    {"prerequisite_code": "AMC-GEO-B2", "target_code": "AMC-GEO-B3"},
    {"prerequisite_code": "AMC-GEO-B3", "target_code": "AMC-GEO-B4"},
    {"prerequisite_code": "AMC-GEO-B3", "target_code": "AMC-GEO-B6"},
    {"prerequisite_code": "AMC-GEO-B3", "target_code": "AMC-GEO-B8"},
    {"prerequisite_code": "AMC-GEO-B2", "target_code": "AMC-GEO-B5"},
    {"prerequisite_code": "AMC-GEO-B2", "target_code": "AMC-GEO-B7"},
    {"prerequisite_code": "AMC-GEO-B2", "target_code": "AMC-GEO-B9"},
    {"prerequisite_code": "AMC-GEO-B5", "target_code": "AMC-GEO-B7"},
    {"prerequisite_code": "AMC-GEO-B5", "target_code": "AMC-GEO-B9"},
    {"prerequisite_code": "AMC-GEO-B4", "target_code": "AMC-GEO-B6"},
    # ── Counting ──
    {"prerequisite_code": "AMC-CNT-C1", "target_code": "AMC-CNT-C2"},
    {"prerequisite_code": "AMC-CNT-C1", "target_code": "AMC-CNT-C5"},
    {"prerequisite_code": "AMC-CNT-C2", "target_code": "AMC-CNT-C3"},
    {"prerequisite_code": "AMC-CNT-C2", "target_code": "AMC-CNT-C6"},
    {"prerequisite_code": "AMC-CNT-C2", "target_code": "AMC-CNT-C8"},
    {"prerequisite_code": "AMC-CNT-C3", "target_code": "AMC-CNT-C4"},
    {"prerequisite_code": "AMC-CNT-C3", "target_code": "AMC-CNT-C7"},
    {"prerequisite_code": "AMC-CNT-C3", "target_code": "AMC-CNT-C9"},
    {"prerequisite_code": "AMC-CNT-C5", "target_code": "AMC-CNT-C9"},
    # ── Number Theory ──
    {"prerequisite_code": "AMC-NT-D1", "target_code": "AMC-NT-D2"},
    {"prerequisite_code": "AMC-NT-D1", "target_code": "AMC-NT-D5"},
    {"prerequisite_code": "AMC-NT-D2", "target_code": "AMC-NT-D3"},
    {"prerequisite_code": "AMC-NT-D2", "target_code": "AMC-NT-D7"},
    {"prerequisite_code": "AMC-NT-D3", "target_code": "AMC-NT-D4"},
    {"prerequisite_code": "AMC-NT-D4", "target_code": "AMC-NT-D6"},
    {"prerequisite_code": "AMC-NT-D4", "target_code": "AMC-NT-D7"},
    # ── Cross-pillar ──
    {"prerequisite_code": "AMC-ALG-A1", "target_code": "AMC-NT-D6"},
    {"prerequisite_code": "AMC-ALG-A3", "target_code": "AMC-GEO-B8"},
]


# ═══════════════════════════════════════════════════════════════════════
# AMC PROBLEMS
# ═══════════════════════════════════════════════════════════════════════

AMC_PROBLEMS = [
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-A1-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nIf $3(x - 2) + 5 = 2x + 7$, what is $x$?",
        "options": {
            "A": "4",
            "B": "6",
            "C": "8",
            "D": "10",
            "E": "12"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-ALG-A1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Expand the left side first."
            },
            {
                "level": 1,
                "text": "3x-6+5=2x+7 → 3x-1=2x+7."
            },
            {
                "level": 2,
                "text": "Subtract 2x: x-1=7."
            },
            {
                "level": 3,
                "text": "x=8."
            },
            {
                "level": 4,
                "text": "Check: 3(6)+5=23, 16+7=23. Actually 3(8-2)+5=23=2(8)+7. x=8, answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-A1-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nSolve the inequality $2x - 3 < 7$.",
        "options": {
            "A": "x < 2",
            "B": "x < 5",
            "C": "x > 5",
            "D": "x > 2",
            "E": "x < -5"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Add 3 to both sides."
            },
            {
                "level": 1,
                "text": "2x < 10."
            },
            {
                "level": 2,
                "text": "Divide by 2: x < 5."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "Check: x=4 gives 5<7 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2022,
        "source_code": "AMC8-2022-A1-03",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nIf $5 - 2(x + 3) = 1$, find $x$.",
        "options": None,
        "correct_answer": "-1",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-ALG-A1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Distribute the -2."
            },
            {
                "level": 1,
                "text": "5-2x-6=1, so -2x-1=1."
            },
            {
                "level": 2,
                "text": "-2x=2, x=-1."
            },
            {
                "level": 3,
                "text": "Check: 5-2(-1+3)=5-4=1 ✓."
            },
            {
                "level": 4,
                "text": "Answer: -1."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-A2-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nIf $2x + 3y = 13$ and $4x - y = 5$, what is $x + y$?",
        "options": {
            "A": "3",
            "B": "4",
            "C": "5",
            "D": "6",
            "E": "7"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-ALG-A2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Try elimination or substitution."
            },
            {
                "level": 1,
                "text": "From eq 2: y=4x-5."
            },
            {
                "level": 2,
                "text": "2x+3(4x-5)=13 → 14x=28 → x=2, y=3."
            },
            {
                "level": 3,
                "text": "x+y=5."
            },
            {
                "level": 4,
                "text": "Check: 2(2)+3(3)=13 ✓, 4(2)-3=5 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-A2-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nTickets cost $3 for children and $5 for adults. A group bought 10 tickets for $42. How many children?",
        "options": {
            "A": "3",
            "B": "4",
            "C": "5",
            "D": "6",
            "E": "7"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-ALG-A2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Let c=children, a=adults. Set up equations."
            },
            {
                "level": 1,
                "text": "c+a=10 and 3c+5a=42."
            },
            {
                "level": 2,
                "text": "a=10-c → 3c+5(10-c)=42 → -2c+50=42 → c=4."
            },
            {
                "level": 3,
                "text": "Answer B, 4 children."
            },
            {
                "level": 4,
                "text": "Check: 4 children + 6 adults = 10 tickets. 3(4)+5(6)=42 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-A3-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA line passes through $(1, 3)$ and $(3, 7)$. What is the slope?",
        "options": {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4",
            "E": "5"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Use m=(y₂-y₁)/(x₂-x₁)."
            },
            {
                "level": 1,
                "text": "m=(7-3)/(3-1)=4/2."
            },
            {
                "level": 2,
                "text": "m=2."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "Right 2, up 4 → slope 2 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-A3-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nThe function $f(x) = 2x - 5$ is graphed. What is the $y$-intercept?",
        "options": {
            "A": "(0, -5)",
            "B": "(0, 2)",
            "C": "(0, 5)",
            "D": "(0, -2)",
            "E": "(0, 3)"
        },
        "correct_answer": "A",
        "difficulty": 2,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-ALG-A3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "y-intercept: x=0."
            },
            {
                "level": 1,
                "text": "f(0)=2(0)-5=-5."
            },
            {
                "level": 2,
                "text": "(0,-5)."
            },
            {
                "level": 3,
                "text": "Answer A."
            },
            {
                "level": 4,
                "text": "In y=kx+b, b=-5 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-A4-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA shirt costs $\\$40$ and is on sale for $25\\%$ off. What is the sale price?",
        "options": {
            "A": "$\\$10$",
            "B": "$\\$25$",
            "C": "$\\$30$",
            "D": "$\\$35$",
            "E": "$\\$15$"
        },
        "correct_answer": "C",
        "difficulty": 1,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Calculate 25% of 40, then subtract."
            },
            {
                "level": 1,
                "text": "Discount=0.25×40=10."
            },
            {
                "level": 2,
                "text": "40-10=30."
            },
            {
                "level": 3,
                "text": "Or: pay 75% → 0.75×40=30."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-A4-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nThe ratio of boys to girls is $3:5$. If 40 students total, how many girls?",
        "options": {
            "A": "15",
            "B": "20",
            "C": "25",
            "D": "24",
            "E": "30"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "3+5=8 parts total."
            },
            {
                "level": 1,
                "text": "Each part=40/8=5."
            },
            {
                "level": 2,
                "text": "Girls=5×5=25."
            },
            {
                "level": 3,
                "text": "Check: Boys=15, Girls=25, Total=40 ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-A5-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nSimplify $\\frac{2^6 \\times 2^3}{2^5}$.",
        "options": {
            "A": "8",
            "B": "16",
            "C": "32",
            "D": "64",
            "E": "4"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Use a^m×a^n=a^(m+n) and a^m/a^n=a^(m-n)."
            },
            {
                "level": 1,
                "text": "2^6×2^3=2^9."
            },
            {
                "level": 2,
                "text": "2^9/2^5=2^4=16."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "2^4=16 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-A5-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nExpress $\\sqrt{72}$ as $a\\sqrt{b}$. What is $a+b$?",
        "options": None,
        "correct_answer": "8",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-ALG-A5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Find the largest perfect square factor of 72."
            },
            {
                "level": 1,
                "text": "72=36×2, 36=6²."
            },
            {
                "level": 2,
                "text": "√72=6√2, a=6, b=2."
            },
            {
                "level": 3,
                "text": "a+b=8."
            },
            {
                "level": 4,
                "text": "Answer: 8."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-B1-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nTwo parallel lines cut by a transversal. One angle is $75°$. What is the same-side interior angle?",
        "options": {
            "A": "75°",
            "B": "105°",
            "C": "85°",
            "D": "95°",
            "E": "115°"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Same-side interior angles are supplementary."
            },
            {
                "level": 1,
                "text": "180°-75°=105°."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "75°+105°=180° ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-B1-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nParallel lines create angles $x°$ and $3x°$ on the same side. What is $x$?",
        "options": {
            "A": "30",
            "B": "35",
            "C": "40",
            "D": "45",
            "E": "50"
        },
        "correct_answer": "D",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Same-side interior angles sum to 180°."
            },
            {
                "level": 1,
                "text": "x+3x=180, 4x=180."
            },
            {
                "level": 2,
                "text": "x=45."
            },
            {
                "level": 3,
                "text": "Check: 45+135=180 ✓."
            },
            {
                "level": 4,
                "text": "Answer D."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-B2-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA triangle has base 10 and height 6. What is its area?",
        "options": {
            "A": "16",
            "B": "20",
            "C": "30",
            "D": "60",
            "E": "15"
        },
        "correct_answer": "C",
        "difficulty": 1,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-GEO-B2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Area=(1/2)×base×height."
            },
            {
                "level": 1,
                "text": "(1/2)×10×6=30."
            },
            {
                "level": 2,
                "text": "Answer C."
            },
            {
                "level": 3,
                "text": "Rectangle 10×6=60, triangle is half ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-B2-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nIn triangle $ABC$, $\\angle A=50°$ and $\\angle B=70°$. What is $\\angle C$?",
        "options": {
            "A": "40°",
            "B": "50°",
            "C": "60°",
            "D": "70°",
            "E": "80°"
        },
        "correct_answer": "C",
        "difficulty": 1,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-GEO-B2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Triangle angles sum to 180°."
            },
            {
                "level": 1,
                "text": "180-50-70=60°."
            },
            {
                "level": 2,
                "text": "Answer C."
            },
            {
                "level": 3,
                "text": "50+70+60=180 ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-B3-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA right triangle has legs 5 and 12. What is the hypotenuse?",
        "options": {
            "A": "11",
            "B": "13",
            "C": "14",
            "D": "15",
            "E": "17"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "a²+b²=c²."
            },
            {
                "level": 1,
                "text": "c²=25+144=169."
            },
            {
                "level": 2,
                "text": "c=13."
            },
            {
                "level": 3,
                "text": "Classic 5-12-13 triple."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-B3-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nHypotenuse is 10, one leg is 6. What is the other leg?",
        "options": None,
        "correct_answer": "8",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "a²+b²=c²."
            },
            {
                "level": 1,
                "text": "36+b²=100."
            },
            {
                "level": 2,
                "text": "b²=64, b=8."
            },
            {
                "level": 3,
                "text": "6-8-10 triangle (3-4-5 ×2)."
            },
            {
                "level": 4,
                "text": "Answer: 8."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-B5-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is the sum of interior angles of a regular hexagon?",
        "options": {
            "A": "540°",
            "B": "720°",
            "C": "900°",
            "D": "1080°",
            "E": "360°"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Sum=(n-2)×180°."
            },
            {
                "level": 1,
                "text": "(6-2)×180°=720°."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "Each angle=720/6=120°."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-B5-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA trapezoid has bases 8 and 14, height 5. What is its area?",
        "options": {
            "A": "40",
            "B": "50",
            "C": "55",
            "D": "60",
            "E": "70"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "A=(1/2)(b₁+b₂)h."
            },
            {
                "level": 1,
                "text": "(1/2)(8+14)(5)=55."
            },
            {
                "level": 2,
                "text": "Answer C."
            },
            {
                "level": 3,
                "text": "Average bases=11, ×5=55 ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-B7-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA square side 8 has a circle radius 4 inscribed. Area inside square but outside circle?",
        "options": {
            "A": "64 - 16π",
            "B": "64 - 8π",
            "C": "32 - 16π",
            "D": "16 - 4π",
            "E": "64 - 4π"
        },
        "correct_answer": "A",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-GEO-B7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Square area minus circle area."
            },
            {
                "level": 1,
                "text": "Square=64, Circle=16π."
            },
            {
                "level": 2,
                "text": "64-16π."
            },
            {
                "level": 3,
                "text": "Answer A."
            },
            {
                "level": 4,
                "text": "Answer A."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-B7-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nRectangle $AB=10$, $BC=6$. Triangle $ABE$ with $E$ on $CD$, $DE=4$. Area of triangle $ABE$?",
        "options": {
            "A": "20",
            "B": "25",
            "C": "30",
            "D": "35",
            "E": "40"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-GEO-B7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Base AB=10. Height?"
            },
            {
                "level": 1,
                "text": "Height=BC=6 (perpendicular from E to AB)."
            },
            {
                "level": 2,
                "text": "Area=(1/2)×10×6=30."
            },
            {
                "level": 3,
                "text": "Position of E doesn't affect area."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-C1-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA restaurant offers 3 appetizers, 5 mains, 2 desserts. How many different meals?",
        "options": {
            "A": "10",
            "B": "15",
            "C": "20",
            "D": "25",
            "E": "30"
        },
        "correct_answer": "E",
        "difficulty": 1,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-CNT-C1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Multiply choices at each step."
            },
            {
                "level": 1,
                "text": "3×5×2=?"
            },
            {
                "level": 2,
                "text": "=30."
            },
            {
                "level": 3,
                "text": "Answer E."
            },
            {
                "level": 4,
                "text": "Multiplication principle ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-C1-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nHow many two-digit positive integers have at least one digit equal to 7?",
        "options": {
            "A": "16",
            "B": "17",
            "C": "18",
            "D": "19",
            "E": "20"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-CNT-C1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Use complement: total 90 minus those with no 7."
            },
            {
                "level": 1,
                "text": "No 7: 8×9=72."
            },
            {
                "level": 2,
                "text": "90-72=18."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "Or: tens=7:10, ones=7:9, overlap(77):1. 10+9-1=18 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-C2-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nHow many ways can 4 students line up?",
        "options": {
            "A": "12",
            "B": "16",
            "C": "24",
            "D": "48",
            "E": "64"
        },
        "correct_answer": "C",
        "difficulty": 1,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-CNT-C2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "4!=P(4,4)."
            },
            {
                "level": 1,
                "text": "4!=4×3×2×1."
            },
            {
                "level": 2,
                "text": "=24."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "4×3×2×1=24 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-C2-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nFrom 7 members, choose president and VP. How many ways?",
        "options": {
            "A": "14",
            "B": "21",
            "C": "35",
            "D": "42",
            "E": "49"
        },
        "correct_answer": "D",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-CNT-C2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "P(7,2): order matters."
            },
            {
                "level": 1,
                "text": "7×6=42."
            },
            {
                "level": 2,
                "text": "Answer D."
            },
            {
                "level": 3,
                "text": "7 choices for president, 6 for VP ✓."
            },
            {
                "level": 4,
                "text": "Answer D."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-C5-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA fair die rolled twice. Probability sum is 7?",
        "options": {
            "A": "1/12",
            "B": "1/9",
            "C": "1/6",
            "D": "5/36",
            "E": "7/36"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-CNT-C5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Count ways to sum to 7."
            },
            {
                "level": 1,
                "text": "(1,6),(2,5),(3,4),(4,3),(5,2),(6,1) → 6 ways."
            },
            {
                "level": 2,
                "text": "6/36=1/6."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "6 out of 36 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-C5-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA bag has 3 red and 5 blue marbles. P(red)?",
        "options": {
            "A": "3/5",
            "B": "3/8",
            "C": "5/8",
            "D": "1/2",
            "E": "1/3"
        },
        "correct_answer": "B",
        "difficulty": 1,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-CNT-C5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "P=favorable/total."
            },
            {
                "level": 1,
                "text": "Red=3, Total=8."
            },
            {
                "level": 2,
                "text": "P=3/8."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "3 out of 8 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-D1-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhich number is divisible by 9?",
        "options": {
            "A": "1234",
            "B": "2345",
            "C": "3456",
            "D": "4567",
            "E": "5678"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-NT-D1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Digit sum divisible by 9?"
            },
            {
                "level": 1,
                "text": "Sums: A=10, B=14, C=18, D=22, E=26."
            },
            {
                "level": 2,
                "text": "Only 18 is divisible by 9 → 3456."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "3456/9=384 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-D1-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nHow many positive integers less than 1000 are divisible by both 3 and 5?",
        "options": {
            "A": "62",
            "B": "63",
            "C": "66",
            "D": "65",
            "E": "64"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-NT-D1"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Divisible by both = divisible by lcm(3,5)=15."
            },
            {
                "level": 1,
                "text": "⌊999/15⌋=66."
            },
            {
                "level": 2,
                "text": "Answer C."
            },
            {
                "level": 3,
                "text": "15×66=990<1000 ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-D2-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nHow many positive divisors does $360$ have?",
        "options": {
            "A": "20",
            "B": "24",
            "C": "30",
            "D": "36",
            "E": "48"
        },
        "correct_answer": "B",
        "difficulty": 2,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-NT-D2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Prime factorize 360."
            },
            {
                "level": 1,
                "text": "360=2³×3²×5¹."
            },
            {
                "level": 2,
                "text": "Divisors=(3+1)(2+1)(1+1)=4×3×2=24."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-D2-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is the largest prime factor of $2024$?",
        "options": {
            "A": "23",
            "B": "11",
            "C": "43",
            "D": "47",
            "E": "2"
        },
        "correct_answer": "A",
        "difficulty": 2,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-NT-D2"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Divide by 2 first."
            },
            {
                "level": 1,
                "text": "2024=2³×253."
            },
            {
                "level": 2,
                "text": "253=11×23. Largest=23."
            },
            {
                "level": 3,
                "text": "Answer A."
            },
            {
                "level": 4,
                "text": "2024=8×11×23=2³×11×23 ✓."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2024,
        "source_code": "AMC8-2024-D3-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is $\\text{lcm}(12, 18)$?",
        "options": {
            "A": "24",
            "B": "36",
            "C": "48",
            "D": "72",
            "E": "6"
        },
        "correct_answer": "B",
        "difficulty": 1,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-NT-D3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "12=2²×3, 18=2×3². LCM=max exponents."
            },
            {
                "level": 1,
                "text": "LCM=2²×3²=36."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "Or: gcd=6, lcm=12×18/6=36 ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC8",
        "source_year": 2023,
        "source_code": "AMC8-2023-D3-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is $\\gcd(252, 198)$ using Euclidean algorithm?",
        "options": {
            "A": "6",
            "B": "12",
            "C": "18",
            "D": "24",
            "E": "9"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-NT-D3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "gcd(a,b)=gcd(b, a mod b)."
            },
            {
                "level": 1,
                "text": "gcd(252,198)=gcd(198,54)=gcd(54,36)=gcd(36,18)=18."
            },
            {
                "level": 2,
                "text": "Answer C."
            },
            {
                "level": 3,
                "text": "18|252 and 18|198 ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-A6-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nFind all solutions to $x^2 - 5x + 6 = 0$.",
        "options": {
            "A": "x = 2, 3",
            "B": "x = -2, -3",
            "C": "x = 1, 6",
            "D": "x = -1, 6",
            "E": "x = -2, 3"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Find two numbers: multiply to 6, add to -5."
            },
            {
                "level": 1,
                "text": "-2 and -3."
            },
            {
                "level": 2,
                "text": "(x-2)(x-3)=0 → x=2 or 3."
            },
            {
                "level": 3,
                "text": "Answer A."
            },
            {
                "level": 4,
                "text": "Check: 4-10+6=0 ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-A6-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nFor what $k$ does $x^2+kx+9=0$ have exactly one solution?",
        "options": {
            "A": "±3",
            "B": "±6",
            "C": "6",
            "D": "-6",
            "E": "±9"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-ALG-A6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "One solution → Δ=0."
            },
            {
                "level": 1,
                "text": "k²-36=0, k=±6."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "x²+6x+9=(x+3)² ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-A7-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is the larger solution of $2x^2+3x-2=0$?",
        "options": {
            "A": "1/2",
            "B": "2",
            "C": "-2",
            "D": "2/3",
            "E": "-1/2"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-ALG-A7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Factor: (2x-1)(x+2)=0."
            },
            {
                "level": 1,
                "text": "x=1/2 or x=-2."
            },
            {
                "level": 2,
                "text": "Larger is 1/2."
            },
            {
                "level": 3,
                "text": "Answer A."
            },
            {
                "level": 4,
                "text": "Check: 2(1/4)+3/2-2=0 ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-A7-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is the discriminant of $x^2-4x+5=0$?",
        "options": {
            "A": "-4",
            "B": "4",
            "C": "-16",
            "D": "16",
            "E": "0"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Δ=b²-4ac."
            },
            {
                "level": 1,
                "text": "16-20=-4."
            },
            {
                "level": 2,
                "text": "Δ<0, no real solutions."
            },
            {
                "level": 3,
                "text": "Answer A."
            },
            {
                "level": 4,
                "text": "Parabola doesn't cross x-axis ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-A8-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nFactor $x^3 - 8$ completely.",
        "options": {
            "A": "(x-2)(x²+2x+4)",
            "B": "(x-2)(x²+4x+4)",
            "C": "(x+2)(x²-2x+4)",
            "D": "(x-2)(x²-2x+4)",
            "E": "(x-8)(x²+8x+64)"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A8"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Difference of cubes: a³-b³=(a-b)(a²+ab+b²)."
            },
            {
                "level": 1,
                "text": "a=x, b=2: (x-2)(x²+2x+4)."
            },
            {
                "level": 2,
                "text": "Answer A."
            },
            {
                "level": 3,
                "text": "Expand to verify ✓."
            },
            {
                "level": 4,
                "text": "Answer A."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-A8-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nSimplify $\\frac{x^2 - 9}{x + 3}$ for $x \\neq -3$.",
        "options": None,
        "correct_answer": "x - 3",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A8"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Factor numerator: difference of squares."
            },
            {
                "level": 1,
                "text": "x²-9=(x+3)(x-3)."
            },
            {
                "level": 2,
                "text": "Cancel (x+3): x-3."
            },
            {
                "level": 3,
                "text": "Answer: x-3."
            },
            {
                "level": 4,
                "text": "Answer: x-3."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-A9-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nIf $f(x)=2x+1$ and $g(x)=x^2$, what is $f(g(3))$?",
        "options": {
            "A": "7",
            "B": "19",
            "C": "37",
            "D": "49",
            "E": "81"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A9"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Evaluate g(3) first."
            },
            {
                "level": 1,
                "text": "g(3)=9."
            },
            {
                "level": 2,
                "text": "f(9)=2(9)+1=19."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "f(g(x)): apply g first, then f ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-A9-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat are the vertex coordinates of $y=x^2-6x+5$?",
        "options": {
            "A": "(3, -4)",
            "B": "(3, 4)",
            "C": "(3, -5)",
            "D": "(-3, -4)",
            "E": "(6, 5)"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-ALG-A9"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Vertex x=-b/(2a)."
            },
            {
                "level": 1,
                "text": "x=6/2=3."
            },
            {
                "level": 2,
                "text": "y=9-18+5=-4. Vertex=(3,-4)."
            },
            {
                "level": 3,
                "text": "Or: y=(x-3)²-4 ✓."
            },
            {
                "level": 4,
                "text": "Answer A."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-A10-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is $1+2+3+\\cdots+100$?",
        "options": {
            "A": "4950",
            "B": "5000",
            "C": "5050",
            "D": "5100",
            "E": "5150"
        },
        "correct_answer": "C",
        "difficulty": 2,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-ALG-A10"
        ],
        "hints": [
            {
                "level": 0,
                "text": "S_n=n(a₁+aₙ)/2."
            },
            {
                "level": 1,
                "text": "100(1+100)/2=5050."
            },
            {
                "level": 2,
                "text": "Answer C."
            },
            {
                "level": 3,
                "text": "Gauss: 50 pairs ×101=5050 ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-A10-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nCompute $\\frac{1}{1 \\times 2} + \\frac{1}{2 \\times 3} + \\cdots + \\frac{1}{99 \\times 100}$.",
        "options": None,
        "correct_answer": "99/100",
        "difficulty": 4,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-ALG-A10"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Telescoping: 1/(n(n+1))=1/n-1/(n+1)."
            },
            {
                "level": 1,
                "text": "Sum=(1-1/2)+(1/2-1/3)+...+(1/99-1/100)."
            },
            {
                "level": 2,
                "text": "Everything cancels except 1-1/100."
            },
            {
                "level": 3,
                "text": "=99/100."
            },
            {
                "level": 4,
                "text": "Answer: 99/100."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-B4-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nTriangle ABC~DEF with ratio 2:3. Area ABC=20. Area DEF?",
        "options": {
            "A": "30",
            "B": "40",
            "C": "45",
            "D": "60",
            "E": "80"
        },
        "correct_answer": "C",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Linear ratio k → area ratio k²."
            },
            {
                "level": 1,
                "text": "Area ratio=(3/2)²=9/4."
            },
            {
                "level": 2,
                "text": "DEF=20×9/4=45."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "45/20=9/4=(3/2)² ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-B4-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nDE ∥ BC, AD=4, DB=6, BC=15. What is DE?",
        "options": {
            "A": "5",
            "B": "6",
            "C": "7",
            "D": "8",
            "E": "10"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-GEO-B4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "DE∥BC → ADE~ABC (AA)."
            },
            {
                "level": 1,
                "text": "Ratio=4/10=2/5."
            },
            {
                "level": 2,
                "text": "DE=(2/5)×15=6."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "6/15=2/5=4/10 ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-B6-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nCircle radius 6. Area of a $60°$ sector?",
        "options": {
            "A": "4π",
            "B": "6π",
            "C": "8π",
            "D": "12π",
            "E": "36π"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "60°/360°=1/6 of circle."
            },
            {
                "level": 1,
                "text": "36π/6=6π."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "(60/360)×π×36=6π ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-B6-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nPoint P outside circle. Tangent PT=12, radius=5. Find OP.",
        "options": None,
        "correct_answer": "13",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-GEO-B6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Tangent ⊥ radius. Use Pythagoras."
            },
            {
                "level": 1,
                "text": "OT=5, PT=12, OT⊥PT."
            },
            {
                "level": 2,
                "text": "OP²=25+144=169, OP=13."
            },
            {
                "level": 3,
                "text": "5-12-13 triangle ✓."
            },
            {
                "level": 4,
                "text": "Answer: 13."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-B8-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nDistance between $(3,4)$ and $(6,8)$?",
        "options": {
            "A": "3",
            "B": "4",
            "C": "5",
            "D": "7",
            "E": "25"
        },
        "correct_answer": "C",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B8"
        ],
        "hints": [
            {
                "level": 0,
                "text": "d=√((Δx)²+(Δy)²)."
            },
            {
                "level": 1,
                "text": "√(9+16)=√25=5."
            },
            {
                "level": 2,
                "text": "Answer C."
            },
            {
                "level": 3,
                "text": "3-4-5 triangle ✓."
            },
            {
                "level": 4,
                "text": "Answer C."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-B8-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nMidpoint of segment from $(-2,3)$ to $(4,7)$?",
        "options": {
            "A": "(1, 5)",
            "B": "(3, 2)",
            "C": "(2, 5)",
            "D": "(1, 4)",
            "E": "(3, 5)"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-GEO-B8"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Midpoint=((x₁+x₂)/2, (y₁+y₂)/2)."
            },
            {
                "level": 1,
                "text": "((−2+4)/2, (3+7)/2)=(1,5)."
            },
            {
                "level": 2,
                "text": "Answer A."
            },
            {
                "level": 3,
                "text": "Check: equal distances ✓."
            },
            {
                "level": 4,
                "text": "Answer A."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-B9-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nBox $3 \\times 4 \\times 5$. Surface area?",
        "options": {
            "A": "47",
            "B": "60",
            "C": "74",
            "D": "94",
            "E": "120"
        },
        "correct_answer": "D",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B9"
        ],
        "hints": [
            {
                "level": 0,
                "text": "SA=2(ab+bc+ac)."
            },
            {
                "level": 1,
                "text": "2(12+20+15)=2(47)=94."
            },
            {
                "level": 2,
                "text": "Answer D."
            },
            {
                "level": 3,
                "text": "24+40+30=94 ✓."
            },
            {
                "level": 4,
                "text": "Answer D."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-B9-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nVolume of cone with radius 3 and height 4?",
        "options": None,
        "correct_answer": "12π",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-GEO-B9"
        ],
        "hints": [
            {
                "level": 0,
                "text": "V=(1/3)πr²h."
            },
            {
                "level": 1,
                "text": "(1/3)π(9)(4)=12π."
            },
            {
                "level": 2,
                "text": "Answer: 12π."
            },
            {
                "level": 3,
                "text": "Don't forget 1/3! ✓."
            },
            {
                "level": 4,
                "text": "Answer: 12π."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-C3-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nChoose 3 from 10. How many ways?",
        "options": {
            "A": "60",
            "B": "120",
            "C": "210",
            "D": "720",
            "E": "1000"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-CNT-C3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "C(10,3)=10!/(3!×7!)."
            },
            {
                "level": 1,
                "text": "(10×9×8)/(3×2×1)=120."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "Order doesn't matter → combination ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-C3-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nCommittee of 4 from 6 men and 5 women. Exactly 2 women?",
        "options": {
            "A": "120",
            "B": "150",
            "C": "180",
            "D": "200",
            "E": "210"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-CNT-C3"
        ],
        "hints": [
            {
                "level": 0,
                "text": "C(5,2)×C(6,2)."
            },
            {
                "level": 1,
                "text": "10×15=150."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "Multiplication principle with combinations ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-C4-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nCoefficient of $x^3$ in $(x+1)^6$?",
        "options": {
            "A": "15",
            "B": "20",
            "C": "30",
            "D": "10",
            "E": "6"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-CNT-C4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Coefficient=C(6,3)."
            },
            {
                "level": 1,
                "text": "C(6,3)=20."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "6!/(3!3!)=20 ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-C4-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nSum of all coefficients in $(x+y)^5$?",
        "options": None,
        "correct_answer": "32",
        "difficulty": 3,
        "estimated_time_sec": 45,
        "knowledge_point_codes": [
            "AMC-CNT-C4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Set x=1, y=1."
            },
            {
                "level": 1,
                "text": "(1+1)⁵=2⁵=32."
            },
            {
                "level": 2,
                "text": "Answer: 32."
            },
            {
                "level": 3,
                "text": "Sum of coefficients = f(1,1) ✓."
            },
            {
                "level": 4,
                "text": "Answer: 32."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-C6-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nHow many 3-digit numbers do NOT end in 0 or 5?",
        "options": {
            "A": "720",
            "B": "800",
            "C": "810",
            "D": "648",
            "E": "900"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-CNT-C6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "9 hundreds × 10 tens × 8 last digits (not 0,5)."
            },
            {
                "level": 1,
                "text": "9×10×8=720."
            },
            {
                "level": 2,
                "text": "Answer A."
            },
            {
                "level": 3,
                "text": "Or: complement from 900. Multiples of 5: 180. 900-180=720 ✓."
            },
            {
                "level": 4,
                "text": "Answer A."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-C6-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\n4-digit password (0-9), no digit 0. How many?",
        "options": {
            "A": "6561",
            "B": "9000",
            "C": "9456",
            "D": "9999",
            "E": "5040"
        },
        "correct_answer": "A",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-CNT-C6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Each digit 1-9: 9 choices per position."
            },
            {
                "level": 1,
                "text": "9⁴=6561."
            },
            {
                "level": 2,
                "text": "Answer A."
            },
            {
                "level": 3,
                "text": "Direct counting is simpler ✓."
            },
            {
                "level": 4,
                "text": "Answer A."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-C7-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nIn a class of 30: 20 take math, 18 take science. How many take both?",
        "options": {
            "A": "6",
            "B": "7",
            "C": "8",
            "D": "9",
            "E": "10"
        },
        "correct_answer": "C",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-CNT-C7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "|A∪B|=|A|+|B|-|A∩B|."
            },
            {
                "level": 1,
                "text": "30=20+18-|A∩B|."
            },
            {
                "level": 2,
                "text": "|A∩B|=38-30=8."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "8 take both ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-C7-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\n1-100: divisible by 3 or 5?",
        "options": {
            "A": "43",
            "B": "45",
            "C": "47",
            "D": "53",
            "E": "50"
        },
        "correct_answer": "C",
        "difficulty": 3,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-CNT-C7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "|A|+|B|-|A∩B|."
            },
            {
                "level": 1,
                "text": "⌊100/3⌋=33, ⌊100/5⌋=20, ⌊100/15⌋=6."
            },
            {
                "level": 2,
                "text": "33+20-6=47."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "Inclusion-exclusion ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-C8-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nIf $F_1=1, F_2=1, F_n=F_{n-1}+F_{n-2}$, what is $F_7$?",
        "options": {
            "A": "8",
            "B": "13",
            "C": "21",
            "D": "34",
            "E": "3"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-CNT-C8"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Compute step by step."
            },
            {
                "level": 1,
                "text": "F3=2, F4=3, F5=5, F6=8, F7=13."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "Fibonacci sequence ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-C8-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nA staircase has $n$ steps. You climb 1 or 2 steps at a time. Let $a_n$ be the number of ways. If $a_1=1, a_2=2$, find $a_6$.",
        "options": None,
        "correct_answer": "13",
        "difficulty": 4,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-CNT-C8"
        ],
        "hints": [
            {
                "level": 0,
                "text": "a_n = a_{n-1} + a_{n-2} (Fibonacci recurrence)."
            },
            {
                "level": 1,
                "text": "a1=1, a2=2, a3=3, a4=5, a5=8, a6=13."
            },
            {
                "level": 2,
                "text": "Answer: 13."
            },
            {
                "level": 3,
                "text": "This is Fibonacci shifted by 1 ✓."
            },
            {
                "level": 4,
                "text": "Answer: 13."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-C9-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nA die pays $\\$3$ for even, $\\$0$ for odd. What is the expected value?",
        "options": {
            "A": "$\\$0.50$",
            "B": "$\\$1.00$",
            "C": "$\\$1.50$",
            "D": "$\\$2.00$",
            "E": "$\\$3.00$"
        },
        "correct_answer": "C",
        "difficulty": 4,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-CNT-C9"
        ],
        "hints": [
            {
                "level": 0,
                "text": "E[X]=Σ x·P(x)."
            },
            {
                "level": 1,
                "text": "P(even)=1/2, P(odd)=1/2."
            },
            {
                "level": 2,
                "text": "E=3·(1/2)+0·(1/2)=1.5."
            },
            {
                "level": 3,
                "text": "Answer C."
            },
            {
                "level": 4,
                "text": "E[X]=$1.50 ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-C9-02",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nFlip 3 coins. You get $\\$1$ per head. Expected earnings?",
        "options": {
            "A": "$\\$1.00$",
            "B": "$\\$1.50$",
            "C": "$\\$2.00$",
            "D": "$\\$3.00$",
            "E": "$\\$0.50$"
        },
        "correct_answer": "B",
        "difficulty": 4,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-CNT-C9"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Each coin: E[heads]=0.5. By linearity, E[total]=3×0.5=1.5."
            },
            {
                "level": 1,
                "text": "Earnings=$1.50."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "Linearity of expectation ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-D4-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is the remainder when $2^{10}$ is divided by 7?",
        "options": {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4",
            "E": "5"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-NT-D4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Compute 2^10 mod 7."
            },
            {
                "level": 1,
                "text": "2³=8≡1 (mod 7). So 2^10=(2³)³×2≡1×2=2 (mod 7)."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "2^10=1024, 1024/7=146R2 ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-D4-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nFind the smallest positive $x$ such that $x \\equiv 2 \\pmod{3}$ and $x \\equiv 1 \\pmod{5}$.",
        "options": None,
        "correct_answer": "11",
        "difficulty": 3,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-NT-D4"
        ],
        "hints": [
            {
                "level": 0,
                "text": "x=3k+2 for some k. Check mod 5: 3k+2≡1 (mod 5) → 3k≡4 (mod 5)."
            },
            {
                "level": 1,
                "text": "3k≡4 (mod 5) → k≡3 (mod 5) since 3×3=9≡4."
            },
            {
                "level": 2,
                "text": "k=3: x=3(3)+2=11."
            },
            {
                "level": 3,
                "text": "Check: 11≡2 (mod 3) ✓, 11≡1 (mod 5) ✓."
            },
            {
                "level": 4,
                "text": "Answer: 11."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-D5-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nWhat is $10110_2$ in base 10?",
        "options": {
            "A": "20",
            "B": "22",
            "C": "26",
            "D": "30",
            "E": "46"
        },
        "correct_answer": "B",
        "difficulty": 3,
        "estimated_time_sec": 60,
        "knowledge_point_codes": [
            "AMC-NT-D5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Expand in powers of 2."
            },
            {
                "level": 1,
                "text": "1·2⁴+0·2³+1·2²+1·2¹+0·2⁰=16+4+2=22."
            },
            {
                "level": 2,
                "text": "Answer B."
            },
            {
                "level": 3,
                "text": "Binary 10110 = decimal 22 ✓."
            },
            {
                "level": 4,
                "text": "Answer B."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-D5-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nConvert $45_{10}$ to binary.",
        "options": None,
        "correct_answer": "101101",
        "difficulty": 3,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-NT-D5"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Divide by 2 repeatedly, collect remainders."
            },
            {
                "level": 1,
                "text": "45→22R1, 22→11R0, 11→5R1, 5→2R1, 2→1R0, 1→0R1."
            },
            {
                "level": 2,
                "text": "Read bottom-up: 101101."
            },
            {
                "level": 3,
                "text": "Check: 32+8+4+1=45 ✓."
            },
            {
                "level": 4,
                "text": "Answer: 101101."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-D6-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nHow many non-negative integer solutions does $2x+3y=12$ have?",
        "options": {
            "A": "2",
            "B": "3",
            "C": "4",
            "D": "5",
            "E": "6"
        },
        "correct_answer": "B",
        "difficulty": 4,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-NT-D6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "gcd(2,3)=1 divides 12, so solutions exist."
            },
            {
                "level": 1,
                "text": "x=(12-3y)/2. Need 12-3y even and ≥0."
            },
            {
                "level": 2,
                "text": "y=0→x=6, y=2→x=3, y=4→x=0. Three solutions."
            },
            {
                "level": 3,
                "text": "Answer B."
            },
            {
                "level": 4,
                "text": "(6,0),(3,2),(0,4) ✓."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-D6-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nFind all non-negative integer solutions of $3x+5y=30$.",
        "options": None,
        "correct_answer": "(10,0),(5,3),(0,6)",
        "difficulty": 4,
        "estimated_time_sec": 150,
        "knowledge_point_codes": [
            "AMC-NT-D6"
        ],
        "hints": [
            {
                "level": 0,
                "text": "x=(30-5y)/3. Need 30-5y divisible by 3 and ≥0."
            },
            {
                "level": 1,
                "text": "30-5y≡0 (mod 3) → y≡0 (mod 3). y=0,3,6."
            },
            {
                "level": 2,
                "text": "y=0→x=10, y=3→x=5, y=6→x=0."
            },
            {
                "level": 3,
                "text": "Three solutions."
            },
            {
                "level": 4,
                "text": "Answer: (10,0),(5,3),(0,6)."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2024,
        "source_code": "AMC10-2024-D7-01",
        "subject": "amc_math",
        "format": "mcq",
        "question_markdown": "## Problem\n\nUsing Fermat's Little Theorem, what is $3^{12} \\pmod{13}$?",
        "options": {
            "A": "1",
            "B": "3",
            "C": "9",
            "D": "12",
            "E": "0"
        },
        "correct_answer": "A",
        "difficulty": 4,
        "estimated_time_sec": 120,
        "knowledge_point_codes": [
            "AMC-NT-D7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "Fermat: a^(p-1)≡1 (mod p) when gcd(a,p)=1."
            },
            {
                "level": 1,
                "text": "13 is prime, gcd(3,13)=1, so 3^12≡1 (mod 13)."
            },
            {
                "level": 2,
                "text": "Answer A."
            },
            {
                "level": 3,
                "text": "3^12 mod 13 = 1 ✓."
            },
            {
                "level": 4,
                "text": "Answer A."
            }
        ]
    },
    {
        "source": "AMC10",
        "source_year": 2023,
        "source_code": "AMC10-2023-D7-02",
        "subject": "amc_math",
        "format": "fill_blank",
        "question_markdown": "## Problem\n\nCompute $\\phi(12)$ (Euler's totient).",
        "options": None,
        "correct_answer": "4",
        "difficulty": 4,
        "estimated_time_sec": 90,
        "knowledge_point_codes": [
            "AMC-NT-D7"
        ],
        "hints": [
            {
                "level": 0,
                "text": "φ(n)=n∏(1-1/p) for prime factors p of n."
            },
            {
                "level": 1,
                "text": "12=2²×3. φ(12)=12×(1-1/2)×(1-1/3)."
            },
            {
                "level": 2,
                "text": "=12×(1/2)×(2/3)=4."
            },
            {
                "level": 3,
                "text": "Numbers coprime to 12: {1,5,7,11} → 4 ✓."
            },
            {
                "level": 4,
                "text": "Answer: 4."
            }
        ]
    }
]
