import numpy as np
import math

class View():
	#Handles the viewing of the data points in 3d space
	def __init__(self):
		self.vrp = np.matrix('0.5,0.5,1') #Simply initialises all the fields
		self.vpn = np.matrix([0,0,-1])
		self.vup = np.matrix([0,1,0])
		self.u = np.matrix([-1,0,0])
		self.extent = np.matrix([1,1,1])
		self.screen = np.matrix([400,400])
		self.offset = np.matrix([20,20])
		self.vtm = self.build()

	def build(self):
		#builds the initial view object
		vtm = np.identity(4,float)
		t1 = np.matrix( [[1,0,0,-self.vrp[0,0]], #translation 1
						 [0,1,0,-self.vrp[0,1]],
						 [0,0,1,-self.vrp[0,2]],
						 [0,0,0,1]]
		)
		vtm = t1*vtm #translation

		tu = np.cross(self.vup, self.vpn) #find the cross products
		tvup = np.cross(self.vpn, tu)
		tvpn = self.vpn.copy()

		self.u = self.normalize(tu) #normalize
		self.vup = self.normalize(tvup)
		self.vpm = self.normalize(tvpn)

		# align the axes
		r1 = np.matrix( [[ tu[0, 0], tu[0, 1], tu[0, 2], 0.0 ],
							[ tvup[0, 0], tvup[0, 1], tvup[0, 2], 0.0 ],
							[ tvpn[0, 0], tvpn[0, 1], tvpn[0, 2], 0.0 ],
							[ 0.0, 0.0, 0.0, 1.0 ] ] )

		vtm = r1 * vtm #update the vtm

		extentScaling = np.matrix (  #scale to size of zoom level
			[[1,0,0,0.5*self.extent[0,0]],
			[0,1,0,0.5*self.extent[0,1]],
			[0,0,1,0],
			[0,0,0,1]]
		)
		vtm = extentScaling * vtm #update vtm

		scaleScreen = np.matrix( [[-self.screen[0,0]/self.extent[0,0],0.0,0.0,0.0], #scale to fit on current screen
							[0.0,-self.screen[0,1]/self.extent[0,1],0.0,0.0],
							[ 0.0, 0.0, 1.0, 0.0],
							[ 0.0, 0.0, 0.0, 1.0 ] ] )
		vtm = scaleScreen * vtm #update vtm

		movingUp = np.matrix( [[1,0,0,self.screen[0,0]+ self.offset[0,0]], #translate back up from negative space
							[0.0,1.0,0,self.screen[0,1]+ self.offset[0,1]],
							[ 0.0, 0.0, 1.0, 0.0],
							[ 0.0, 0.0, 0.0, 1.0 ] ] )
		vtm = movingUp * vtm #update vtm
		return vtm

	def rotateVRC(self, rVUP, rU):
		#rotates the view object
		t1 = np.matrix([
		[1,0,0,-(self.vrp[0,0] + self.vpn[0,0] * self.extent[0,2]*0.5)],
		[0,1,0,-(self.vrp[0,1] + self.vpn[0,1] * self.extent[0,2]*0.5)],
		[0,0,1,-(self.vrp[0,2] + self.vpn[0,2] * self.extent[0,2]*0.5)],
		[0,0,0,1]
		]) #translation matrix

		Rxyz = np.matrix([[self.u[0,0],self.u[0,1],self.u[0,2],0], #axis alignment matrix
					[self.vup[0,0],self.vup[0,1],self.vup[0,2],0],
					[self.vpn[0,0],self.vpn[0,1],self.vpn[0,2],0],
					[0,0,0,1]])
		r1 = np.matrix([ #Rotation around the y axis
			[math.cos(rVUP),0,math.sin(rVUP),0],
			[0,1,0,0],
			[-math.sin(rVUP),0,math.cos(rVUP),0],
			[0,0,0,1]
		])
		r2 = np.matrix([ #Rotation around the x axis
			[1,0,0,0],
			[0,math.cos(rU),-math.sin(rU),0],
			[0,math.sin(rU),math.cos(rU),0],
			[0,0,0,1]
		])
		t2 = np.matrix([ #untranslation matrix
		[1,0,0,(self.vrp[0,0] + self.vpn[0,0] * self.extent[0,2]*0.5)],
		[0,1,0,(self.vrp[0,1] + self.vpn[0,1] * self.extent[0,2]*0.5)],
		[0,0,1,(self.vrp[0,2] + self.vpn[0,2] * self.extent[0,2]*0.5)],
		[0,0,0,1]
		])
		 #translation matrix
		tvrc = np.matrix ([
		[self.vrp[0,0],self.vrp[0,1],self.vrp[0,2],1],
		[self.u[0,0],self.u[0,1],self.u[0,2],0],
		[self.vup[0,0],self.vup[0,1],self.vup[0,2],0],
		[self.vpn[0,0],self.vpn[0,1],self.vpn[0,2],0]
		])

		tvrc = (t2*Rxyz.transpose()*r2*r1*Rxyz*t1*tvrc.transpose()).transpose() #tvrc ==> product

		self.vrp = np.matrix (tvrc[0,:3]) #updates fields of object
		self.u = self.normalize(tvrc[1,:3]) #normalizes and updates the field
		self.vup = self.normalize(tvrc[2,:3])
		self.vpn = self.normalize(tvrc[3,:3])


	def normalize(self, V):
		#V is a numpy matrix
		length = math.sqrt(V[0,0]*V[0,0] + V[0,1]*V[0,1]  + V[0,2]*V[0,2] )
		vnorm = V/length #divides matrix by the distance
		return vnorm

	def clone(self):
		#creates a clone of the view object
		copy = View()
		copy.vrp = self.vrp.copy()
		copy.vpn = self.vpn.copy()
		copy.vup = self.vup.copy()
		copy.u = self.u.copy()
		copy.extent = self.extent.copy()
		copy.screen = self.screen.copy()
		copy.offset = self.offset.copy()
		return copy

	def reset(self):
		#resets the view object to original position
		self.vrp = np.matrix('0.5,0.5,1')
		self.vpn = np.matrix([0,0,-1])
		self.vup = np.matrix([0,1,0])
		self.u = np.matrix([-1,0,0])
		self.extent = np.matrix([1,1,1])
		self.screen = np.matrix([400,400])
		self.offset = np.matrix([20,20])
		self.vtm = self.build()


if __name__ == "__main__":
    vapp = View()
	# print vapp.clone()
