def pet_emoji(id):
    if id == 1:
        e = "🥚"
    elif id == 2:
        e = "🐭"
    elif id == 3:
        e = "🕷"
    elif id == 4:
        e = "🐈"
    elif id == 5:
        e = "🐢"
    elif id == 6:
        e = "🦃"
    elif id == 7:
        e = "🦔"
    elif id == 8:
        e = "🦉"
    elif id == 9:
        e = "🦇"
    elif id == 10:
        e = "🦝"
    elif id == 11:
        e = "🦌"
    elif id == 12:
        e = "🦍"
    elif id == 13:
        e = "🦓"
    elif id == 14:
        e = "🐅"
    elif id == 15:
        e = "🐆"
    elif id == 16:
        e = "🦐"
    elif id == 17:
        e = "🐠"
    elif id == 18:
        e = "🦑"
    elif id == 19:
        e = "🐙"
    elif id == 20:
        e = "🦭"
    elif id == 21:
        e = "🐂"
    elif id == 22:
        e = "🦒"
    elif id == 23:
        e = "🦢"
    elif id == 24:
        e = "🐳"
    elif id == 25:
        e = "🦜"
    elif id == 26:
        e = "🐛"
    elif id == 27:
        e = "🦙"
    elif id == 28:
        e = "🦩"
    elif id == 29:
        e = "🐍"
    elif id == 30:
        e = "🦘"
    elif id == 31:
        e = "🦣"
    elif id == 50:
        e = "🦕"
    elif id == 51:
        e = "🦖"
    elif id == 60:
        e = "🦄"
    elif id == 61:
        e = "🐇"           
    elif id == 0:
        e = "☠"
    else:
        e = "❌"
    return e

def item_emoji(id):
    if id == 1:
        e = "⬜"
    elif id == 2:
        e = "🟦"
    elif id == 3:
        e = "🟪"
    elif id == 5:
        e = "💉"
    elif id == 6:
        e = "🔐"
    elif id == 7:
        e = "🚨"
    elif id == 10:
        e = "📔"
    elif id == 11:
        e = "🧯"
    elif id == 12:
        e = "🔭"
    elif id == 13:
        e = "🗺"
    elif id == 14:
        e = "🥫"
    elif id == 15:
        e = "🔬"
    elif id == 16:
        e = "⛏️"
    elif id == 20:
        e = "🔑"
    elif id == 30:
        e = "🥣"
    elif id == 31:
        e = "🚐"
    elif id == 40:
        e = "🦴"
    elif id == 41:
        e = "🦴"
    elif id == 42:
        e = "🥚"
    elif id == 43:
        e = "🥚"
    elif id == 45:
        e = "🪨"
    elif id == 46:
        e = "☢️"
    elif id == 47:
        e = "💫"
    else:
        e = "✖"
    return e


# values(1,'desert'),(2,'field'),(3,'forest'),(4,'water'),(5,'any')
def habitat_emoji(id):
    if id == 1:
        e = "🏜"
    elif id == 2:
        e = "🛣" # maby don't use at all
    elif id == 3:
        e = "🌲"
    elif id == 4:
        e = "🌊"
    elif id == 5:
        e = "🏠"
    elif id == 6:
        e = "🌎"
    elif id == 7:
        e = "🇦🇺"
    elif id == 10:
        e = "🌈"
    else:
        e = "❔"
    return e

def define_mood(pet: list, environment: list=None):
    hunger = pet[2]
    health = pet[3]
    habitat = pet[6]
    shit = pet[10]
    sum_points = hunger + health - shit
    mood = "😐"
    if hunger == 0 or health == 1:
        mood = "🥴"
    elif sum_points < 5:
        mood = "😒"
    elif sum_points < 8:
        mood = "😐"
    elif sum_points >  12:
        mood = "😀"
    elif sum_points > 16:
        mood = "🥳"
    return mood

def tech_emoji(id):
    if id == 1:
        e = "🌌"
    elif id == 2:
        e = "🦣" # maby don't use at all
    elif id == 3:
        e = "🦠"
    elif id == 4:
        e = "🧬"
    elif id == 5:
        e = "🧬"
    elif id == 6:
        e = "🧬🦕"
    elif id == 7:
        e = "🧬🦖"
    elif id == 8:
        e = "☢️"
    elif id == 9:
        e = "💫"
    else:
        e = "❔"
    return e