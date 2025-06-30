from agents import Runner, Agent, OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled, function_tool
import os
from dotenv import load_dotenv
import chainlit as cl
import random
from openai.types.responses import ResponseTextDeltaEvent

# Load .env variables
load_dotenv()
set_tracing_disabled(disabled=True)

# API Key from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")

provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Gemini Model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

# --- TOOL FUNCTIONS ---
@function_tool
def get_random_dua() -> str:
    duas = [
        "اللّهُـمَّ أَجِرْنِي مِنَ النّارِ\nO Allah, protect me from the Hellfire.",
        "اللهم إني أعوذ بك من الهم والحزن\nO Allah, I seek refuge in You from anxiety and grief.",
        "ربنا آتنا في الدنيا حسنة وفي الآخرة حسنة وقنا عذاب النار"
    ]
    return random.choice(duas)

@function_tool
def get_motivational_quote() -> str:
    quotes = [
        "Indeed, with hardship comes ease – Quran 94:6",
        "Don’t lose hope, Allah’s mercy is near – Quran 11:9",
        "You are stronger than you think. Keep going!",
        "Every test is a blessing in disguise. Trust Allah."
    ]
    return random.choice(quotes)

@function_tool
def suggest_self_care_tip() -> str:
    tips = [
        "Take a moment to make dua and reflect silently.",
        "Go for a peaceful walk and do some dhikr.",
        "Drink water, rest, and breathe deeply with focus.",
        "Write down 3 things you're grateful for today."
    ]
    return random.choice(tips)

@function_tool
def suggest_quran_ayah() -> str:
    ayahs = [
        "So verily, with the hardship, there is relief – Surah Al-Inshirah 94:6",
        "And He found you lost and guided [you] – Surah Ad-Duhaa 93:7",
        "Indeed, Allah is with the patient – Surah Al-Baqarah 2:153"
    ]
    return random.choice(ayahs)

@function_tool
def offer_gratitude_prompt() -> str:
    prompts = [
        "List three things you are thankful for today.",
        "What is something small that made you smile recently?",
        "Think of one person who helped you this week – send a prayer for them."
    ]
    return random.choice(prompts)

# Agent definition
agent = Agent(
    name="Mental Health Supporter Agent",
    instructions="""
You are a gentle Islamic support agent who replies to mental health-related concerns.
1. Respond with empathy
2. Include an Islamic dua or Quranic ayah with translation
3. End with a motivational quote or tip
You may call tools like get_random_dua, get_motivational_quote, suggest_self_care_tip,
suggest_quran_ayah, offer_gratitude_prompt when appropriate.
""",
    model=model
)



@cl.on_chat_start
async def handle_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Assalamu Alaikum! How can I help you today?").send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()

    result =Runner.run_streamed(
        agent,
        input=history,
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and hasattr(event.data, "delta"):
            await msg.stream_token(event.data.delta)

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)