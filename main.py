import g4f
import asyncio
import json
import translators as ts
import  PySimpleGUI as sg

def translate_array(a):
    b = []
    for i in a:
        b.append(ts.translate_text(i, to_language='ru'))
    return b

def save(save_t:str, tag:str = "memory", database:str = "Memory.json"):
    data = load(database)
    with open(database, 'w', encoding='utf-8') as json_file:
        data[tag] = save_t
        json.dump(data, json_file, indent=2, separators=(',', ': '), ensure_ascii=False)

def load(database:str = "Memory.json"):
    with open(database, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

# Params
history = load("database.json")["history"]
memory = load()["memory"]
notes = load()["notes"]
name = load()["name"]
description = load()["description"]
stats = load()["stats"]
max_words_count = 50
log = False
error = True
_providers = [
    g4f.Provider.GPTalk,
    #g4f.Provider.ChatBase
]

def hp():
    d = 1

def GUI():
    sg.theme('DarkAmber')
    quests = translate_array(load()["quests"])
    layout = [  [sg.Text('Информация')],
                [sg.Text(f'Имя: {name}')],
                [sg.Text(f'LVL: {stats["level"]}, XP: {stats["xp"]}/{stats["max_xp"]}, HP: {stats["hp"]}/{stats["max_hp"]}')],
                [sg.Text('Квесты:')],
                [sg.Multiline('\n'.join(quests),s=(50,3), autoscroll=True, write_only=True)],
                [sg.Text('История')],
                [sg.Multiline('\n'.join(history),s=(100,20), autoscroll=True, write_only=True, key='-OUT-')],
                [sg.Text('Введите действие:'), sg.InputText(key='-IN-')],
                [sg.Button('Выполнить действие')] ]
    return layout

async def gpt(prompt:str)->str:
    provider = g4f.Provider.GPTalk
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
            provider=provider,
        )
        if (log): print(f"{provider.__name__}:", response)
        return response
    except Exception as e:
        if (error): print(f"{provider.__name__}:", e)
        return ""

async def make_prompt(PI:str)->str:
    quests = load()["quests"]
    memory = load()["memory"]
    location = load()["location"]
    world = load()["world"]
    characters = load()["characters"]
    prompt = "You are Narrator in dark fantasy rpg game. You can describe the environment and play characters and enemies. But not the player. Reply to the player's action. " \
             f"Use concise sentences. Use around {max_words_count} words." \
             "Info: {" \
             "Location: " + location + \
             "; World info: " + world + \
             "; Player name: " + name + \
             "; Player description: " + description + \
             "; Quests: " + ", ".join(quests) + \
             "; Characters around: [Enemies:" + ", ".join(characters["enemies"]) + "; Allies:" + ", ".join(characters["allies"]) + "; Neutral:" + ", ".join(characters["neutral"]) + \
             "]; What happened before: [" + "\n".join(memory) + "]; Notes: " + notes +  \
             "; Player last respond: [" + PI + "]}"
    if (log): print("Prompt roleplay: " + prompt)
    return prompt

async def make_memory(msg):
    memory.append(msg)
    if (len(memory) > 4): memory.pop(0)
    save(memory, "memory")
    for sentence in msg.split('.'):
        history.append(ts.translate_text(sentence, to_language='ru'))
    save(history, "history", "database.json")

async def main():
    window = sg.Window('Нейро-шутовская днд', GUI())
    while True:
        event, values = window.read()
        player_input = ts.translate_text(values["-IN-"], to_language='en')
        prompt = await make_prompt(player_input)
        msg = await gpt(prompt)
        await make_memory(name + " (Player): " + player_input + ". \n" + msg)
        if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
            break
        window['-OUT-'].update('\n'.join(history))
        """
        for sentence in msg.split('.'):
            print(ts.translate_text(sentence, to_language='ru') + "\n ", end="", flush=True)
        """
asyncio.run(main())