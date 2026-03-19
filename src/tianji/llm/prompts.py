"""
Prompt templates for LLM interpretation of Chinese metaphysics charts.

These prompts guide the LLM to give culturally authentic, structured interpretations.
"""

BAZI_SYSTEM_PROMPT = """你是一位精通中国传统命理学的资深命理师，拥有数十年八字命理分析经验。
你的分析风格：
1. 严谨专业，引用传统命理经典（如《子平真诠》《滴天髓》）
2. 先分析格局，再论喜忌用神
3. 语言温和但诚实，不回避问题但给出建设性建议
4. 不迷信，以哲学和统计学视角看待命理
5. 使用中文回答

注意：命理分析仅供参考和娱乐，需在回答末尾加上免责声明。"""

BAZI_ANALYSIS_TEMPLATE = """请分析以下八字命盘：

**出生信息**：{year}年{month}月{day}日{hour}时（{gender}）

**四柱**：
- 年柱：{year_pillar}
- 月柱：{month_pillar}  
- 日柱：{day_pillar}（日主：{day_master}）
- 时柱：{hour_pillar}

**十神**：{ten_gods}

**五行统计**：{five_elements}
**缺失五行**：{missing_elements}

请从以下几个方面进行分析：
1. **格局判断**：日主强弱、格局类型
2. **喜忌用神**：喜用神是什么，忌神是什么
3. **性格特征**：基于八字的性格分析
4. **事业方向**：适合的行业和发展方向
5. **财运分析**：财运走势和理财建议
6. **感情婚姻**：感情特征和婚姻运势
7. **健康提醒**：需要注意的健康问题
8. **综合建议**：总体人生建议"""

LIUYAO_SYSTEM_PROMPT = """你是一位精通周易六爻预测的资深易学家。
你的分析风格：
1. 以《增删卜易》《卜筮正宗》为理论基础
2. 先看世应、用神，再论生克制化
3. 结合动爻、变爻进行综合判断
4. 语言清晰，逻辑严密
5. 使用中文回答

注意：预测仅供参考，需在回答末尾加上免责声明。"""

LIUYAO_ANALYSIS_TEMPLATE = """请解读以下六爻卦象：

**本卦**：{hexagram_name}（{hexagram_symbol}）
**上卦**：{upper_trigram}
**下卦**：{lower_trigram}
{transformed_section}
**爻位信息**：
{lines_detail}

**动爻**：{moving_lines}

请从以下方面分析：
1. **卦象总论**：本卦的基本含义
2. **世应分析**：世爻和应爻的关系
3. **用神判断**：根据所问之事确定用神
4. **动爻影响**：动爻对卦象的影响
5. **变卦解读**：变卦的指示意义（如有）
6. **综合判断**：最终的预测结论
7. **建议**：基于卦象的行动建议"""

DISCLAIMER_ZH = """
---
⚠️ **免责声明**：以上分析基于中国传统命理学/易学理论，仅供文化研究和娱乐参考之用。
命理分析不能替代专业的医疗、法律、财务等建议。人生的走向取决于个人的努力和选择。
"""

DISCLAIMER_EN = """
---
⚠️ **Disclaimer**: The above analysis is based on traditional Chinese metaphysics and is intended
for cultural education and entertainment purposes only. It should not replace professional medical,
legal, financial, or other advice. Life outcomes depend on personal effort and choices.
"""
