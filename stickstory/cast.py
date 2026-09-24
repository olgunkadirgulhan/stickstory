"""Karakter kadrosu (orijinal). Renkler 0-1 RGB, ses = Kokoro voice id.

pitch > 1 sesi inceltir (Kokoro çıktısı yeniden örneklenir), speed konuşma hızıdır.
"""

CAST = {
    'dex': {
        'name': 'Dex', 'shirt': (1.0, 0.55, 0.12), 'skin': (0.99, 0.85, 0.70), 'scale': 1.0,
        'voice': 'am_puck', 'speed': 1.05, 'pitch': 1.06, 'accent': (1.0, 0.62, 0.15),
        'bible': 'Dex (orange t-shirt, backwards green cap): lazy young guy full of excuses, always looks for shortcuts.',
    },
    'nia': {
        'name': 'Nia', 'shirt': (0.58, 0.33, 0.85), 'skin': (0.80, 0.58, 0.42), 'scale': 0.97,
        'voice': 'af_bella', 'speed': 1.0, 'pitch': 1.02, 'accent': (0.78, 0.55, 1.0),
        'bible': "Nia (purple dress, big round glasses, hair bun): smart, sarcastic, always catches Dex's lies. Dry humor.",
    },
    'mama_rose': {
        'name': 'Mama Rose', 'shirt': (0.98, 0.72, 0.78), 'skin': (0.93, 0.75, 0.60), 'scale': 1.0,
        'voice': 'af_sarah', 'speed': 1.0, 'pitch': 0.97, 'accent': (1.0, 0.35, 0.35),
        'bible': 'Mama Rose (red apron, slipper as a weapon): strict but loving mom, loud, has absurd house rules.',
    },
    'big_tony': {
        'name': 'Big Tony', 'shirt': (0.50, 0.52, 0.56), 'skin': (0.86, 0.66, 0.52), 'scale': 1.08,
        'voice': 'am_onyx', 'speed': 0.93, 'pitch': 0.90, 'accent': (0.75, 0.78, 0.82),
        'bible': 'Big Tony (grey suit, sunglasses): thinks he is rich and a business genius, boss/neighbor, slow deep voice.',
    },
    'pip': {
        'name': 'Pip', 'shirt': (1.0, 0.84, 0.15), 'skin': (0.99, 0.85, 0.70), 'scale': 0.78,
        'voice': 'af_sky', 'speed': 1.02, 'pitch': 1.22, 'accent': (1.0, 0.9, 0.2),
        'bible': 'Pip (yellow hoodie, headphones): little brother, snitches on everyone, squeaky voice.',
    },
    'coach_barry': {
        'name': 'Coach Barry', 'shirt': (0.20, 0.68, 0.35), 'skin': (0.62, 0.43, 0.30), 'scale': 1.02,
        'voice': 'am_fenrir', 'speed': 1.08, 'pitch': 0.98, 'accent': (0.35, 0.9, 0.45),
        'bible': 'Coach Barry (green tracksuit, whistle): over-motivational coach who yells ridiculous advice.',
    },
}

EMOTIONS = ['neutral', 'happy', 'angry', 'shock', 'cry', 'nervous', 'sad', 'smug', 'confused', 'excited', 'suspicious']
POSES = ['standing', 'arms_crossed', 'hips', 'pointing', 'shrug', 'celebrate', 'facepalm', 'thinking', 'phone', 'fist',
         'crying', 'sitting']
ACTIONS = ['throw_slipper', 'slap', 'faint', 'run_away', 'jump', 'door_slam', 'dramatic_zoom', 'rimshot', 'spin']
SFX = ['slap', 'whoosh', 'boing', 'pop', 'thud', 'ding', 'crash', 'rimshot', 'sting', 'door', 'buzz', 'gasp_hit']


def bible():
    return '\n'.join('- id "%s": %s' % (k, v['bible']) for k, v in CAST.items())
