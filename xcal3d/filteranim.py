import xcal3d
import sys

def allin(values,target):
	for v in values:
		if not v in target:
			return False
	return True

def number2seconds(x):
	a = x.split(":")
	if len(a) == 1:
		return float(a)
	else:
		return float(a[0])*60+float(b[0])

def newduration2seconds(x,ed):
	a = x.split(":")
	if len(a) == 1:
		a = a[0]
		if a.endswith("%"):
			return float(a[0:-1])*ed/100
		else:
			return float(a)
	else:
		return float(a[0])*60+float(b[0])



if __name__ == "__main__":
	import argparse
	import sys
	import os

	parser = argparse.ArgumentParser(description='CAL3D Animation Filter - 1.0 - Emanuele Ruffaldi 2013')
	parser.add_argument('--rootbone','-b', metavar='rootbone', default="",type=str, 	help='Bone to be added with its children (bone number or name)')
	parser.add_argument('--roothead',action="store_true")
	parser.add_argument('--starttime','-s', metavar='starttime', default="",type=str, 	help='Start time to be filtered (seconds or min:seconds, negative if with respect to end)')
	parser.add_argument('--endtime', '-e', metavar='endtime', default="",type=str, 	help='End time to be filtered (seconds or min:seconds, negative if with respect to end)')
	parser.add_argument('--duration', '-d',metavar='duration', default="",type=str, 	help='Duration to be taken (seconds or min:seconds)')
	parser.add_argument('--newduration','-D', metavar='newduration', default="100%",type=str, 	help='Duration to be rescaled (seconds or min:seconds or num%%)')
	parser.add_argument('--info',help="show input animation",action='store_true', default=False)
	parser.add_argument('inputskel', metavar='skeleton',type=str, 	help='Input skeleton xsf file')
	parser.add_argument('inputanim', metavar='inanimation',type=str, 	help='Input animation xaf file')
	parser.add_argument('outputanim', metavar='outanimation', type=str, help='Output animation xaf file')

	args = parser.parse_args()

	inputskel = args.inputskel
	inputanim = args.inputanim
	outputanim = args.outputanim
	if outputanim == "":
		outputanim,e = os.path.splitext(inputanim)
		outputanim = outputanim + "-f" + e

	starttime = 0
	endtime = None
	duration = None

	if args.starttime != "":
		starttime = number2seconds(args.starttime)
	if args.duration != "":
		duration = number2seconds(args.duration)
	if args.endtime != "":
		endtime = number2seconds(args.endtime)


	ext = os.path.splitext(inputskel)[1]
	if ext != ".xsf":
		print "not skel extension"
		sys.exit(0)

	ext = os.path.splitext(inputanim)[1]
	if ext != ".xaf":
		print "not anim extension"
		sys.exit(0)

	ext = os.path.splitext(outputanim)[1]
	if ext != ".xaf":
		print "not anim extension"
		sys.exit(0)

	print "loading skel"
	pa = xcal3d.SkelParser()
	s = pa.load(open(inputskel,"rb"))

	if args.roothead:
		args.rootbone = "Bip01 Head"
	if args.rootbone != "":
		try:
			id = int(args.rootbone)
		except:
			id = s.findbone(args.rootbone)
		goodbones = set(s.findbonesbelow(id))
		goodbones.add(id)
	else:
		goodbones = None
	
	print "loading anim"
	pa = xcal3d.AnimationParser()
	at = pa.load(open(inputanim,"rb"))

	if args.info:
		print "Duration:",at.duration
		print "Tracks:",len(at.tracks)
		bb = set([t.boneid for t in at.tracks])
		print "Bones:",",".join([s.bones[id].name for id in bb])
		sys.exit(0)

	cutmode = False
	if starttime < 0:
		starttime = at.duration+starttime
		cutmode = True
	if endtime is not None:
		cutmode = True
		if endtime < 0:
			endtime = at.duration+endtime
	elif duration is not None:
		cutmode = True
		endtime = starttime + duration
	else:
		endtime = starttime + at.duration

	print "cutting from ",starttime,"to",endtime,"as",endtime-starttime,"seconds"

	if args.newduration != "":
		newduration = newduration2seconds(args.newduration,at.duration)
		timescaling = newduration/at.duration
	else:
		newduration = 0

	print "from ",len(at.tracks),"tracks"
	if goodbones is not None:
		at.tracks = [t for t in at.tracks if t.boneid in goodbones]

	if cutmode:
		print "time cutting"
		# remove tracks that are before or after the requested interval
		at.tracks = [t for t in at.tracks if not (t.frames[-1].time < starttime or t.frames[0].time > endtime)]
		md = 0
		# then cut pieces
		for t in at.tracks:
			t.frames = [f for f in t.frames if f.time >= startime and f.time <= endtime] # WE COULD USE MONOTONY
			if starttime > 0:
				for f in t.frames:
					f.time = f.time - starttime # remove starting offset
			md = max(t.frames[-1].time,md) # compute new duration 
		at.duration = md

	if newduration > 0:
		print "rescaling time to new duration",newduration," from ",at.duration
		for t in at.tracks:
			for f in t.frames:
				f.time = f.time*timescaling
		at.duration = newduration


	print "to ",len(at.tracks),"tracks"
	at.save(open(outputanim,"wb"))
