"""Kanal kurulumu (tekrar çalıştırılabilir, GitHub Actions 'channel' workflow'u ile, secrets'taki token kullanılır):
açıklama, anahtar kelimeler, ülke/dil, banner, filigran, fragman, oynatma listeleri, ana sayfa bölümleri,
yüklenmiş videoların listelere eklenmesi.

Profil fotoğrafı ve @handle API ile değiştirilemez: branding/profile.png'yi YouTube Studio > Customization'dan yükle.
"""
import csv
import json
import sys
from pathlib import Path

from googleapiclient.http import MediaFileUpload

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import upload  # noqa: E402

BRAND = HERE / 'branding'
PLAYLISTS_FILE = HERE / 'playlists.json'

DESCRIPTION = """Dex has an excuse for everything. Mama Rose has a slipper for every excuse.

Welcome to Dex & Friends: short animated comedy about the chaos of everyday life. Family rules that make zero sense, school excuses, first jobs, the gym, weddings, bosses and the little brother who snitches on everyone.

Meet the crew:
🧢 Dex: lazy, full of excuses, always looking for a shortcut
👓 Nia: smart, sarcastic, catches every lie
🩴 Mama Rose: strict, loud, loving and armed with a slipper
🕶️ Big Tony: thinks he is a business genius
🎧 Pip: the little brother who tells Mom everything
📣 Coach Barry: yells the worst motivational advice ever

New Shorts every day and full episodes every week.
Subscribe and tell us in the comments what Dex should get caught doing next! 👇

#DexAndFriends #animation #comedy"""

KEYWORDS = ('"Dex and Friends" animation "animated comedy" cartoon "stick figure" "stickman animation" '
            '"funny animation" "animated story" "mom logic" "relatable comedy" "funny shorts" "family comedy" '
            '"school comedy" "expectation vs reality" "types of people" "plot twist" "cartoon shorts"')

PLAYLISTS = {
    'caught': ('Caught Lying 😭', 'Dex lies. Somebody always catches him. The slipper always wins.'),
    'mom_logic': ('Mom Logic 🩴', "Mama Rose's house rules make zero sense. Arguing makes it worse."),
    'expectation_reality': ('Expectation vs Reality', 'The plan vs what actually happened.'),
    'types_of_people': ('Types of People', 'Every wedding, school and gym has these people.'),
    'plot_twist': ('Plot Twists 💀', 'Normal conversation... until the last 3 seconds.'),
    'dexs_terrible_ideas': ("Dex's Terrible Ideas", "Full episodes: Dex has a plan. It's a terrible plan."),
    'growing_up_with_mama_rose': ('Growing Up With Mama Rose', 'Full episodes: family chaos at home.'),
    'big_tonys_business_lessons': ("Big Tony's Business Lessons", 'Full episodes: Big Tony teaches business. It backfires.'),
}
SECTIONS = ['caught', 'mom_logic', 'plot_twist', 'expectation_reality', 'types_of_people']


def step(name, fn):
    try:
        fn(); print(f'✓ {name}', flush=True)
    except Exception as e:
        print(f'✗ {name}: {str(e)[:300]}', flush=True)


def main():
    yt = upload.client()
    ch = yt.channels().list(part='id,snippet,brandingSettings,status', mine=True).execute()['items'][0]
    cid, title = ch['id'], ch['snippet']['title']
    print(f'kanal: {title}')
    published = list(csv.DictReader(open(HERE / 'published.csv', encoding='utf-8'))) if (HERE / 'published.csv').exists() else []

    def branding():
        banner = yt.channelBanners().insert(
            media_body=MediaFileUpload(str(BRAND / 'banner.png'), mimetype='image/png')).execute()
        channel = {'title': title, 'description': DESCRIPTION, 'keywords': KEYWORDS, 'country': 'US',
                   'defaultLanguage': 'en'}
        if published:
            channel['unsubscribedTrailer'] = published[0]['video_id']
        yt.channels().update(part='brandingSettings', body={'id': cid, 'brandingSettings': {
            'channel': channel, 'image': {'bannerExternalUrl': banner['url']}}}).execute()
    step('açıklama, anahtar kelimeler, ülke/dil, banner, fragman', branding)

    step('kanal: çocuklara yönelik değil', lambda: yt.channels().update(part='status', body={
        'id': cid, 'status': {'selfDeclaredMadeForKids': False}}).execute())

    def watermark():
        body = {'timing': {'type': 'offsetFromStart', 'offsetMs': 0},
                'position': {'type': 'corner', 'cornerPosition': 'topRight'}}
        errors = []
        for kw in (dict(resumable=True, chunksize=-1), dict(resumable=False), dict(resumable=True, chunksize=256 * 1024)):
            try:
                media = MediaFileUpload(str(BRAND / 'watermark.png'), mimetype='image/png', **kw)
                req = yt.watermarks().set(channelId=cid, body=body, media_body=media)
                if kw.get('resumable'):
                    resp = None
                    while resp is None:
                        _, resp = req.next_chunk()
                else:
                    req.execute()
                return
            except Exception as e:
                errors.append(str(e)[:150])
        raise RuntimeError(' | '.join(errors))
    step('filigran (abone ol)', watermark)

    existing = {p['snippet']['title']: p['id'] for p in
                yt.playlists().list(part='snippet', mine=True, maxResults=50).execute().get('items', [])}
    ids = json.loads(PLAYLISTS_FILE.read_text(encoding='utf-8')) if PLAYLISTS_FILE.exists() else {}
    for key, (ptitle, pdesc) in PLAYLISTS.items():
        if key in ids:
            continue
        if ptitle in existing:
            ids[key] = existing[ptitle]; continue
        p = yt.playlists().insert(part='snippet,status', body={
            'snippet': {'title': ptitle, 'description': pdesc + '\n\nNew Dex & Friends animation every day. #DexAndFriends',
                        'defaultLanguage': 'en'},
            'status': {'privacyStatus': 'public'}}).execute()
        ids[key] = p['id']; print(f'✓ oynatma listesi: {ptitle}')
    PLAYLISTS_FILE.write_text(json.dumps(ids, indent=2) + '\n', encoding='utf-8')

    for row in published:
        key = row.get('template')
        if key not in ids:
            continue
        have = yt.playlistItems().list(part='contentDetails', playlistId=ids[key], maxResults=50).execute().get('items', [])
        if any(i['contentDetails']['videoId'] == row['video_id'] for i in have):
            continue
        step(f"video {row['video_id']} -> {key}", lambda: upload.add_to_playlist(ids[key], row['video_id']))

    have = yt.channelSections().list(part='snippet,contentDetails', mine=True).execute().get('items', [])
    have = {(s['snippet']['type'], tuple(s.get('contentDetails', {}).get('playlists', []))) for s in have}
    wanted = [('recentUploads', ()), ('popularUploads', ())] + [('singlePlaylist', (ids[k],)) for k in SECTIONS]
    for pos, (stype, pls) in enumerate(wanted):
        if (stype, pls) in have:
            continue
        body = {'snippet': {'type': stype, 'position': pos}}
        if pls:
            body['contentDetails'] = {'playlists': list(pls)}
        step(f'ana sayfa bölümü {stype} {pls}', lambda: yt.channelSections().insert(
            part='snippet,contentDetails', body=body).execute())
    print('\nElle yapılacak: branding/profile.png -> YouTube Studio > Customization > Branding > Picture')


if __name__ == '__main__':
    main()
