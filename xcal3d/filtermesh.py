#
# Cal3d mesh filter by emanuele ruffaldi
#
#
#
import xcal3d
import sys

def allin(values,target):
	for v in values:
		if not v in target:
			return False
	return True

def partin(values,target):
	for v in values:
		if v in target:
			return True
	return False



if __name__ == "__main__":
	import sys
	import os

	if len(sys.argv) != 5:
		print "filtermesh skeleton meshin boneroot outmesh"
		sys.exit(0)

	fm = sys.argv[2]
	ext = os.path.splitext(fm)[1]
	if ext != ".xmf":
		print "not mesh extension"
		sys.exit(0)

	fs = sys.argv[1]
	ext = os.path.splitext(fs)[1]
	if ext != ".xsf":
		print "not skel extension"
		sys.exit(0)

	fom = sys.argv[4]
	ext = os.path.splitext(fom)[1]
	if ext != ".xmf":
		print "not mesh extension"
		sys.exit(0)

	print "parsing skel",fs
	pa = pyxcal3d.SkelParser()
	s = pa.load(open(fs,"rb"))

	id = s.findbone(sys.argv[3])
	print "target bone:",sys.argv[3],id
	goodbones = set(s.findbonesbelow(id))
	goodbones.add(id)
	print "selected bones",len(goodbones),"over",len(s.bones)
	
	print "parsing mesh",fm
	pa = pyxcal3d.ModelParser()
	sm = pa.load(open(fm,"rb"))

	# load mesh
	# remove all the vertices that are not influenced by bones in the set
	# save it again
	for m in sm.children:
		goodvertices = set()
		print "input vertices",len(m.vertices)
		for v in m.vertices:
			if partin([p[0] for p in v.influences],goodbones):
				goodvertices.add(v.id)

		print "\tselected vertices",len(goodvertices)

		# now select faces
		# NOTE: faces with any of the target face is candidate for future close
		goodfaces = []
		for f in m.faces:
			if allin(f,goodvertices):
				goodfaces.append(f)

		print "\tselected faces",len(goodfaces)
		# degenerate meshes
		if len(goodvertices) == 0 or len(goodfaces) == 0:
			print "removed mesh with ",len(m.vertices)
			m.vertices = []
			continue
		# renumber new vertices (DISTRUCTIVE)
		old2new = {}
		newvertices = []
		newv = 0		
		for oldv in goodvertices:
			v = m.vertices[oldv]
			old2new[oldv] = newv
			v.id = newv
			newvertices.append(v)
			newv = newv + 1
		# renumber good faces
		newfaces = []
		for f in goodfaces:
			newfaces.append(tuple([old2new[vi] for vi in f]))

		m.faces = newfaces
		m.vertices = newvertices
		print "final mesh",len(m.faces),len(m.vertices)
	sm.children = [m for m in sm.children if len(m.vertices) > 0]
	print "final meshes",len(sm.children)
	sm.save(open(fom,"wb"))