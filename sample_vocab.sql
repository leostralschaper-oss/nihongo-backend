-- ============================================================
-- Sample vocab cards — auto-inserts for your first user account
-- Run in Supabase SQL Editor
-- ============================================================

do $$
declare
  uid uuid;
begin
  select id into uid from auth.users order by created_at limit 1;

  insert into public.vocab_cards
    (user_id, word, reading, meaning, jlpt_level, tags,
     repetitions, interval_days, ease_factor, memory_strength,
     next_review_at, last_reviewed_at, learned_at)
  values
    (uid, '日本語',   'にほんご',       'Japanisch',           'N5', '{sprache}',     0, 1, 2.5, 0.3, now(), now() - interval '3 days', now() - interval '5 days'),
    (uid, '学校',     'がっこう',       'Schule',              'N5', '{orte}',        1, 3, 2.4, 0.5, now(), now() - interval '2 days', now() - interval '7 days'),
    (uid, '電車',     'でんしゃ',       'Zug / U-Bahn',        'N5', '{transport}',   0, 1, 2.5, 0.2, now(), now() - interval '4 days', now() - interval '6 days'),
    (uid, '食べる',   'たべる',         'essen',               'N5', '{verben}',      2, 6, 2.6, 0.7, now(), now() - interval '1 days', now() - interval '10 days'),
    (uid, '飲む',     'のむ',           'trinken',             'N5', '{verben}',      0, 1, 2.5, 0.1, now(), now() - interval '5 days', now() - interval '8 days'),
    (uid, '友達',     'ともだち',       'Freund / Freundin',   'N5', '{personen}',    1, 4, 2.5, 0.6, now(), now() - interval '2 days', now() - interval '9 days'),
    (uid, '先生',     'せんせい',       'Lehrer / Lehrerin',   'N5', '{personen}',    3, 8, 2.7, 0.8, now() + interval '2 days', now() - interval '1 days', now() - interval '12 days'),
    (uid, '水',       'みず',           'Wasser',              'N5', '{essen}',       0, 1, 2.5, 0.15, now(), now() - interval '6 days', now() - interval '7 days'),
    (uid, '今日',     'きょう',         'heute',               'N5', '{zeit}',        2, 5, 2.5, 0.65, now(), now() - interval '2 days', now() - interval '11 days'),
    (uid, '明日',     'あした',         'morgen',              'N5', '{zeit}',        0, 1, 2.5, 0.25, now(), now() - interval '3 days', now() - interval '5 days'),
    (uid, '大きい',   'おおきい',       'groß',                'N5', '{adjektive}',   1, 3, 2.4, 0.45, now(), now() - interval '2 days', now() - interval '8 days'),
    (uid, '小さい',   'ちいさい',       'klein',               'N5', '{adjektive}',   0, 1, 2.5, 0.1, now(), now() - interval '5 days', now() - interval '6 days'),
    (uid, '見る',     'みる',           'sehen / schauen',     'N5', '{verben}',      2, 7, 2.6, 0.75, now() + interval '1 days', now(), now() - interval '14 days'),
    (uid, '行く',     'いく',           'gehen',               'N5', '{verben}',      1, 2, 2.5, 0.4, now(), now() - interval '3 days', now() - interval '6 days'),
    (uid, '来る',     'くる',           'kommen',              'N4', '{verben}',      0, 1, 2.5, 0.2, now(), now() - interval '4 days', now() - interval '5 days'),
    (uid, '言葉',     'ことば',         'Wort / Sprache',      'N4', '{sprache}',     1, 3, 2.4, 0.5, now(), now() - interval '1 days', now() - interval '9 days'),
    (uid, '勉強',     'べんきょう',     'Studium / Lernen',    'N4', '{schule}',      0, 1, 2.5, 0.15, now(), now() - interval '5 days', now() - interval '7 days'),
    (uid, '難しい',   'むずかしい',     'schwierig',           'N4', '{adjektive}',   2, 6, 2.5, 0.7, now() + interval '3 days', now() - interval '1 days', now() - interval '13 days'),
    (uid, '面白い',   'おもしろい',     'interessant / lustig','N4', '{adjektive}',   0, 1, 2.5, 0.3, now(), now() - interval '2 days', now() - interval '4 days'),
    (uid, '桜',       'さくら',         'Kirschblüte',         'N3', '{natur}',       1, 4, 2.5, 0.55, now(), now() - interval '2 days', now() - interval '10 days')
  on conflict (user_id, word) do nothing;

  raise notice 'Inserted vocab cards for user %', uid;
end;
$$;
