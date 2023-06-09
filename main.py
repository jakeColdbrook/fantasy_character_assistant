from langchain.llms import OpenAI
import os
import streamlit as st
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory

os.environ['OPENAI_API_KEY'] = st.secrets['open_api_key']
os.environ['PINECONE_API_KEY'] = st.secrets['pinecone_api_key']


def character_inputs():
    # LLM Stuff
    character_summary_template = PromptTemplate(
        input_variables=['character_name', 'race', 'class_type', 'alignment', 'general_information', 'appearance',
                         'personality'],
        template="""You are a fantasy writer and a famous fantasy novelists. Your job is to take the following traits and inputs given to you by a fan and write them an amazing and embellished 2 paragraph character summary. Their writing is bland and amatuer, but you are a professional. As such, your version will reuse as little words as possible while still staying true to the character. Write your version in the style of Brandon Sanderson:
                Name: {character_name}
                Race: {race}
                Class: {class_type}
                Alignment: {alignment}
                General Information: {general_information}
                Appearance: {appearance}
                Personality: {personality}
                """)

    llm = OpenAI(temperature=0.8, max_tokens=2000)
    character_summary_chain = LLMChain(llm=llm,
                                       prompt=character_summary_template,
                                       verbose=True,
                                       output_key='character_summary', )

    # Create the options
    race_options = ['Human', 'Elf', 'Dwarf', 'Half-elf', 'Half-orc', 'Halfling', 'Other']
    class_options = ['Fighter', 'Wizard', 'Cleric', 'Ranger', 'Rogue', 'Monk', 'Warlock', 'Sorcerer', 'Bard',
                     'Barbarian']
    alignment_options = ['Lawful Good', 'Lawful Neutral', 'Lawful Evil', 'Neutral Good', 'True Neutral', 'Neutral Evil',
                         'Chaotic Good', 'Chaotic Neutral', 'Chaotic Evil']

    # Create the placeholders
    general_information_placeholder = """You are a cleric of the Queen of Cinders. You come from a barbarian tribe, wear heavy armor, and wield a warhammer."""
    appearance_placeholder = """You are tall and blond with a half shaven head with the shaven half covered in tribal tattoos. You have a long braided beard and a scar across your left eye. You wear heavy armor and wield a warhammer. Your armor is always lightly smoldering, and your cape always lightly blowing in the wind. You also have a large shield with tribal and holy symbols on it."""
    personality_placeholder = """You usually find yourself fighting in the front-lines with the warriors, but your specialty is lightning and fire focused spells. Your name is "Obsidian Ash", and you always change the story when asked how you earned your name.  You despise healing magic and will only use it as a last resort to bring a ally back from the brink of dead. Your healing spells take on a unique style of healing that burns the wounds and often leaves a scar. Your magic is inspired by fire, storms, and nature. All spells should be described in a manner consistent with the spell name while including the flavor of fire, lava, and thunder. You often make reference to your goddess, often called "The Empress of Cinders" or "The Queen of Ash", but you realize that your allies do not worship her.  You speak with few words, but always with purpose and meaning, the only exception is when telling legends, which always take on a epic and dark tone. You have a very direct way of speaking, and you never use contractions. For example, "I'm" would always be "I am."""

    # Create the inputs
    character_name = st.text_input("Character Name", "Obsidian Ash")
    race = st.selectbox("Race", race_options, index=0)
    class_type = st.selectbox("Class", class_options, index=2)
    alignment = st.selectbox("Alignment", alignment_options, index=6)
    general_information = st.text_area("General Information", general_information_placeholder, height=200)
    appearance = st.text_area("Appearance", value=appearance_placeholder, height=200, )
    personality = st.text_area("Personality", value=personality_placeholder, height=400, )

    # Create the save button
    save_button = st.button("Save Character Information")

    # Save the inputs if the button is clicked
    if save_button:
        st.session_state.character_name = character_name
        st.session_state.race = race
        st.session_state.class_type = class_type
        st.session_state.alignment = alignment
        st.session_state.general_information = general_information
        st.session_state.appearance = appearance
        st.session_state.personality = personality
        st.write("Character information saved.")
        character_summary = character_summary_chain.run(character_name=character_name, race=race, class_type=class_type,
                                                        alignment=alignment,
                                                        general_information=general_information, appearance=appearance,
                                                        personality=personality)
        st.write(character_summary)
        st.session_state.character_summary = character_summary


# Create a function to display the outputs
def script_generator():
    if st.session_state.character_summary ==None:
        st.write('Please return to the character inputs page and click the "Save Character Information" button')
    # Get the saved inputs
    character_name = st.session_state.character_name
    # race = st.session_state.race
    # class_type = st.session_state.class_type
    # alignment = st.session_state.alignment
    # general_information = st.session_state.general_information
    # appearance = st.session_state.appearance
    # personality = st.session_state.personality
    character_summary = st.session_state.character_summary

    # Display the outputs
    if character_name:
        st.write(f"{character_name}-GPT Roleplaying Assistant")
        action_prompt = st.text_input('Enter a prompt',
                                      placeholder="You're surrounded by goblins. How do you break through them?")
    else:
        st.write("Please enter a character name.")

    action_template = PromptTemplate(
        input_variables=['action_prompt', 'character_summary'],
        template="""You are a fantasy writer and  a famous fantasy novelist. A fan has given you the following paragraphs as character in your book:
                    {character_summary}
                    
                    You must write an short and concise epic and heart stopping snippet in the style of Brandon Sanderson for your book based on the following prompt, {action_prompt}""")
    # Add memory for player actions

    llm = OpenAI(temperature=0.8, max_tokens=2000)
    action_chain = LLMChain(llm=llm,
                            prompt=action_template,
                            verbose=True,
                            output_key='action', )

    if action_prompt:
        response = action_chain.run(action_prompt=action_prompt, character_summary=character_summary)
        st.write(response)

if 'character_summary' not in st.session_state:
    st.session_state.character_summary = None
# Create the tabs
tabs = ["Character Information", "Roleplaying Assistant"]
selected_tab = st.sidebar.selectbox("Select a tab", tabs)

# Display the selected tab
if selected_tab == "Character Information":
    character_inputs()
elif selected_tab == "Roleplaying Assistant":
    script_generator()
