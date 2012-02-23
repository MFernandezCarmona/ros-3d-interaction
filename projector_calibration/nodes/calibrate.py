#!/usr/bin/env python
import roslib; roslib.load_manifest('projector_calibration')
from projector_calibration import CalibrationGrid
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import PySide
import sys
from functools import partial
import numpy as np
bridge = CvBridge()

import cv

image = None
calib_im = None

class Calibrator(object):
	def publish_image(self, grid_pub):
		im = self.grid.getPatternAsImage(im_type='OPENCV')

		msg = bridge.cv_to_imgmsg(self.removeAlpha(im), 'rgb8')
		msg.header.stamp = rospy.Time.now()
		grid_pub.publish(msg)

	def removeAlpha(self, im):
		r = cv.CreateMat(im.height, im.width, cv.CV_8UC1)
		g = cv.CreateMat(im.height, im.width, cv.CV_8UC1)
		b = cv.CreateMat(im.height, im.width, cv.CV_8UC1)
		cv.Split(im,r,g,b,None)
		imrgb = cv.CreateMat(im.height, im.width, cv.CV_8UC3)
		cv.Merge(r,g,b,None,imrgb)
		return imrgb

	def get_projector_grid(self):
		PySide.QtCore.QTimer.singleShot(0, self.grid, self.printhello)
	
	def printhello(self):
		print 'hello'
	
	def calibrate(self, e):
		print 'calibrate'
		# TODO wait until we can detect a checkerboard
		while not image:
			rospy.sleep(0.1)
			print 'waiting'
		print 'ready'
		# self.get_projector_grid()
		# print self.grid.getPatternAsImage(im_type='OPENCV')
		im1 = bridge.imgmsg_to_cv(image)
		im2 = self.removeAlpha(self.grid.getPatternAsImage(im_type='OPENCV'))
		corners1 = cv.FindChessboardCorners(im1, (self.grid.nRows-1, self.grid.nCols-1))
		corners2 = cv.FindChessboardCorners(im2, (self.grid.nRows-1, self.grid.nCols-1))
		
		import pprint
		f = cv.CreateMat(3, 3, cv.CV_32FC1)
		cv.FindFundamentalMat(cv.fromarray(np.array(corners1[1])), cv.fromarray(np.array(corners2[1])), f)
		pprint.pprint(np.asarray(f))
		
	def image_cb(self, msg):
		global image
		image = msg
	
	def __init__(self):
		rospy.init_node('grid')
		rospy.Subscriber('grid', Image, self.image_cb)
		grid_pub = rospy.Publisher('grid', Image)
		app = PySide.QtGui.QApplication(sys.argv)
		self.grid = CalibrationGrid()
		self.grid.addKeyHandler(67, self.calibrate)
		# self.grid.showFullScreen()
		timer = PySide.QtCore.QTimer(self.grid)
		self.grid.connect(timer, PySide.QtCore.SIGNAL('timeout()'), partial(self.publish_image, grid_pub))
		timer.start(100)
		sys.exit(app.exec_())

if __name__ == '__main__':
	Calibrator()