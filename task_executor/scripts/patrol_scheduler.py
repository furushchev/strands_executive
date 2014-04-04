#!/usr/bin/env python

import rospy

from strands_executive_msgs.msg import Task
from strands_executive_msgs.srv import AddTask, SetExecutionStatus
from std_msgs.msg import String
from random import shuffle


class PatrolScheduler(object):

	def __init__(self):
		self.waypoints = ['WayPoint1', 'WayPoint2', 'WayPoint3']
		self.current_waypoint = ''
		self.add_task_srv = None
		rospy.Subscriber("/current_node", String, self.current_node_cb)
		
		add_task_srv_name = '/task_executor/add_task'
		set_exe_stat_srv_name = '/task_executor/set_execution_status'
		rospy.loginfo("Waiting for task_executor service...") 
		rospy.wait_for_service(add_task_srv_name) 
		rospy.wait_for_service(set_exe_stat_srv_name) 
		rospy.loginfo("Done") 
		self.add_task_srv = rospy.ServiceProxy(add_task_srv_name, AddTask) 
		set_execution_status_srv = rospy.ServiceProxy(set_exe_stat_srv_name, SetExecutionStatus)
		
		shuffle(self.waypoints) 
		self.send_tasks() 

		try: 
			# Make sure the task executor is running 
			set_execution_status_srv(True) 
		except rospy.ServiceException, e: 
			print "Service call failed: %s"%e

	def send_tasks(self): 
		rospy.loginfo("Sending next batch of patrol tasks")
		for wp in self.waypoints:
			self.add_task_srv(Task(node_id=wp))
	

	def current_node_cb(self, data):
	
		# if we have just changed nodes 
		if self.current_waypoint != data.data: 
			rospy.loginfo("Changed nodes to %s from %s" % (data.data, self.current_waypoint))
	    	self.current_waypoint = data.data
	    	# if we're on the last waypoint, send the tasks again
	    	if self.current_waypoint == self.waypoints[-1]:
	    		shuffle(self.waypoints) 
	    		self.send_tasks()

			




if __name__ == '__main__':
    rospy.init_node("patrol_scheduler")
    
    patrol_scheduler = PatrolScheduler()

    rospy.spin()


