from langchain_anthropic import ChatAnthropic
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI

OPENAI_MODEL_KEY = "openai_gpt_4o_mini"
GPT_4O_MODEL_KEY = "openai_gpt_4o"
ANTHROPIC_MODEL_KEY = "anthropic_claude_3_haiku"
CLAUDE_35_SONNET_MODEL_KEY = "anthropic_claude_3_5_sonnet"

gpt_4o_mini = ChatOpenAI(model="gpt-4o-mini", temperature=0)
gpt_4o_mini2 = ChatOpenAI(model="gpt-4o-mini")

claude_3_haiku = ChatAnthropic(
    model="claude-3-haiku-20240307",
)


gpt_4o = ChatOpenAI(
    model="gpt-4o-2024-08-06",
)
claude_35_sonnet = ChatAnthropic(
    model="claude-3-5-sonnet-20240620",
)

llm = gpt_4o_mini.configurable_alternatives(
    ConfigurableField(id="llm"),
    default_key=OPENAI_MODEL_KEY,
    **{
        ANTHROPIC_MODEL_KEY: claude_3_haiku,
        GPT_4O_MODEL_KEY: gpt_4o,
        CLAUDE_35_SONNET_MODEL_KEY: claude_35_sonnet,
    },
)
