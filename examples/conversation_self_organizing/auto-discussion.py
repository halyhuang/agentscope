# -*- coding: utf-8 -*-
"""A simple example for auto discussion: the agent builder automatically\
 set up the agents participating the discussion ."""
from tools import load_txt, extract_scenario_and_participants
import agentscope
from agentscope.agents import DialogAgent
from agentscope.pipelines.functional import sequentialpipeline
from agentscope.message import Msg
import os

model_configs = [
    {
        "model_type": "dashscope_chat",
        "config_name": "dash",
        "model_name": "qwen-turbo",
        "api_key": os.environ.get("DASHSCOPE_API_KEY", "sk-a2eb345c7f514044b7f4a9053d228467"),
        "organization": "noodle-ai",  # Load from env if not provided
        "generate_args": {
            "temperature": 0.5,
        },
    },
    {
        "model_type": "dashscope_chat",
        "config_name": "my_post_api",
        "model_name": "qwen-turbo",
        "api_key": os.environ.get("DASHSCOPE_API_KEY", "sk-a2eb345c7f514044b7f4a9053d228467"),
        "headers": {},
        "json_args": {},
    },
]

agentscope.init(
    model_configs=model_configs,
    project="Self-Organizing Conversation",
)


# init the self-organizing conversation
agent_builder = DialogAgent(
    name="agent_builder",
    sys_prompt="You're a helpful assistant.",
    model_config_name="my_post_api",
)


max_round = 2
query = "Say the pupil of your eye has a diameter of 5 mm and you have a \
telescope with an aperture of 50 cm. How much more light can the \
telescope gather than your eye?"

# get the discussion scenario and participant agents
x = load_txt(
    "examples/conversation_self_organizing/agent_builder_instruct.txt",
).format(
    question=query,
)

x = Msg("user", x, role="user")
settings = agent_builder(x)
scenario_participants = extract_scenario_and_participants(settings.content)

# set the agents that participant the discussion
agents = [
    DialogAgent(
        name=key,
        sys_prompt=val,
        model_config_name="my_post_api",
    )
    for key, val in scenario_participants["Participants"].items()
]

# begin discussion
msg = Msg("user", f"let's discuss to solve the question: {query}", role="user")
for i in range(max_round):
    msg = sequentialpipeline(agents, msg)
