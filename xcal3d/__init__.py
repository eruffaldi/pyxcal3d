#
# 
#
#
import xml.sax
import numpy
import bisect

def str2vec(y):
	return numpy.array([float(x) for x in y.split(" ")],dtype="float32")

def str2ivec(y):
	return numpy.array([int(x) for x in y.split(" ")],dtype="int32")

def vec2str(y):
	return " ".join([str(x) for x in y])

#<MATERIAL VERSION="1100" NUMMAPS="2">
#    <AMBIENT>0 0 0 0</AMBIENT>
#    <DIFFUSE>0 0 0 255</DIFFUSE>
#    <SPECULAR>229 229 229 0</SPECULAR>
#   <SHININESS>0</SHININESS>
##    <MAP>m014_opacity_color.tga</MAP>
#    <MAP>m014_opacity_color.tga</MAP>
#</MATERIAL>


class Config:
	def __init__(self):
		self.values = dict()
		self.materials = []

class ConfigParser:
	def __init__(self,target=None):
		if target is None:
			target = Config()
		self.target = target
	def load(self,source):
		for line in source:
			line = line.strip()
			if len(line) == 0 or line[0] == "#":
				continue
			name,value = line.split("=",1)
			if name == "material":
				self.target.materials.append(value)
			else:
				self.target.values[name] = value
		return self.target
class Material:
	def __init__(self):
		self.maps = []
		self.shininess = 0
		self.ambient = None
		self.diffuse = None
		self.specular = None

class MaterialParser(xml.sax.ContentHandler):
	def __init__(self,target=None):
		xml.sax.ContentHandler.__init__(self)
		if target is None:
			target = Material()
		self.target = target
		self.lastin = ""
		self.body = ""
	def load(self,source):
		xml.sax.parse(source, self)
		return self.target

	def startElement(self, name, attrs):
		if name == "AMBIENT" or name == "DIFFUSE" or name == "SPECULAR" or name == "SHININESS" or name == "MAP":
			self.lastin = name
			self.body = ""
		else:
			self.body = ""
			self.lastin= ""

	def endElement(self, name):
		content = self.body.strip()
		if self.lastin == "MAP":
			if content == "<none>":
				content = ""
			self.target.maps.append(content)
		elif self.lastin == "SHININESS":
			self.target.shininess = float(content)
		elif self.lastin != "":
			setattr(self.target,self.lastin.lower(),str2vec(content))
		self.lastin = ""

	def characters(self, content):
		self.body += content


#<ANIMATION VERSION="1100" DURATION="42.1333" NUMTRACKS="82">
#    <TRACK BONEID="0" NUMKEYFRAMES="1265">
#        <KEYFRAME TIME="0">
#            <TRANSLATION>0 -1.18448e-015 -2.70976e-008</TRANSLATION>
#            <ROTATION>0 0.707106 -3.09086e-008 0.707107</ROTATION>
#        </KEYFRAME>
class AnimFrame:
	def __init__(self):
		self.pos = None
		self.quat = None
		self.time = 0

class Track:
	def __init__(self):
		self.boneid = 0
		#self.nkeyframes = 0
		self.frames = []
		self.times = []
	@property
	def timeStep(self):
		if len(self.frames) > 1:
			return self.times[1]-self.times[0]
	@property
	def framesCount(self):
		return len(self.frames)
	def findnearestframe(self,t):
		if t < self.times[0] or t > self.times[-1]:
			return None
		i = bisect.bisect_right(self.times, t)
		if i:
			return i-1
		else:
			return None

# TODO: http://docs.python.org/2/library/bisect.html
class Animation:
	def __init__(self):
		self.duration = 0
		#self.ntracks = 0
		self.tracks = []
	@property
	def affectedbones(self):
		return [x.boneid for x in self.tracks]

	@property
	def timeStep(self):
		if len(self.tracks) > 0:
			return self.tracks[0].timeStep
		else:
			return 1000000
	@property
	def tracksCount(self):
		return len(self.tracks)
	def save(self,of):
		of.write("""<ANIMATION VERSION="1100" DURATION="%f" NUMTRACKS="%d">\n""" % (self.duration,len(self.tracks)))
		for t in self.tracks:
			of.write("""\t<TRACK BONEID="%d" NUMKEYFRAMES="%d">\n""" % (t.boneid,len(t.frames)))
			for f in t.frames:
				of.write("""\t\t<KEYFRAME TIME="%f">\n""" % f.time)
				if f.pos:
					of.write("""\t\t\t<TRANSLATION>%s</TRANSLATION>\n""" % vec2str(f.pos))
				if f.quat:
					of.write("""\t\t\t<ROTATION>%s</ROTATION>\n""" % vec2str(f.quat))
				of.write("""\t\t</KEYFRAME>\n""")
			of.write("""\t</TRACK>""")
		of.write("""</ANIMATION>""")

class AnimationParser(xml.sax.ContentHandler):
	def __init__(self,target=None):
		xml.sax.ContentHandler.__init__(self)
		if target is None:
			target = Animation()
		self.target = target
		self.track = None
		self.lastin = ""
		self.frame = None
	def load(self,source):
		xml.sax.parse(source, self)
		return self.target
	def startElement(self, name, attrs):
		if name == "ANIMATION":
			self.target.duration = float(attrs.getValue("DURATION"))
			self.target.ntracks = int(attrs.getValue("NUMTRACKS"))
		elif name == "TRACK":
			self.track = Track()
			self.target.tracks.append(self.track)
			self.track.boneid = int(attrs.getValue("BONEID"))
			#self.track.nkeyframes = int(attrs.getValue("NUMKEYFRAMES"))
		elif name == "KEYFRAME":
			t = float(attrs.getValue("TIME"))
			self.frame = AnimFrame()
			self.frame.time = t
			self.track.frames.append(self.frame)
			self.track.times.append(t)
		elif name == "TRANSLATION":
			self.lastin = name
		elif name == "ROTATION":
			self.lastin = name
		self.ctext = ""

	def endElement(self, name):
		content = self.ctext
		self.ctext = ""
		if self.lastin == "TRANSLATION":
			v = str2vec(content)
			self.frame.pos = v
		elif self.lastin == "ROTATION":
			v = str2vec(content)
			self.frame.quat = v
		self.lastin = ""

	def characters(self, content):
		self.ctext = self.ctext + content

#<MESH VERSION="1100" NUMSUBMESH="3">
#    <SUBMESH NUMVERTICES="2553" NUMFACES="4022" MATERIAL="0" NUMLODSTEPS="0" NUMSPRINGS="0" NUMTEXCOORDS="3">
#        <VERTEX ID="0" NUMINFLUENCES="2">
#            <POS>-0.16154 -0.225337 0.0354975</POS>
#           <NORM>-0.972743 -0.0846959 0.215866</NORM>
#           <TEXCOORD>0.145743 0.156416</TEXCOORD>
#            <TEXCOORD>0.145743 0.156416</TEXCOORD>
#            <TEXCOORD>0.145743 0.156416</TEXCOORD>
#            <INFLUENCE ID="118">0.9</INFLUENCE>
#            <INFLUENCE ID="2">0.1</INFLUENCE>
#        <FACE VERTEXID="0 1 2" />

class Vertex:
	def __init__(self):
		self.pos = None
		self.normal = None
		self.texcoords = []
		self.influences = [] # b,w
		self.id = 0

class Mesh:
	def __init__(self,name=""):
		self.name = name
		self.children = []
		self.nvtxs = 0
		self.nfaces = 0
		self.numtexcoords = 0
		self.material = 0
		self.numlodsteps = 0
		self.numsprings = 0
		self.vertices = []
		self.faces = [] # array of tuples of vertices
		self.maxinfluence = -1
		self.bones = None
	def computestats(self):
		bi = set()
		mi = -1
		for v in self.vertices:
			mi = max(len(v.influences),mi)
			for b,w in v.influences:
				bi.add(b)
		self.bones = bi
		self.maxinfluence = mi
	def limitinfuence(self,n):
		print "limitinfluence NOT IMPLEMENTED"
	def save(self,of,top=1):
		if top:
			of.write("""<MESH VERSION="1100" NUMSUBMESH="%d">\n""" % len(self.children))
			for m in self.children:
				m.save(of,top=0)
			of.write("</MESH>\n")
		else:
			m = self
			of.write("""\t<SUBMESH NUMVERTICES="%d" NUMFACES="%d" MATERIAL="%d" NUMLODSTEPS="0" NUMSPRINGS="0" NUMTEXCOORDS="%d">\n"""
				% (len(m.vertices),len(m.faces),m.material,m.numtexcoords))
			for v in self.vertices:
				of.write("""\t\t<VERTEX ID="%d" NUMINFLUENCES="%d">\n""" % (v.id,len(v.influences)))
				# pos
				of.write("\t\t\t<POS>" + vec2str(v.pos) +"</POS>\n")
				if v.norm is not None:
					of.write("\t\t\t<NORM>" + vec2str(v.norm) +"</NORM>\n")					
				for t in v.texcoords:
					of.write("\t\t\t<TEXCOORD>" + vec2str(t) +"</TEXCOORD>\n")					
				for ii in v.influences:
					of.write("\t\t\t<INFLUENCE ID=\"%d\">%f</INFLUENCE>\n" % (ii[0],ii[1] ))
				of.write("""\t\t</VERTEX>\n""")
			for f in self.faces:
				of.write("""\t\t<FACE VERTEXID="%s"/>\n""" % vec2str(f))
			of.write("""\t</SUBMESH>\n""")

vertexsub = set(["POS","NORM","TEXCOORD","INFLUENCE"])
class ModelParser(xml.sax.ContentHandler):
	def __init__(self,target=None):
		xml.sax.ContentHandler.__init__(self)
		if target is None:
			target = Mesh()
		self.target = target
		self.sub = None
		self.lastin = ""
		self.vid = 0
		self.ninf = 0
		self.infid = 0
		self.vtx = None
		self.ctext = ""
	def load(self,source):
		xml.sax.parse(source, self)
		return self.target
	def startElement(self, name, attrs):
		if name == "MESH":
			pass
		elif name == "SUBMESH":
			self.sub = Mesh()
			self.target.children.append(self.sub)
			for x in attrs.getNames():
				setattr(self.sub,x.lower(),int(attrs.getValue(x)))
		elif name == "VERTEX":
			vid = int(attrs.getValue("ID"))
			self.ninf = int(attrs.getValue("NUMINFLUENCES"))
			self.lastin = name
			self.vtx = Vertex()
			self.vtx.id = vid
			self.sub.vertices.append(self.vtx)
		elif name == "INFLUENCE":
			self.infid = int(attrs.getValue("ID"))
			self.lastin = name
		elif name == "FACE":
			ff = str2ivec(attrs.getValue("VERTEXID"))
			self.sub.faces.append(ff)
		elif name in vertexsub:
			self.lastin = name
		else:
			print "unknown start",name
		self.ctext = ""

	def endElement(self, name):
		content = self.ctext
		if self.lastin == "POS":
			self.vtx.pos = str2vec(content)
		elif self.lastin == "NORM":
			self.vtx.normal = str2vec(content)
		elif self.lastin == "TEXCOORD":
			self.vtx.texcoords.append(str2vec(content))
		elif self.lastin == "INFLUENCE":
			self.vtx.influences.append((self.infid,float(content)))
		self.lastin = ""

	def characters(self, content):
		self.ctext = 		self.ctext + content

class Bone:
	def __init__(self,id,name):
		self.id = id
		self.parent = None
		self.pid = -1
		self.name = name
		self.children = []
		self.tx = None
		self.rot = None
		self.localtx = None
		self.localrot = None

class Skeleton:
	def __init__(self):
		self.bones = {}
	def findbone(self,name):
		for x in self.bones.values():
			if name == x.name:
				return x.id
		return None
	def findbonesbelow(self,x):
		todo = [x]
		out = []
		while len(todo) > 0:
			top = todo[0]
			todo = todo[1:]
			btop = self.bones[top]
			for c in btop.children:
				out.append(c)
				todo.append(c)
		return out





#<SKELETON VERSION="1100" NUMBONES="123">
#    <BONE ID="0" NAME="Bip01" NUMCHILDS="2">
#        <TRANSLATION>0 -1.18448e-015 -2.70976e-008</TRANSLATION>
#        <ROTATION>0 0.707106 -3.09086e-008 0.707107</ROTATION>
#        <LOCALTRANSLATION>2.70976e-008 1.62381e-021 3.71483e-014</LOCALTRANSLATION>
#        <LOCALROTATION>0 -0.707106 3.09086e-008 0.707107</LOCALROTATION>
#        <PARENTID>-1</PARENTID>
#        <CHILDID>1</CHILDID>
#        <CHILDID>2</CHILDID>
#    </BONE>

bonesub = set(["TRANSLATION","ROTATION","LOCALROTATION","LOCALTRANSLATION","PARENTID","CHILDID"])
class SkelParser(xml.sax.ContentHandler):
	def __init__(self,target=None):
		xml.sax.ContentHandler.__init__(self)
		if target is None:
			target = Skeleton()
		self.target = target
		self.nbones = 0
		self.version = ""
		self.current = ""
		self.children = []
		self.bone = None
		self.lastin = ""

	def load(self,source):
		xml.sax.parse(source, self)
		return self.target

	def startElement(self, name, attrs):
		if name == "SKELETON":
			self.nbones = int(attrs.getValue("NUMBONES"))
			self.version = attrs.getValue("VERSION")
		elif name == "BONE":
			id = int(attrs.getValue("ID"))
			name = attrs.getValue("NAME")
			nc = int(attrs.getValue("NUMCHILDS"))
			self.bone = Bone(id,name)
			self.target.bones[id] = self.bone
		elif name in bonesub:
			self.current = name


		self.lastin = name
		self.ctext = ""
		if name == "address":
			print("\tattribute type='" + attrs.getValue("type") + "'")

	def endElement(self, name):
		content = self.ctext
		self.ctext = ""
		if name ==" SKELETON":
			# finished
			for b in self.target.bones.items():
				for c in b.children:
					self.target.bones[c].parent = b
		elif self.lastin == "TRANSLATION":
			self.bone.tx = str2vec(content)
		elif self.lastin == "LOCALTRANSLATION":
			self.bone.localtx = str2vec(content)
		elif self.lastin == "ROTATION":
			self.bone.rot = str2vec(content)
		elif self.lastin == "LOCALROTATION":
			self.bone.localrot = str2vec(content)
		elif self.lastin == "CHILDID":
			self.bone.children.append(int(content))
		elif self.lastin == "PARENTID":
			self.bone.pid = int(content)
			if self.bone.pid in self.target.bones:
				self.bone.parent = self.target.bones[self.bone.pid]
		elif len(content.strip()) > 0:
			print "unexpeced char",self.lastin
		self.lastin = ""

	def characters(self, content):
		self.ctext = 		self.ctext + content

