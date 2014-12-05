import xcal3d
import sys
import math

#import xml.etree.cElementTree as ET
import lxml.etree as ET


#Verify with: urdf_to_graphiz check_urdf
#https://github.com/ros/urdfdom for python parser

#From: https://github.com/ros/urdfdom_headers/blob/master/urdf_model/include/urdf_model/pose.h

def quat2mat(q):
	x,y,z,w = q

	mat = [[0,0,0] for i in range(0,3)]
	mat[0,0] = 1 - 2*y*y - 2*z*z;
	mat[1,0] = 2*x*y + 2*z*w;
	mat[2,0] = 2*x*z - 2*w*y;
	mat[0,1] = 2*y*x - 2*z*w;
	mat[1,1] = 1 - 2*x*x - 2*z*z;
	mat[2,1] = 2*z*y + 2*x*w;
	mat[0,2] = 2*x*z + 2*w*y;
	mat[1,2] = 2*z*y - 2*x*w;
	mat[2,2] = 1 - 2*x*x - 2*y*y;

def quat2rpy(q):
	x,y,z,w = q
	sqx = x * x;
	sqy = y * y;
	sqz = z * z;
	sqw = w * w;

	roll  = math.atan2(2 * (y*z + w*x), sqw - sqx - sqy + sqz);
	sarg = -2 * (x*z - w*y);

	#pitch = sarg <= -1.0 ? -0.5*M_PI : (sarg >= 1.0 ? 0.5*M_PI : asin(sarg));
	if sarg <= -1:
		pitch = -0.5*math.pi
	elif sarg >= 1.0:
		pitch = 0.5*math.pi
	else:
		pitch = math.acos(sarg)

	yaw   = math.atan2(2 * (x*y + w*z), sqw + sqx - sqy - sqz);
	return (roll,pitch,yaw)

def urdfrpy2quat(rpy):
	phi = rpy[0] / 2.0;
	the = rpy[1] / 2.0;
	psi = rpy[2] / 2.0;
	sin = math.sin
	cos = math.cos

	x = sin(phi) * cos(the) * cos(psi) - cos(phi) * sin(the) * sin(psi);
	y =cos(phi) * sin(the) * cos(psi) + sin(phi) * cos(the) * sin(psi);
	z =cos(phi) * cos(the) * sin(psi) - sin(phi) * sin(the) * cos(psi);
	w=cos(phi) * cos(the) * cos(psi) + sin(phi) * sin(the) * sin(psi);
	return (x,y,z,w)

if __name__ == "__main__":
	import sys
	import os

	if len(sys.argv) != 2:
		print "required input mesh"
		sys.exit(0)

	fm = sys.argv[1]
	ext = os.path.splitext(fm)[1]
	if ext.lower() != ".xsf":
		print "not skeleton extension"
		sys.exit(0)

	name = os.path.split(fm)[1]

	pa = xcal3d.SkelParser()
	s = pa.load(open(fm,"rb"))

	root = ET.Element("robot")
	root.set("name",name)


	doc = ET.SubElement(root, "doc")

	for b in s.bones.values():
		l = ET.SubElement(root,"link")
		l.set("name",b.name)
		l.set("index",str(b.id))
		ol = ET.SubElement(l,"vertexorigin")
		ol.set("xyz"," ".join([str(x) for x in b.localtx]))
		ol.set("rpy"," ".join([str(x) for x in quat2rpy(b.localrot)]))
		ol = ET.SubElement(l,"origin")
		ol.set("xyz"," ".join([str(x) for x in b.tx]))
		ol.set("rpy"," ".join([str(x) for x in quat2rpy(b.rot)]))

	for b in s.bones.values():
		if b.parent is not None:
			l = ET.SubElement(root,"joint")
			l.set("name",b.parent.name + "_" + b.name)
			l.set("type","floating")
			pl = ET.SubElement(l,"parent")
			pl.set("link",b.parent.name)
			cl = ET.SubElement(l,"child")
			cl.set("link",b.name)

	tree = ET.ElementTree(root)
	open(os.path.splitext(fm)[0]+".urdf","wb").write(ET.tostring(root,pretty_print=True))
	#tree.write(o[0] + ".urdf")

	"""	if len(sys.argv) == 3:
			for b in [x for x in s.bones.values() if x.pid == -1]:
				dump(s.bones,b,"")
		else:
			for b in s.bones.values():
				print b.id,b.pid,"\"%s\""%b.name,str(b.tx)[1:-1],str(b.rot)[1:-1],str(b.localtx)[1:-1],str(b.localrot)[1:-1]"""