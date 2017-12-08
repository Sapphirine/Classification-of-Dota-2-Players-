from flask import Flask, request, render_template, jsonify
import os, pickle
import json, urllib2

steam_key = "86FE36CEEF0FECD245B5C711C8B82C5A"
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
profile_map = {}


#-----------------------------------------------------------

def save_obj(obj, name):
	path = os.path.join(SITE_ROOT, "obj", name + ".pkl")
	with open(path, 'wb+') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
	path = os.path.join(SITE_ROOT, "obj", name + ".pkl")
	with open(path, 'rb') as f:
		return pickle.load(f)

class Profile:
	exist = "not_exsit"
	steam_id32 = ""
	steam_id64 = ""
	avatar_medium = ""
	avatar_full = ""
	name = ""
	personaname = ""
	friends = []
	tags = ["aaa","bbb"]
	
	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
	

def get_profile(steam_id32):
	global steam_key, profile_map
	new_user = Profile()
	new_user.steam_id32 = steam_id32
	try:
		dota2_profile = urllib2.urlopen("https://api.opendota.com/api/players/" + steam_id32)
	except urllib2.HTTPError, e:
		print steam_id32 + " request_error"
		return "request_error"
	
	dota2_profile = json.loads(dota2_profile.read()) 
	
	if "profile" not in dota2_profile:
		print steam_id32 + " id_not_exist"
		return "id_not_exsit"
	
	new_user.steam_id64 = dota2_profile["profile"]["steamid"]
	new_user.avatar_full = dota2_profile["profile"]["avatarfull"]
	new_user.avatar_medium = dota2_profile["profile"]["avatarmedium"]
	new_user.personaname = dota2_profile["profile"]["personaname"]
	new_user.name = dota2_profile["profile"]["name"]
	new_user.exist = "OK"
	
	# get friends
	try:
		friends = urllib2.urlopen("http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key="+ steam_key + "&steamid=" + new_user.steam_id64 + "&relationship=friend")
	except urllib2.HTTPError, e:
		print steam_id32 + " friends request_error"
		return "request_error"
	
	friends = json.loads(friends.read())
	
	if "friendslist" in friends:
		for x in friends["friendslist"]["friends"]:
			#print x["steamid"]
			new_user.friends.append(x["steamid"])
	
	profile_map[steam_id32] = new_user
	save_obj(profile_map, "profile_map")
	return "OK"

#------------------------------------------------------------

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/query')
def query():
	global profile_map
	steam_id32 = request.args.get('x', 0, type=int)

	if len(profile_map) == 0 and os.path.isfile('obj/profile_map.pkl'):
		profile_map = load_obj("profile_map")

	print "1"

	if steam_id32 not in profile_map:
		res = get_profile(str(steam_id32))
		if res != "OK":
			return jsonify(result = res)

	print "2"

	profile_obj = profile_map[str(steam_id32)]
	return jsonify(result = profile_obj.exist,
				   img_url = profile_obj.avatar_full,
				   name = profile_obj.name,
				   personaname = profile_obj.personaname,
				   tags = profile_obj.tags)
	

@app.route('/json')
def graph_json():
	global SITE_ROOT
	json_url = os.path.join(SITE_ROOT, "json", "graph.json")
	json_data = json.load(open(json_url))
	print json_data
	return jsonify(json_data)






