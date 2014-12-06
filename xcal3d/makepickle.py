#
# Cal3d mesh filter by emanuele ruffaldi
#
#
#
import xcal3d
import sys
from array import array
import cPickle,numpy

def picklemesh(meshfilename,maxinfluence=4,maxtransforms=52,maxtexcoords=1):
	print "parsing mesh",fm
	pa = xcal3d.ModelParser()
	sm = pa.load(open(fm,"rb"))

	dd = []
	stride = maxtexcoords*2+3+3+maxinfluence*2
	for m in sm.children:
		m.computestats()
		print m.name,"vertices",len(m.vertices), "affected bones",len(m.bones),"maxinfluence",m.maxinfluence,"texcoords",m.numtexcoords

		if m.maxinfluence > maxinfluence:
			print "influence remap not implemented"
			sys.exit(-1)
			m.limitinfluence(maxinfluence)
		if len(m.bones) > maxtransforms:
			print "more bones than max -> FAIL"
		if len(m.bones) < 10:
			print "small bone ref:",m.bones
		if m.numtexcoords > maxtexcoords:
			print "more texcoord than max -> skip coords"

		bones = list(m.bones)
		oldbone2newbone = dict([(b,i) for i,b in enumerate(bones)])

		md = {}
		ad = []
		for v in m.vertices:
			ad.append(v.pos[0])
			ad.append(v.pos[1])
			ad.append(v.pos[2])
			ad.append(v.normal[0])
			ad.append(v.normal[1])
			ad.append(v.normal[2])
			ni = len(v.influences)
			# weights with pad to max
			for b,w in v.influences:
				ad.append(w)
			for i in range(ni,maxinfluence):
				ad.append(0)
			# bones with pad to max, added as RELATIVE
			for b,w in v.influences:
				ad.append(oldbone2newbone[b])
			for i in range(ni,maxinfluence):
				ad.append(0)
			if m.numtexcoords > 0:
				ad.append(v.texcoords[0][0])
				ad.append(v.texcoords[0][1])
			else:
				ad.append(0)
				ad.append(0)
		fd = []
		for f in m.faces:
			fd.append(f[0])
			fd.append(f[1])
			fd.append(f[2])
		md["vertices"] = numpy.array(ad,dtype="float32")
		md["faces"] = numpy.array(fd,dtype="int32")
		md["name"] = m.name
		md["numvertices"] = len(m.vertices)
		md["material"] = m.material
 		md["stride"] = stride
		md["numinfluences"] = maxinfluence
		md["numtexcoords"] = 1
		md["bones"] = bones
		md["layout"] = ["pos","norm","weights","rel_bones","texcoords"]
		print "dumping",len(ad),"vertexdata",len(ad)/len(m.vertices),"faces:",len(fd)
		dd.append(md)
	cPickle.dump(dd,open(meshfilename+".pik","wb"),2)
		# build array of all mesh information using standard layout

		# append this mesh to dd
	# store dd

if __name__ == "__main__":
	import sys
	import os

	if len(sys.argv) != 2:
		print "required input mesh"
		sys.exit(0)

	fm = sys.argv[1]
	ext = os.path.splitext(fm)[1]
	if ext != ".xmf":
		print "not mesh extension"
		sys.exit(0)

	picklemesh(fm)

