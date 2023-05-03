from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback
from langchain.llms import OpenAI
import os
import streamlit as st

os.environ['OPENAI_API_KEY'] = st.secrets['open_api_key']
os.environ['PINECONE_API_KEY'] = st.secrets['pinecone_api_key']

# Dummy character sheet data. Will replace with read from character sheet later.
character_sheet = {
    "name": "Nashira",
    "class_type": "Warlock",
    "subclass": "Great Old One",
    "race": "High Elf",
    "background": "Sage",
    "level": 6,
    "strength modifier": -1,
    "dexterity modifier": 4,
    "constitution modifier": 2,
    "intelligence modifier": 3,
    "wisdom modifier": 0,
    "charisma modifier": 4,
    "skills": {
        "Acrobatics": 4,
        "Animal Handling": 0,
        "Arcana": 5,
        "Athletics": -1,
        "Deception": -1,
        "History": 5,
        "Insight": 0,
        "Intimidation": -1,
        "Investigation": 5,
        "Medicine": 0,
        "Nature": 3,
        "Perception": 2,
        "Performance": -1,
        "Persuasion": -1,
        "Religion": 3,
        "Sleight of Hand": 4,
        "Stealth": 6,
        "Survival": 0,
    },
    "weapon": ["Long Bow"],
    "armor_class": 20,
    "proficiency bonus": 3,
}


player_query = "What's my atheltics"

# Prompt Setup
type_of_question_prompt = PromptTemplate(input_variables=['player_query'],
                                         template="""
You are a Dungeons and Dragons 5th Edition dungeon master. Your job is the decide what type of question the player query, {player_query}, is.
Your choices are: attack, skills, saving throw, spellcasting, or general rules. Your answer should only be one of these words and nothing else.
                                              """)

stats_needed_template = PromptTemplate(input_variables=['question_type'],
                                        template="""You are a Dungeons and Dragons 5th Edition dungeon master. Your job is the select which stats are needed to answer a about a/an {question_type} based question. You may select from the following list of stats: strength modifier, dexterity modifier, constitution modifier, intelligence modifier, wisdom modifier, charisma modifier, proficiency bonus, armor class, weapon
                                        You may select only the stats required to resolve the roll in the most optimal way. You must select at least one. Your answer should be a comma separated list of stats.
                                        """
)

what_to_roll_template = PromptTemplate(input_variables=['player_query','stats_needed_string'],
                                        template="""You are a Dungeons and Dragons 5th Edition dungeon master. Your job is to, as concisely as possible, tell the player what to roll to answer the following query, "{player_query}". You have been given the following stats from their character sheet: {stats_needed_string}. Include enough information to resolve all parts of the query as applicable such as attack bonus, damage, saving throw, special effects, etc. Always use the ability modifier that results in the highest damage. For example, finesse and ranged weapons should use dexterity. If the question is about a spell, return the exact dungeons and dragons 5th edition spell description and no dice or modifiers. Attack rolls always use a d20.
                                        """
)

# LLM Setup
type_of_question_llm = OpenAI(temperature=0.2, max_tokens=150)
stats_needed_llm = OpenAI(temperature=0.2, max_tokens=150)
what_to_roll_llm = OpenAI(temperature=.2, max_tokens=300)
# what_to_roll_llm = OpenAI(top_p=0.8, max_tokens=300)


# Chain setup
type_of_question_chain = LLMChain(llm=type_of_question_llm,
                                  verbose=True,
                                  prompt=type_of_question_prompt,
                                  output_key='type_of_question', )

stats_need_chain = LLMChain(llm=stats_needed_llm,
                            verbose=True,
                            prompt=stats_needed_template,
                            output_key='stats_needed',)

what_to_roll_chain = LLMChain(llm=what_to_roll_llm,
                            verbose=True,
                            prompt=what_to_roll_template,
                            output_key='what_to_roll',)

with get_openai_callback() as cb:
    question_type = (type_of_question_chain.run(player_query)).lower().split()[
        0]  # can't figure out why but there's an extra character without splitting
    if question_type == 'attack':
        stats_need = 'weapon, proficiency bonus, dexterity modifier, strength modifier, armor class'

    elif question_type == 'skills':
        stats_needed = 'skills'

    elif question_type == 'spellcasting':
    #     if character_sheet['class_type'] in ['warlock', 'sorcerer', 'bard','paladin']:
    #         casting_stat = 'charisma modifier'
    #     elif character_sheet['class_type'] in ['wizard'] or character_sheet['subclass'] in ['arcane trickster', 'eldritch knight']:
    #         casting_stat = 'intelligence modifier'
    #     elif character_sheet['class_type'] in ['cleric', 'druid', 'ranger']:
    #         casting_stat = 'wisdom modifier'
    #     else:
    #         casting_stat = 'intelligence modifier, wisdom modifier, charisma modifier'
    #     stats_needed = f'level, proficiency bonus, {casting_stat}'
    # else:
    #     stats_needed = stats_need_chain.run(question_type)
        stats_needed = ''

    # stats_needed cleanup and formatting
    stats_needed_list = stats_needed.lower().replace('\n', '').split(', ')
    stats_needed_string = f'class: {character_sheet["class_type"]}\n'
    if stats_needed=='':
        pass
    else:
        for stat in stats_needed_list:
            if stat == 'class':
                stat = 'class_type'

        stats_needed_string += f"{stat}: {character_sheet[stat]}\n"

    what_to_roll = what_to_roll_chain.run(player_query=player_query, stats_needed_string=stats_needed_string)

print(question_type)
print(stats_needed_string)
print(what_to_roll)
print(cb)
