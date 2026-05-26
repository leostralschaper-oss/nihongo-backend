-- ============================================================
-- Sample immersion segments — paste into Supabase SQL Editor
-- ============================================================

-- TRAVEL: Arriving at Tokyo Station (N5)
insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 1, '東京駅に着きました。', 'とうきょうえきに つきました。', 'I arrived at Tokyo Station.',
'[{"surface":"東京駅","base_form":"東京駅","reading":"とうきょうえき","meaning":"Tokyo Station","part_of_speech":"noun"},{"surface":"に","base_form":"に","reading":"に","meaning":"at / to","part_of_speech":"particle"},{"surface":"着きました","base_form":"着く","reading":"つきました","meaning":"arrived","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Arriving at Tokyo Station';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 2, 'きっぷを買います。', 'きっぷを かいます。', 'I will buy a ticket.',
'[{"surface":"きっぷ","base_form":"きっぷ","reading":"きっぷ","meaning":"ticket","part_of_speech":"noun"},{"surface":"を","base_form":"を","reading":"を","meaning":"object particle","part_of_speech":"particle"},{"surface":"買います","base_form":"買う","reading":"かいます","meaning":"buy","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Arriving at Tokyo Station';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 3, '電車は何番線ですか？', 'でんしゃは なんばんせん ですか？', 'Which platform is the train on?',
'[{"surface":"電車","base_form":"電車","reading":"でんしゃ","meaning":"train","part_of_speech":"noun"},{"surface":"何番線","base_form":"何番線","reading":"なんばんせん","meaning":"which platform","part_of_speech":"noun"},{"surface":"ですか","base_form":"です","reading":"ですか","meaning":"is it? (question)","part_of_speech":"auxiliary"}]'::jsonb
from public.immersion_content where title = 'Arriving at Tokyo Station';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 4, 'すみません、出口はどこですか？', 'すみません、でぐちは どこですか？', 'Excuse me, where is the exit?',
'[{"surface":"すみません","base_form":"すみません","reading":"すみません","meaning":"excuse me","part_of_speech":"interjection"},{"surface":"出口","base_form":"出口","reading":"でぐち","meaning":"exit","part_of_speech":"noun"},{"surface":"どこ","base_form":"どこ","reading":"どこ","meaning":"where","part_of_speech":"pronoun"}]'::jsonb
from public.immersion_content where title = 'Arriving at Tokyo Station';

-- DAILY LIFE: Cooking Ramen at Home (N5)
insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 1, '今日はラーメンを作ります。', 'きょうは ラーメンを つくります。', 'Today I will make ramen.',
'[{"surface":"今日","base_form":"今日","reading":"きょう","meaning":"today","part_of_speech":"noun"},{"surface":"ラーメン","base_form":"ラーメン","reading":"ラーメン","meaning":"ramen","part_of_speech":"noun"},{"surface":"作ります","base_form":"作る","reading":"つくります","meaning":"make","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Cooking Ramen at Home';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 2, 'まず、お湯を沸かします。', 'まず、おゆを わかします。', 'First, I will boil water.',
'[{"surface":"まず","base_form":"まず","reading":"まず","meaning":"first of all","part_of_speech":"adverb"},{"surface":"お湯","base_form":"お湯","reading":"おゆ","meaning":"hot water","part_of_speech":"noun"},{"surface":"沸かします","base_form":"沸かす","reading":"わかします","meaning":"boil","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Cooking Ramen at Home';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 3, '麺を三分間茹でます。', 'めんを さんぷんかん ゆでます。', 'Boil the noodles for three minutes.',
'[{"surface":"麺","base_form":"麺","reading":"めん","meaning":"noodles","part_of_speech":"noun"},{"surface":"三分間","base_form":"三分間","reading":"さんぷんかん","meaning":"three minutes","part_of_speech":"noun"},{"surface":"茹でます","base_form":"茹でる","reading":"ゆでます","meaning":"boil food","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Cooking Ramen at Home';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 4, 'スープをお椀に入れて、麺を乗せます。', 'スープを おわんに いれて、めんを のせます。', 'Pour the soup into a bowl and add the noodles.',
'[{"surface":"スープ","base_form":"スープ","reading":"スープ","meaning":"soup","part_of_speech":"noun"},{"surface":"お椀","base_form":"お椀","reading":"おわん","meaning":"bowl","part_of_speech":"noun"},{"surface":"麺","base_form":"麺","reading":"めん","meaning":"noodles","part_of_speech":"noun"},{"surface":"乗せます","base_form":"乗せる","reading":"のせます","meaning":"place on top","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Cooking Ramen at Home';

-- ANIME: A Day at School (N4)
insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 1, '今日は学校に早く来ました。', 'きょうは がっこうに はやく きました。', 'I came to school early today.',
'[{"surface":"今日","base_form":"今日","reading":"きょう","meaning":"today","part_of_speech":"noun"},{"surface":"学校","base_form":"学校","reading":"がっこう","meaning":"school","part_of_speech":"noun"},{"surface":"早く","base_form":"早い","reading":"はやく","meaning":"early","part_of_speech":"adjective"},{"surface":"来ました","base_form":"来る","reading":"きました","meaning":"came","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'A Day at School';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 2, '先生が黒板に書いています。', 'せんせいが こくばんに かいています。', 'The teacher is writing on the blackboard.',
'[{"surface":"先生","base_form":"先生","reading":"せんせい","meaning":"teacher","part_of_speech":"noun"},{"surface":"黒板","base_form":"黒板","reading":"こくばん","meaning":"blackboard","part_of_speech":"noun"},{"surface":"書いています","base_form":"書く","reading":"かいています","meaning":"is writing","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'A Day at School';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 3, '授業が始まります。静かにしてください。', 'じゅぎょうが はじまります。しずかに してください。', 'Class is starting. Please be quiet.',
'[{"surface":"授業","base_form":"授業","reading":"じゅぎょう","meaning":"class","part_of_speech":"noun"},{"surface":"始まります","base_form":"始まる","reading":"はじまります","meaning":"starts","part_of_speech":"verb"},{"surface":"静かに","base_form":"静か","reading":"しずかに","meaning":"quietly","part_of_speech":"adjective"},{"surface":"してください","base_form":"する","reading":"してください","meaning":"please do","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'A Day at School';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 4, '昼休みに友達と話しました。', 'ひるやすみに ともだちと はなしました。', 'I talked with my friend during lunch break.',
'[{"surface":"昼休み","base_form":"昼休み","reading":"ひるやすみ","meaning":"lunch break","part_of_speech":"noun"},{"surface":"友達","base_form":"友達","reading":"ともだち","meaning":"friend","part_of_speech":"noun"},{"surface":"話しました","base_form":"話す","reading":"はなしました","meaning":"talked","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'A Day at School';

-- NEWS: Cherry Blossom Season (N3)
insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 1, '今年も桜の季節がやってきました。', 'ことしも さくらのきせつが やってきました。', 'Cherry blossom season has come again this year.',
'[{"surface":"今年","base_form":"今年","reading":"ことし","meaning":"this year","part_of_speech":"noun"},{"surface":"桜","base_form":"桜","reading":"さくら","meaning":"cherry blossom","part_of_speech":"noun"},{"surface":"季節","base_form":"季節","reading":"きせつ","meaning":"season","part_of_speech":"noun"},{"surface":"やってきました","base_form":"やってくる","reading":"やってきました","meaning":"has arrived","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Cherry Blossom Season Begins';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 2, '公園では花見をする人々で賑わっています。', 'こうえんでは はなみをする ひとびとで にぎわっています。', 'The park is lively with people doing flower viewing.',
'[{"surface":"公園","base_form":"公園","reading":"こうえん","meaning":"park","part_of_speech":"noun"},{"surface":"花見","base_form":"花見","reading":"はなみ","meaning":"flower viewing","part_of_speech":"noun"},{"surface":"人々","base_form":"人","reading":"ひとびと","meaning":"people","part_of_speech":"noun"},{"surface":"賑わっています","base_form":"賑わう","reading":"にぎわっています","meaning":"is lively","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Cherry Blossom Season Begins';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 3, '今年の開花は例年より一週間早いそうです。', 'ことしのかいかは れいねんより いっしゅうかん はやいそうです。', 'The bloom this year is reportedly one week earlier than usual.',
'[{"surface":"開花","base_form":"開花","reading":"かいか","meaning":"blooming","part_of_speech":"noun"},{"surface":"例年","base_form":"例年","reading":"れいねん","meaning":"average year","part_of_speech":"noun"},{"surface":"一週間","base_form":"一週間","reading":"いっしゅうかん","meaning":"one week","part_of_speech":"noun"},{"surface":"早い","base_form":"早い","reading":"はやい","meaning":"early","part_of_speech":"adjective"}]'::jsonb
from public.immersion_content where title = 'Cherry Blossom Season Begins';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 4, '花びらが風に舞っている様子は本当に美しいです。', 'はなびらが かぜに まっている ようすは ほんとうに うつくしいです。', 'The sight of petals dancing in the wind is truly beautiful.',
'[{"surface":"花びら","base_form":"花びら","reading":"はなびら","meaning":"petal","part_of_speech":"noun"},{"surface":"風","base_form":"風","reading":"かぜ","meaning":"wind","part_of_speech":"noun"},{"surface":"舞っている","base_form":"舞う","reading":"まっている","meaning":"dancing / swirling","part_of_speech":"verb"},{"surface":"美しい","base_form":"美しい","reading":"うつくしい","meaning":"beautiful","part_of_speech":"adjective"}]'::jsonb
from public.immersion_content where title = 'Cherry Blossom Season Begins';

-- BUSINESS: Starting a Meeting (N3)
insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 1, 'それでは、会議を始めさせていただきます。', 'それでは、かいぎを はじめさせていただきます。', 'Well then, allow me to start the meeting.',
'[{"surface":"それでは","base_form":"それでは","reading":"それでは","meaning":"well then","part_of_speech":"conjunction"},{"surface":"会議","base_form":"会議","reading":"かいぎ","meaning":"meeting","part_of_speech":"noun"},{"surface":"始めさせていただきます","base_form":"始める","reading":"はじめさせていただきます","meaning":"humbly begin (keigo)","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Starting a Meeting';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 2, 'お忙しい中お集まりいただき、ありがとうございます。', 'おいそがしいなか おあつまりいただき、ありがとうございます。', 'Thank you for gathering despite your busy schedules.',
'[{"surface":"お忙しい中","base_form":"忙しい","reading":"おいそがしいなか","meaning":"despite being busy","part_of_speech":"expression"},{"surface":"お集まりいただき","base_form":"集まる","reading":"おあつまりいただき","meaning":"honored you gathered (keigo)","part_of_speech":"verb"},{"surface":"ありがとうございます","base_form":"ありがとう","reading":"ありがとうございます","meaning":"thank you very much","part_of_speech":"expression"}]'::jsonb
from public.immersion_content where title = 'Starting a Meeting';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 3, '本日の議題は三点ございます。', 'ほんじつの ぎだいは さんてん ございます。', 'Today we have three agenda items.',
'[{"surface":"本日","base_form":"本日","reading":"ほんじつ","meaning":"today (formal)","part_of_speech":"noun"},{"surface":"議題","base_form":"議題","reading":"ぎだい","meaning":"agenda item","part_of_speech":"noun"},{"surface":"三点","base_form":"三点","reading":"さんてん","meaning":"three items","part_of_speech":"noun"},{"surface":"ございます","base_form":"ある","reading":"ございます","meaning":"there are (humble)","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Starting a Meeting';

insert into public.immersion_segments (content_id, index, japanese, reading, translation, words)
select id, 4, 'ご質問があれば、遠慮なくおっしゃってください。', 'ごしつもんが あれば、えんりょなく おっしゃってください。', 'If you have any questions, please do not hesitate to ask.',
'[{"surface":"ご質問","base_form":"質問","reading":"ごしつもん","meaning":"question (polite)","part_of_speech":"noun"},{"surface":"遠慮なく","base_form":"遠慮","reading":"えんりょなく","meaning":"without hesitation","part_of_speech":"expression"},{"surface":"おっしゃってください","base_form":"言う","reading":"おっしゃってください","meaning":"please say (honorific)","part_of_speech":"verb"}]'::jsonb
from public.immersion_content where title = 'Starting a Meeting';
