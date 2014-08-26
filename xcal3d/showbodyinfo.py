from xcal3d import *
import numpy



if __name__ == "__main__":
	import sys
	import os

	f = sys.argv[1]
	ext = os.path.splitext(f)[1]

	if ext != ".xsf":
		print "unsupported skeleton file, only xsf"
	source = open(f,"rb")
	pa = SkelParser()
	xml.sax.parse(source, pa)
	sk = pa.target


	db = dict([(b.name,b) for b in sk.bones.values()])
	
	prefix = "Bip01 "
	names = ["Spine","R Thigh","R Calf","R Foot"]
	bones = [db[prefix+x] for x in names]
	print "\n".join(["%s <- %s" %(x.name,x.parent is not None and x.parent.name or "<none>") for x in bones])

	for x in db.values():
		if x.parent == bones[-1]:
			print "children of foot:",x.name

	poses = [numpy.array(x.tx)  for x in bones]
	distances = [numpy.linalg.norm(poses[i]-poses[i-1]) for i in range(1,len(poses))]
	print "distances",distances
	deltas = "\n".join(["%s:%s" % (bones[i].name,str(poses[i]-poses[i-1])) for i in range(1,len(poses))])
	print deltas


