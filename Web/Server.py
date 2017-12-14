from flask import Flask, request, render_template, jsonify
import os, pickle
import json, urllib2
import random

# ML models
#from pyspark.context import SparkContext
#from pyspark.mllib.classification import LogisticRegressionWithLBFGS,LogisticRegressionModel
#from pyspark.mllib.util import MLUtils
#from pyspark.mllib.evaluation import MulticlassMetrics


steam_key = "86FE36CEEF0FECD245B5C711C8B82C5A"
CONV64_32 = 76561197960265728
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
profile_map = {}
dota_appid = 570
cur_id32 = -1


#sc = SparkContext('local')
#test_model = LogisticRegressionModel.load(sc, "models/test_model.model")
#model_map = {}
#tag_name_map = {}



#-----------------------------------------------------------

def save_obj(obj, name):
	path = os.path.join(SITE_ROOT, "obj", name + ".pkl")
	with open(path, 'wb+') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
	path = os.path.join(SITE_ROOT, "obj", name + ".pkl")
	with open(path, 'rb') as f:
		return pickle.load(f)


#def gen_tags(name, args):
#	global model_map, tag_name_map
#	tag_id = model_map[name].predict(args)
#	return tag_name_map[name][tag_id]

#def get_args()
	

def get_profile(steam_id32):
	global steam_key, profile_map, model_map

	if steam_id32 in profile_map:
		return steam_id32 + " already exist"

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

	# gen tags
	#for name in model_map:
	#	new_user["tags"].append(gen_tags(name, get_args(steam_id32, name)))


	new_user["tags"] = ["aaa", "bbb", "ccc", "ddd"]
	
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
	profile_map[steam_id32] = new_user
	save_obj(profile_map, "profile_map")

	print "get " + steam_id32 + " done" 

	return "OK"

def gen_children(steam_id32, t):
	global profile_map
	re_hash = {}
	user = profile_map[steam_id32]
	re_hash["name"] = user["name"]
	re_hash["img"] = user["avatar_medium"]
	re_hash["size"] = 4
	re_hash["value"] = 8
	re_hash["type"] = t
	re_hash["steam_id32"] = user["steam_id32"]
	re_hash["tags"] = user["tags"]
	return re_hash

def count_same_tags(id1, id2):
	global profile_map
	id1_map = {}
	count = 0
	for x in profile_map[id1][tags]:
		id1_map[x] = True
	for x in profile_map[id2][tags]:
		if x in id1_map:
			count += 1
	return count


def graph_json(master):
	global cur_id32, profile_map
	re_json = {}

	cur_obj = profile_map[cur_id32]
	re_json["name"] = cur_obj["name"]
	re_json["img"] = cur_obj["avatar_medium"]
	re_json["steam_id32"] = cur_id32
	re_json["father"] = 1
	re_json["tags"] = cur_obj["tags"]

	children = []
	print "friends len: " + str(len(cur_obj["friends"]))
	print cur_obj["friends"]
	count = 0
	for friend in cur_obj["friends"]:
		#print cur_obj.friends
		count += 1
		friend = str(friend)

		if friend not in profile_map:
			ok = get_profile(friend)
			if ok == "OK":
				tmp = gen_children(friend, random.randint(1,2))
				if master and tmp["type"] == 1:
					children.append(tmp)
				elif not master and tmp["type"] == 2:
					children.append(tmp)
		elif profile_map[friend]["exist"] == True:
			tmp = gen_children(friend, random.randint(1,2))
			if master and tmp["type"] == 1:
				children.append(tmp)
			elif not master and tmp["type"] == 2:
				children.append(tmp)


	re_json["children"] = children
	return re_json
	

#------------------------------------------------------------

app = Flask(__name__)

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
		res = get_profile(str(steam_id32))
		if res != "OK":
			return jsonify(result = res)


	profile_obj = profile_map[steam_id32]
	cur_id32 = str(steam_id32)
	if profile_obj["exist"] == False:
		return jsonify(result = "id_not_exsit")

	print(profile_obj["tags"])

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





