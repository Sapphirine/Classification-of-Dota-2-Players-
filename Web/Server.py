from flask import Flask, request, render_template, jsonify
import os, pickle
import json, urllib2
import random

import time
import numpy as np
import pandas as pd

from collections import defaultdict

# ML models
from pyspark.context import SparkContext
from pyspark.mllib.classification import LogisticRegressionWithLBFGS,LogisticRegressionModel
from pyspark.mllib.util import MLUtils
from pyspark.mllib.evaluation import MulticlassMetrics


steam_key = "86FE36CEEF0FECD245B5C711C8B82C5A"
CONV64_32 = 76561197960265728
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
profile_map = {}
famous_map = {}
dota_appid = 570
cur_id32 = -1


model_map = {}
tag_name_map = defaultdict(dict)

sc = SparkContext('local')
for i in range(1,11):
	model_name = str(i) + "_players_model.model"
	print "load " + model_name
	model = LogisticRegressionModel.load(sc, "models/" + model_name)
	model_map[i] = model	

tag_name_map[1][0] = "newbie"
tag_name_map[1][1] = "normal"
tag_name_map[1][2] = "legend"
tag_name_map[1][3] = "divine"

tag_name_map[2][0] = "onlooker"
tag_name_map[2][1] = "effective assiatant"
tag_name_map[2][2] = "warrior"
tag_name_map[2][3] = "main force"
tag_name_map[2][4] = "tower killer"

tag_name_map[3][0] = "pioneer"
tag_name_map[3][1] = "enemy controller"
tag_name_map[3][2] = "backbone"
tag_name_map[3][3] = "babysitter"

tag_name_map[4][0] = "normal support"
tag_name_map[4][1] = "aggressive support"
tag_name_map[4][2] = "hunter"
tag_name_map[4][3] = "prophet"
tag_name_map[4][4] = "ruthless prophet"

tag_name_map[5][0] = "berserker"
tag_name_map[5][1] = "knight"
tag_name_map[5][2] = "paladin"
tag_name_map[5][3] = "shepherd"
tag_name_map[5][4] = "wizard"

tag_name_map[6][0] = "mediocre"
tag_name_map[6][1] = "white collar"
tag_name_map[6][2] = "gold digger"
tag_name_map[6][3] = "alchemist"

tag_name_map[7][0] = "one tenth"
tag_name_map[7][1] = "hard worker"
tag_name_map[7][2] = "main"
tag_name_map[7][3] = "dominator"

tag_name_map[8][0] = "kind person"
tag_name_map[8][1] = "footman"
tag_name_map[8][2] = "rifleman"
tag_name_map[8][3] = "ruthless killer"
tag_name_map[8][4] = "destroyer"

tag_name_map[9][0] = "selfish"
tag_name_map[9][1] = "weeder"
tag_name_map[9][2] = "guard"
tag_name_map[9][3] = "telescope"
tag_name_map[9][4] = "warder"

tag_name_map[10][0] = "philanthropist"
tag_name_map[10][1] = "pass line"
tag_name_map[10][2] = "expert"
tag_name_map[10][3] = "skilled master"

famous_id=["111620041","25907144","86745912","105248644","26771994","137193239","139876032","149486894","148215639","87012746","90892734","113705693","119576842","106863163","101695162","98878010"]
#famous_id=["111620041"]

	


#-----------------------------------------------------------

def save_obj(obj, name):
	path = os.path.join(SITE_ROOT, "obj", name + ".pkl")
	with open(path, 'wb+') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
	path = os.path.join(SITE_ROOT, "obj", name + ".pkl")
	with open(path, 'rb') as f:
		return pickle.load(f)

#-----------------------------------------------------------

def read_matches_id(file_name):     
    f_read_random = open(file_name, 'r+')
    random_matches_id = f_read_random.readlines()
    f_read_random.close()
    for i in range(len(random_matches_id)):
        random_matches_id[i] = random_matches_id[i].strip('\n')
    return random_matches_id

def get_match_data(id):
    # get one match's information
    match_dat = urllib2.urlopen("https://api.opendota.com/api/matches/" + str(id)).read()
    match_dat = json.loads(match_dat)
    return match_dat
    # Out put: match data of certain match id


# limit: 500
# game_mode: 1.All pick  3.Random Draft (most popular game mode) 22. ranked all pick
# version: 7.07 (latest game version)
def request_personal_match_id(id, num):    
    player_dat = urllib2.urlopen("https://api.opendota.com/api/players/"+str(id)+"/matches?limit="+str(num)+"#game_mode=1,3,22").read()
    #print player_dat
    player_info = json.loads(player_dat)
    f_player = open("single_player_match_id.txt", 'w')
    for i in range(num):
        f_player.write(str(player_info[i]['match_id']) + '\n')
    f_player.close()
    
#'account_id','hero_id','lose','isRadiant','duration'
# farm:'gold_per_min','xp_per_min','hero_damage','tower_damage'
# skill: 'kills','deaths','assists','last_hits','denies','rune_pickup','courier_kills'
# support: 'stuns','sentry_uses','sentry_kills', 'hero_healing','camp_stacked'    
    
def read_person_match_info(x_id):
    file_name = "single_player_match_id.txt"
    match_id = read_matches_id(file_name)
    f_write_match = open("single_player_match_dat.csv", 'w')
    f_write_match.write('duration'+','+'gpm'+','+'xpm'+','+'hero_damage_pm'+','+'tower_damage_pm'+','+'kills_pm'+','+
                       'deaths_pm'+','+'assists_pm'+','+'last_hits_pm'+','+'denies_pm'+','+'rune_pickup_pm'+','+
                       'courier_kills_pm'+','+'stuns_pm'+','+'sentry_uses_pm'+','+'sentry_kills_pm'+','+
                       'hero_healing_pm'+','+'camp_stacked_pm'+'\n')
    for match in match_id:
        match_dat = get_match_data(match)
        time.sleep(0.35)
	#print len(match_dat)
	#print x_id
        if (len(match_dat) == 41):
            for i in range(10):
		#print match_dat['players'][i]['account_id']
                if (str(match_dat['players'][i]['account_id']) == str(x_id)):
                    print "get"
                    # personal information 5
                    #f_write_match.write(str(match_dat['players'][i]['account_id']) + ',')
                    #f_write_match.write(str(match_dat['players'][i]['hero_id']) + ',')
                    #f_write_match.write(str(match_dat['players'][i]['lose']) + ',')
                    #f_write_match.write(str(int(match_dat['players'][i]['isRadiant'])) + ',')
                    d = match_dat['players'][i]['duration']
                    f_write_match.write(str(match_dat['players'][i]['duration']) + ',')
                    # farm 4
                    f_write_match.write(str(match_dat['players'][i]['gold_per_min']) + ',')
                    f_write_match.write(str(match_dat['players'][i]['xp_per_min']) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['hero_damage'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['tower_damage'])/d) + ',')
                    # skill 7
                    f_write_match.write(str(float(match_dat['players'][i]['kills'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['deaths'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['assists'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['last_hits'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['denies'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['rune_pickups'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['courier_kills'])/d) + ',')
                    # support 5
                    f_write_match.write(str(float(match_dat['players'][i]['stuns'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['sentry_uses'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['sentry_kills'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['hero_healing'])/d) + ',')
                    f_write_match.write(str(float(match_dat['players'][i]['camps_stacked'])/d) + '\n')
    f_write_match.close()

def get_person_average_info():
    file_name = "single_player_match_dat.csv"
    data = pd.read_csv(file_name)
    num = len(data)
    data_new = []
    cols = ['duration','gpm','xpm','hero_damage_pm','tower_damage_pm','kills_pm','deaths_pm','assists_pm',
        'last_hits_pm','denies_pm','rune_pickup_pm','courier_kills_pm','stuns_pm','sentry_uses_pm',
        'sentry_kills_pm', 'hero_healing_pm','camp_stacked_pm']
    for col in cols:
        v = 0
        if num != 0:
            v = sum(data[:][col])/num
        data_new.append(v)       
    data_new = np.r_['0,2,1', cols, data_new]    
    data_new_df = pd.DataFrame(data_new)
    data_new_df.to_csv("single_player_ave_dat.csv", index=False, header=False)

def gen_args(id):
    request_personal_match_id(id, num = 50)                                          
    read_person_match_info(id)            
    get_person_average_info()


def get_args(id, mode_name):
    data = pd.read_csv('single_player_ave_dat.csv')
    if mode_name == 1:
        return [data['kills_pm'].values[0], data['deaths_pm'].values[0], data['assists_pm'].values[0]]
    if mode_name == 2:
        return [data['tower_damage_pm'].values[0], data['assists_pm'].values[0],data['last_hits_pm'].values[0]]
    if mode_name == 3:
        return [data['assists_pm'].values[0], data['stuns_pm'].values[0], data['hero_healing_pm'].values[0]]    
    if mode_name == 4:
        return [data['kills_pm'].values[0], data['courier_kills_pm'].values[0], data['sentry_kills_pm'].values[0]]
    if mode_name == 5:
        return [data['stuns_pm'].values[0], data['hero_healing_pm'].values[0], data['camp_stacked_pm'].values[0]]
    if mode_name == 6:
        return [data['gpm'].values[0], data['kills_pm'].values[0], data['last_hits_pm'].values[0]]
    if mode_name == 7:
        return [data['gpm'].values[0], data['xpm'].values[0]]
    if mode_name == 8:
        return [data['hero_damage_pm'].values[0], data['tower_damage_pm'].values[0]]
    if mode_name == 9:
        return [data['sentry_uses_pm'].values[0], data['sentry_kills_pm'].values[0]]
    if mode_name == 10:
        return [data['last_hits_pm'].values[0], data['denies_pm'].values[0]]

#-----------------------------------------------------------


def gen_tags(name, args):
	global model_map, tag_name_map
	tag_id = model_map[name].predict(args)
	return tag_name_map[name][int(tag_id)]

def add_tags(steam_id32):
	global profile_map, model_map
	print steam_id32 + " start gen tags"
	# gen tags
	tags_array = []
	gen_args(steam_id32)
	for name in model_map:
		tags_array.append(gen_tags(name, get_args(steam_id32, name)))
	profile_map[steam_id32]["tags"] = tags_array	
	save_obj(profile_map, "profile_map")
	print tags_array
	

def get_profile(steam_id32, ask_tags, famous):
	global steam_key, profile_map, model_map, famous_map

	new_user = {}

	try:
		dota2_profile = urllib2.urlopen("https://api.opendota.com/api/players/" + steam_id32)
	except urllib2.HTTPError, e:
		print steam_id32 + " request_error"
		new_user["exist"] = False
		profile_map[steam_id32] = new_user
		save_obj(profile_map, "profile_map")
		return "request_error"
	
	dota2_profile = json.loads(dota2_profile.read()) 
	
	if "profile" not in dota2_profile:
		print steam_id32 + " id_not_exist"
		new_user["exist"] = False
		profile_map[steam_id32] = new_user
		save_obj(profile_map, "profile_map")
		return "id_not_exsit"
	
	new_user["steam_id64"] = dota2_profile["profile"]["steamid"]
	new_user["steam_id32"] = steam_id32
	new_user["avatar_full"] = dota2_profile["profile"]["avatarfull"]
	new_user["avatar_medium"] = dota2_profile["profile"]["avatarmedium"]
	new_user["personaname"] = dota2_profile["profile"]["personaname"]
	new_user["name"] = dota2_profile["profile"]["name"]
	new_user["exist"] = True

	if ask_tags == True:
		gen_args(steam_id32)
		print steam_id32 + " start gen tags"
		# gen tags
		tags_array = []
		for name in model_map:
			tags_array.append(gen_tags(name, get_args(steam_id32, name)))
		new_user["tags"] = tags_array
		print tags_array
	else:
		new_user["tags"] = []
		print new_user["tags"]


	#new_user["tags"] = ["aaa", "bbb", "ccc", "ddd"]
	
	# get friends
	try:
		friends = urllib2.urlopen("http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key="+ steam_key + "&steamid=" + new_user["steam_id64"] + "&relationship=friend")
	except urllib2.HTTPError, e:
		new_user["exist"] = False
		profile_map[steam_id32] = new_user
		save_obj(profile_map, "profile_map")
		print steam_id32 + " friends request_error"
		return "request_error"
	
	friends = json.loads(friends.read())
	friend_list = []
	if "friendslist" in friends:
		for x in friends["friendslist"]["friends"]:
			#print x["steamid"]
			friend_id32 = int(x["steamid"]) - CONV64_32
			friend_list.append(str(friend_id32))

	new_user["friends"] = friend_list
	#print new_user.friends	
	if famous == True:
		famous_map[steam_id32] = new_user
		save_obj(famous_map, "famous_map")
	else:
		profile_map[steam_id32] = new_user
		save_obj(profile_map, "profile_map")

	print "get " + steam_id32 + " done" 

	return "OK"

def count_same_tags(id1, id2):
	global profile_map, famous_map
	id1_map = {}
	count = 0
	for x in profile_map[id1]["tags"]:
		id1_map[x] = True
	for x in famous_map[id2]["tags"]:
		if x in id1_map:
			count += 1
	return count

def gen_children(steam_id32):
	global profile_map
	re_hash = {}
	user = profile_map[steam_id32]
	re_hash["name"] = user["name"]
	re_hash["img"] = user["avatar_medium"]
	re_hash["size"] = 4
	re_hash["value"] = 8
	re_hash["type"] = 2
	re_hash["steam_id32"] = user["steam_id32"]
	re_hash["tags"] = user["tags"]
	return re_hash

def gen_famous_children(steam_id32):
	global famous_map, cur_id32
	re_hash = {}
	user = famous_map[steam_id32]
	#print user
	re_hash["name"] = user["name"]
	re_hash["img"] = user["avatar_medium"]
	re_hash["size"] = 4
	re_hash["value"] = (count_same_tags(cur_id32, steam_id32) + 1) * 25
	re_hash["type"] = 1
	re_hash["steam_id32"] = user["steam_id32"]
	re_hash["tags"] = user["tags"]
	return re_hash




def graph_json(master):
	global cur_id32, profile_map, famous_map
	re_json = {}
	
	cur_obj = profile_map[cur_id32]

	re_json["name"] = cur_obj["name"]
	re_json["img"] = cur_obj["avatar_medium"]
	re_json["steam_id32"] = cur_id32
	re_json["father"] = 1
	re_json["tags"] = cur_obj["tags"]

	children = []

	if master == True:
		for x in famous_map:
			children.append(gen_famous_children(x)) 
	else:
		print "friends len: " + str(len(cur_obj["friends"]))
		print cur_obj["friends"]
		count = 0
		for friend in cur_obj["friends"]:
			#print cur_obj.friends
			count += 1
			friend = str(friend)

			if friend not in profile_map:
				ok = get_profile(friend, False, False)
				if ok == "OK":
					tmp = gen_children(friend)
					children.append(tmp)
			elif profile_map[friend]["exist"] == True:
				tmp = gen_children(friend)
				children.append(tmp)


	re_json["children"] = children
	return re_json
	

#------------------------------------------------------------

app = Flask(__name__)

if os.path.isfile('obj/famous_map.pkl'):
	famous_map = load_obj("famous_map")
else:
	for x in famous_id:
		get_profile(x, True, True)

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/query')
def query():
	global profile_map, cur_id32
	steam_id32 = request.args.get('x', 0, type=int)

	if len(profile_map) == 0 and os.path.isfile('obj/profile_map.pkl'):
		profile_map = load_obj("profile_map")

	steam_id32 = str(steam_id32)
	if steam_id32 not in profile_map:
		res = get_profile(str(steam_id32), True, False)
		if res != "OK":
			return jsonify(result = res)
	elif profile_map[steam_id32]["exist"] == True and len(profile_map[steam_id32]["tags"]) == 0:
		print "profile exist no tags, add tags"
		add_tags(steam_id32)
			

	profile_obj = profile_map[steam_id32]
	cur_id32 = str(steam_id32)
	if profile_obj["exist"] == False:
		return jsonify(result = "id_not_exsit")

	#print(profile_obj["tags"])

	return jsonify(result = "OK",
				   img_url = profile_obj["avatar_full"],
				   name = profile_obj["name"],
				   personaname = profile_obj["personaname"],
				   tags = profile_obj["tags"])
	

@app.route('/json_master')
def json_master():
	re_json = graph_json(True)
	re = json.dumps(re_json)
	print re
	return re

@app.route('/json_friends')
def json_friends():
	re_json = graph_json(False)
	re = json.dumps(re_json)
	print re
	return re





