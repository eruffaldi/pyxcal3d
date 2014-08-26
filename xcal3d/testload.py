from xcal3d import *

if __name__ == "__main__":
	import sys
	import os

	f = sys.argv[1]
	ext = os.path.splitext(f)[1]

	if ext == ".xaf":
		source = open(f,"rb")
		pa = AnimationParser()
		a = pa.load(source)
		allbones = set([t.boneid for t in a.tracks])
		if len(sys.argv) > 2 and sys.argv[2].endswith("xsf"):
			pa = SkelParser()
			m = pa.load(open(sys.argv[2],"rb"))
			print "\n".join([m.bones[i].name for i in allbones])
		else:
			print "bones:",allbones
	elif ext == ".xsf":
		source = open(f,"rb")
		pa = SkelParser()
		xml.sax.parse(source, pa)
		s = pa.target
		for b in s.bones.values():
			print b.name,b.tx	
		print "ready"
	elif ext == ".xmf":
		source = open(f,"rb")
		pa = ModelParser()
		xml.sax.parse(source, pa)
		print "ready"
	elif ext == ".xrf":
		source = open(f,"rb")
		pa = ModelParser()
		xml.sax.parse(source, pa)
		print "ready"
	else:
		print "unknown extension",ext 