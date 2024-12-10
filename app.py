import gradio as gr
from datetime import datetime
import openai

# OpenAI API key
openai.api_key = "your_openai_key"

# 六神数组
liu_shen = ["大安", "留连", "速喜", "赤口", "小吉", "空亡"]

# 六神释义
liu_shen_texts = {
        "大安": "身不动时，五行属木，颜色青色，方位东方。临青龙，谋事主一、五、七。有静止、心安。吉祥之含义。诀曰：大安事事昌，求谋在东方，失物去不远。宅舍保平安，行人身未动，病者主无妨，将军回田野，仔细更推详。",
        "留连": "人未归时，五行属水，颜色黑色，方位北方，临玄武，凡谋事主二、入、十。有喑味不明，延迟。纠缠．拖延、漫长之含义。 诀曰：留连事难成，求谋日未明，官事只宜缓。去者来回程，失物南方见，急讨方遂心。更需防口舌，人事且平平。",
        "速喜": "人即至时，五行属火，颜色红色方位南方，临朱雀，谋事主三，六，九。有快速、喜庆，吉利之含义。指时机已到。诀曰：速喜喜来临，求财向南行，失物申未午(南或西南)逢人路上寻，官事有福德，病者无祸侵,田宅六畜吉，行人有音信。",
        "赤口": "官事凶时，五行属金，颜色白色，方位西方，临白虎，谋事主四、七，十。有不吉、惊恐，凶险、 口舌是非之含义。诀曰：赤口主口舌，官非切要防，失物急去寻行人有惊慌，鸡犬多作怪，病者出西方更须防咀咒，恐怕染瘟殃。",
        "小吉": "人来喜时，五行属木，临六合，凡谋事主一、五、七有和合、吉利之含义。诀曰：小吉最吉昌，路上好商量，阴人来报喜。失物在坤方(西南)，行人立便至，交易甚是强凡事皆和合，病者祈上苍。",
        "空亡": "音信稀时，五行属土，颜色黄色，方位中央；临勾陈。谋事主三、六、九。 有不吉、无结果、忧虑之含义。诀曰：空亡事不禅，阴人多乖张，求财无利益。行人有灾殃，失物寻不见，官事有刑伤病人逢暗鬼，析解可安康。"
    }

# 计算卦象
def calculate_divination(num1, num2, num3):
    index1 = (num1 - 1) % 6
    index2 = (num1 + num2 - 2) % 6
    index3 = (num1 + num2 + num3 - 3) % 6
    return liu_shen[index1], liu_shen[index2], liu_shen[index3]

# AI 解释卦象
def generate_ai_interpretation(question, divination):
    if not openai.api_key:
        return "OpenAI API key 不正确"
    
    prompt = (
        f"我问的问题是：'{question}'\n"
        f"卦象结果是：{divination[0]}，{divination[1]}，{divination[2]}。\n"
        f"每个卦象的基本释义如下：\n"
        f"- {divination[0]}: {liu_shen_texts[divination[0]]}\n"
        f"- {divination[1]}: {liu_shen_texts[divination[1]]}\n"
        f"- {divination[2]}: {liu_shen_texts[divination[2]]}\n\n"
        "请根据以上卦象和我的问题，提供一个详细的解释，分析可能的结果以及需要注意的地方。"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI 分析失败，可能调用次数达到limit，请稍后重试。错误信息：{e}"

# 起卦方法
def divination(method, use_ai, question="", num1=None, num2=None, num3=None):
    if method == "当前时辰起卦":
        now = datetime.now()
        num1 = now.hour
        num2 = now.minute // 10
        num3 = now.minute % 10
    elif method == "手动输入":
        if not all([num1, num2, num3]):
            return "请输入三个有效数字。", None, None, None

    divination_result = calculate_divination(num1, num2, num3)
    explanations = [liu_shen_texts[god] for god in divination_result]
    
    result = (
        f"卦象：{divination_result[0]} {divination_result[1]} {divination_result[2]}\n\n"
        f"解释：\n"
        f"{divination_result[0]}：{explanations[0]}\n"
        f"{divination_result[1]}：{explanations[1]}\n"
        f"{divination_result[2]}：{explanations[2]}"
    )
    ai_interpretation = None
    if use_ai:
        if not question.strip():
            return "请输入问题以启用 AI 分析。", result, None
        ai_interpretation = generate_ai_interpretation(question, divination_result)
    
    return result, ai_interpretation

# 构建 Gradio 界面
def gradio_ui():
    css = """
    <style>
        #header {text-align: center; color: #2c3e50; margin-bottom: 20px;}
        #num-input {margin-right: 10px;}
        #ai-checkbox {margin-top: 20px;}
        #question-input {margin-top: 10px;}
        #result-output {border: 2px solid #3498db; border-radius: 8px; padding: 10px;}
        #ai-output {border: 2px dashed #2ecc71; border-radius: 8px; padding: 10px;}
        #footer {margin-top: 40px; font-size: 0.9em; color: #7f8c8d;}
    </style>
    """
    
    with gr.Blocks() as interface:
        gr.HTML(css)  # 插入自定义 CSS
        gr.Markdown(
            """
            # 🌟 小六壬预测系统 🌟
            欢迎使用小六壬预测系统！心中默想所问之事，然后选择起卦方式并输入相关信息。<br>
            👉 使用传统占卜方法，结合现代 AI 技术（可选），为您提供详细解读！
            """, 
            elem_id="header"
        )

        with gr.Row():
            method = gr.Radio(
                ["当前时辰起卦", "手动输入"], 
                label="选择起卦方式", 
                value="当前时辰起卦",
                interactive=True
            )
            with gr.Column(visible=False) as manual_inputs:
                num1 = gr.Number(label="请随机输入第一个0-99之间的数字", precision=0, elem_id="num-input")
                num2 = gr.Number(label="请随机输入第二个0-99之间的数字", precision=0, elem_id="num-input")
                num3 = gr.Number(label="请随机输入第三个0-99之间的数字", precision=0, elem_id="num-input")

        def toggle_manual(method):
            return gr.update(visible=(method == "手动输入"))

        method.change(toggle_manual, method, manual_inputs)

        use_ai = gr.Checkbox(label="启用 AI 分析", value=False, elem_id="ai-checkbox")
        question = gr.Textbox(
            label="输入您的问题（仅在启用 AI 分析时填写）", 
            visible=False, 
            placeholder="例如：我的事业是否顺利？",
            elem_id="question-input"
        )
        
        def toggle_ai(use_ai):
            return gr.update(visible=use_ai)

        use_ai.change(toggle_ai, use_ai, question)

        result = gr.Textbox(label="📜 起卦结果", interactive=False, elem_id="result-output")
        ai_interpretation = gr.Textbox(label="🤖 AI 智能分析（可选）", interactive=False, elem_id="ai-output")

        def predict(method, use_ai, question, num1=None, num2=None, num3=None):
            return divination(method, use_ai, question, num1, num2, num3)

        gr.Button("✨ 起卦", elem_id="predict-button").click(
            predict,
            inputs=[method, use_ai, question, num1, num2, num3],
            outputs=[result, ai_interpretation]
        )
        
        gr.Markdown(
            """
            ## 六神释义 🌸
            - **大安**：万事大吉，身心安泰，所求皆如意。
            - **留连**：事多阻滞，凡事宜缓不宜急。
            - **速喜**：喜事临门，吉祥如意，吉庆可期。
            - **赤口**：口舌是非，谨慎言行，避免争执。
            - **小吉**：平安顺遂，虽无大利，亦无大害。
            - **空亡**：事难成就，凡事宜守不宜进。
            """, 
            elem_id="footer"
        )

    return interface

if __name__ == "__main__":
    gradio_ui().launch()
