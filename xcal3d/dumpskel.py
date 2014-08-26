import xcal3d

def dump(o,b,s):
	print s,b.name,"#%d" % b.id
	for c in b.children:
		dump(o,o[c],s + "-")
if __name__ == "__main__":
	import sys
	import os

	f = sys.argv[1]
	ext = os.path.splitext(f)[1]

	if ext != ".xsf":
		print "not skel extension"
		sys.exit(0)

	pa = xcal3d.SkelParser()
	s = pa.load(open(f,"rb"))

	if len(sys.argv) == 3:
		for b in [x for x in s.bones.values() if x.pid == -1]:
			dump(s.bones,b,"")
	else:
		for b in s.bones.values():
			print b.id,b.pid,"\"%s\""%b.name,str(b.tx)[1:-1],str(b.rot)[1:-1],str(b.localtx)[1:-1],str(b.localrot)[1:-1]