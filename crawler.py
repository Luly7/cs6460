"""
Crawler Robot Environment and Robot Implementation for Reinforcement Learning

This module provides a complete implementation of a 2-joint robotic crawler and its
reinforcement learning environment. The robot learns to move forward efficiently by
coordinating its arm and hand joint movements.

Key Components:
- CrawlingRobotEnvironment: RL environment wrapper that:
  * Discretizes continuous joint angles into state buckets
  * Defines legal actions for joint movements
  * Calculates rewards based on forward progress
  * Handles state transitions and episode termination

- CrawlingRobot: Physical robot implementation with:
  * Configurable arm and hand segments with angle constraints
  * Forward kinematics for position tracking
  * Collision detection with ground plane
  * Real-time visualization of robot state and metrics
  * Methods for controlling individual joints

Changes in this version:
- Verified compatibility with Python 3.13
- Improved docstring organization and clarity
- Added detailed component descriptions
- Updated formatting for better readability

Originally based on Berkeley CS188 crawler robot implementation
Modified for use in USAFA CS330 course

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

# Original crawler robot implementation from UC Berkeley CS188 Pacman Projects
# http://ai.berkeley.edu/reinforcement.html
# Attribution: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import math
from math import pi as PI
import time
import environment
import random
from typing import Tuple, List, Optional, Any, Union, Dict

class CrawlingRobotEnvironment(environment.Environment):
    """
    Environment wrapper for crawler robot that implements RL environment interface.
    
    The environment discretizes the continuous state space of arm and hand angles
    into buckets. States are represented as (armBucket, handBucket) tuples.
    Actions are discrete movements of either the arm or hand up/down.
    Rewards are based on forward movement of the robot.

    Attributes:
        crawlingRobot: CrawlingRobot instance used in environment
        state: Current state tuple of (armBucket, handBucket) 
        nArmStates: Number of discrete arm angle buckets
        nHandStates: Number of discrete hand angle buckets
        armBuckets: List of discretized arm angles
        handBuckets: List of discretized hand angles
    """

    def __init__(self, crawlingRobot: 'CrawlingRobot') -> None:
        """
        Initialize environment with given robot instance.
        
        Args:
            crawlingRobot: CrawlingRobot instance to use in environment
            
        Initializes state space discretization by creating angle buckets and
        setting initial state to middle bucket values.
        """
        self.crawlingRobot = crawlingRobot

        # The state is of the form (armAngle, handAngle)
        # where the angles are bucket numbers, not actual
        # degree measurements
        self.state: Optional[Tuple[int, int]] = None

        self.nArmStates = 9
        self.nHandStates = 13

        # create a list of arm buckets and hand buckets to
        # discretize the state space
        minArmAngle,maxArmAngle = self.crawlingRobot.getMinAndMaxArmAngles()
        minHandAngle,maxHandAngle = self.crawlingRobot.getMinAndMaxHandAngles()
        armIncrement = (maxArmAngle - minArmAngle) / (self.nArmStates-1)
        handIncrement = (maxHandAngle - minHandAngle) / (self.nHandStates-1)
        self.armBuckets = [minArmAngle+(armIncrement*i) \
           for i in range(self.nArmStates)]
        self.handBuckets = [minHandAngle+(handIncrement*i) \
         for i in range(self.nHandStates)]

        # Reset
        self.reset()

    def getCurrentState(self) -> Tuple[int, int]:
        """
        Return the current state of the crawling robot.
        
        Returns:
            Tuple of (armBucket, handBucket) representing current discretized state
            where each value is an integer index into the corresponding angle buckets
        """
        return self.state

    def getPossibleActions(self, state: Tuple[int, int]) -> List[str]:
        """
        Get valid actions for the given state.
        
        Args:
            state: Current state tuple of (armBucket, handBucket)
            
        Returns:
            List of valid action strings from: 'arm-up', 'arm-down', 'hand-up', 'hand-down'
            based on whether movements would exceed angle limits
        """
        actions = list()

        currArmBucket,currHandBucket = state
        if currArmBucket > 0: actions.append('arm-down')
        if currArmBucket < self.nArmStates-1: actions.append('arm-up')
        if currHandBucket > 0: actions.append('hand-down')
        if currHandBucket < self.nHandStates-1: actions.append('hand-up')

        return actions

    def doAction(self, action: str) -> Tuple[Tuple[int, int], float]:
        """
        Perform the action and update environment state.
        
        Args:
            action: Action string to execute ('arm-up', 'arm-down', 'hand-up', or 'hand-down')
            
        Returns:
            Tuple of (nextState, reward) where:
                nextState: Resulting state after action as (armBucket, handBucket)
                reward: Reward received for the transition (based on forward movement)
        """
        nextState, reward =  None, None

        oldX,oldY = self.crawlingRobot.getRobotPosition()

        armBucket,handBucket = self.state
        armAngle,handAngle = self.crawlingRobot.getAngles()
        if action == 'arm-up':
            newArmAngle = self.armBuckets[armBucket+1]
            self.crawlingRobot.moveArm(newArmAngle)
            nextState = (armBucket+1,handBucket)
        if action == 'arm-down':
            newArmAngle = self.armBuckets[armBucket-1]
            self.crawlingRobot.moveArm(newArmAngle)
            nextState = (armBucket-1,handBucket)
        if action == 'hand-up':
            newHandAngle = self.handBuckets[handBucket+1]
            self.crawlingRobot.moveHand(newHandAngle)
            nextState = (armBucket,handBucket+1)
        if action == 'hand-down':
            newHandAngle = self.handBuckets[handBucket-1]
            self.crawlingRobot.moveHand(newHandAngle)
            nextState = (armBucket,handBucket-1)

        newX,newY = self.crawlingRobot.getRobotPosition()

        # a simple reward function
        reward = newX - oldX

        self.state = nextState
        return nextState, reward


    def reset(self) -> None:
        """
        Reset environment to initial state.
        
        Sets state to middle bucket values and resets robot joint angles.
        The initial state is (nArmStates//2, nHandStates//2) to start
        in middle of state space.
        """
        ## Initialize the state to be the middle
        ## value for each parameter e.g. if there are 13 and 19
        ## buckets for the arm and hand parameters, then the intial
        ## state should be (6,9)
        ##
        ## Also call self.crawlingRobot.setAngles()
        ## to the initial arm and hand angle

        armState = self.nArmStates//2
        handState = self.nHandStates//2
        self.state = armState,handState
        self.crawlingRobot.setAngles(self.armBuckets[armState],self.handBuckets[handState])
        self.crawlingRobot.positions = [20,self.crawlingRobot.getRobotPosition()[0]]


class CrawlingRobot:
    """
    Implementation of 2-joint robotic crawler with arm and hand segments.
    
    The robot consists of:
    - A body segment that can rotate relative to ground
    - An arm segment that can rotate within angle bounds relative to body
    - A hand segment that can rotate within angle bounds relative to arm
    
    The robot maintains its position and can detect collisions with ground.
    Movement is achieved by coordinated rotation of arm and hand joints.
    
    Attributes:
        canvas: Drawing canvas for visualization
        armAngle: Current arm angle in radians
        handAngle: Current hand angle in radians 
        robotPos: Current (x,y) position of robot base
        positions: List tracking historical x positions
        velAvg: Moving average of velocity
    """

    def setAngles(self, armAngle: float, handAngle: float) -> None:
        """
        Set the robot's arm and hand angles to the passed in values.
        
        Args:
            armAngle: New arm angle in radians relative to body
            handAngle: New hand angle in radians relative to arm
        """
        self.armAngle = armAngle
        self.handAngle = handAngle

    def getAngles(self) -> Tuple[float, float]:
        """
        Get the current arm and hand angles.
        
        Returns:
            Tuple of (armAngle, handAngle) in radians representing current joint angles
        """
        return self.armAngle, self.handAngle

    def getRobotPosition(self) -> Tuple[float, float]:
        """
        Get the robot's current position.
        
        Returns:
            Tuple of (x,y) coordinates of the lower-left point of the robot body
        """
        return self.robotPos

    def moveArm(self, newArmAngle: float) -> None:
        """
        Move the robot arm to the new angle.
        
        Args:
            newArmAngle: Target angle in radians to move arm to
            
        Raises:
            Exception: If target angle exceeds allowed bounds defined by
                      minArmAngle and maxArmAngle
        """
        oldArmAngle = self.armAngle
        if newArmAngle > self.maxArmAngle:
            raise Exception('Crawling Robot: Arm Raised too high. Careful!')
        if newArmAngle < self.minArmAngle:
            raise Exception('Crawling Robot: Arm Raised too low. Careful!')
        disp = self.displacement(self.armAngle, self.handAngle,
                                  newArmAngle, self.handAngle)
        curXPos = self.robotPos[0]
        self.robotPos = (curXPos+disp, self.robotPos[1])
        self.armAngle = newArmAngle

        # Position and Velocity Sign Post
        self.positions.append(self.getRobotPosition()[0])
#        self.angleSums.append(abs(math.degrees(oldArmAngle)-math.degrees(newArmAngle)))
        if len(self.positions) > 100:
            self.positions.pop(0)
 #           self.angleSums.pop(0)

    def moveHand(self, newHandAngle: float) -> None:
        """
        Move the robot hand to the new angle.
        
        Args:
            newHandAngle: Target angle in radians to move hand to
            
        Raises:
            Exception: If target angle exceeds allowed bounds defined by
                      minHandAngle and maxHandAngle
        """
        oldHandAngle = self.handAngle

        if newHandAngle > self.maxHandAngle:
            raise Exception('Crawling Robot: Hand Raised too high. Careful!')
        if newHandAngle < self.minHandAngle:
            raise Exception('Crawling Robot: Hand Raised too low. Careful!')
        disp = self.displacement(self.armAngle, self.handAngle, self.armAngle, newHandAngle)
        curXPos = self.robotPos[0]
        self.robotPos = (curXPos+disp, self.robotPos[1])
        self.handAngle = newHandAngle

        # Position and Velocity Sign Post
        self.positions.append(self.getRobotPosition()[0])
 #       self.angleSums.append(abs(math.degrees(oldHandAngle)-math.degrees(newHandAngle)))
        if len(self.positions) > 100:
            self.positions.pop(0)
 #           self.angleSums.pop(0)

    def getMinAndMaxArmAngles(self):
        """
            get the lower- and upper- bound
            for the arm angles returns (min,max) pair
        """
        return self.minArmAngle, self.maxArmAngle

    def getMinAndMaxHandAngles(self):
        """
            get the lower- and upper- bound
            for the hand angles returns (min,max) pair
        """
        return self.minHandAngle, self.maxHandAngle

    def getRotationAngle(self):
        """
            get the current angle the
            robot body is rotated off the ground
        """
        armCos, armSin = self.__getCosAndSin(self.armAngle)
        handCos, handSin = self.__getCosAndSin(self.handAngle)
        x = self.armLength * armCos + self.handLength * handCos + self.robotWidth
        y = self.armLength * armSin + self.handLength * handSin + self.robotHeight
        if y < 0:
            return math.atan(-y/x)
        return 0.0


    ## You shouldn't need methods below here


    def __getCosAndSin(self, angle: float) -> Tuple[float, float]:
        """
        Helper method to calculate cosine and sine of an angle.

        Args:
            angle: Angle in radians

        Returns:
            Tuple containing (cosine, sine) of the input angle
        """
        return math.cos(angle), math.sin(angle)

    def displacement(self, oldArmDegree: float, oldHandDegree: float, 
                    armDegree: float, handDegree: float) -> float:
        """
        Calculates the horizontal displacement of the robot between two configurations.

        This method computes how far the robot moves horizontally when transitioning
        from one set of arm/hand angles to another. It handles cases where the robot
        may be in contact with the ground in different ways during the transition.

        Args:
            oldArmDegree: Previous arm angle in radians
            oldHandDegree: Previous hand angle in radians  
            armDegree: New arm angle in radians
            handDegree: New hand angle in radians

        Returns:
            Float representing the horizontal displacement. Positive values indicate
            forward movement, negative values indicate backward movement.

        Raises:
            Exception: If an impossible configuration is encountered (should never happen)
        """
        oldArmCos, oldArmSin = self.__getCosAndSin(oldArmDegree)
        armCos, armSin = self.__getCosAndSin(armDegree)
        oldHandCos, oldHandSin = self.__getCosAndSin(oldHandDegree)
        handCos, handSin = self.__getCosAndSin(handDegree)

        xOld = self.armLength * oldArmCos + self.handLength * oldHandCos + self.robotWidth
        yOld = self.armLength * oldArmSin + self.handLength * oldHandSin + self.robotHeight

        x = self.armLength * armCos + self.handLength * handCos + self.robotWidth
        y = self.armLength * armSin + self.handLength * handSin + self.robotHeight

        if y < 0:
            if yOld <= 0:
                return math.sqrt(xOld*xOld + yOld*yOld) - math.sqrt(x*x + y*y)
            return (xOld - yOld*(x-xOld) / (y - yOld)) - math.sqrt(x*x + y*y)
        else:
            if yOld  >= 0:
                return 0.0
            return -(x - y * (xOld-x)/(yOld-y)) + math.sqrt(xOld*xOld + yOld*yOld)

        raise Exception('Never Should See This!')

    def draw(self, stepCount: int, stepDelay: float) -> None:
        """
        Draws the robot's current state on the canvas.
        
        Updates the visual representation of the robot body, arm and hand based on current angles
        and position. Also tracks movement metrics like position and velocity.

        Args:
            stepCount: Current step number in the simulation
            stepDelay: Time delay between steps in seconds

        Raises:
            Exception: If robot is not in contact with ground (y position invalid)
        """
        x1, y1 = self.getRobotPosition()
        x1 = x1 % self.totWidth

        ## Check Lower Still on the ground
        if y1 != self.groundY:
            raise Exception('Flying Robot!!')

        rotationAngle = self.getRotationAngle()
        cosRot, sinRot = self.__getCosAndSin(rotationAngle)

        x2 = x1 + self.robotWidth * cosRot
        y2 = y1 - self.robotWidth * sinRot

        x3 = x1 - self.robotHeight * sinRot
        y3 = y1 - self.robotHeight * cosRot

        x4 = x3 + cosRot*self.robotWidth
        y4 = y3 - sinRot*self.robotWidth

        self.canvas.coords(self.robotBody,x1,y1,x2,y2,x4,y4,x3,y3)

        armCos, armSin = self.__getCosAndSin(rotationAngle+self.armAngle)
        xArm = x4 + self.armLength * armCos
        yArm = y4 - self.armLength * armSin

        self.canvas.coords(self.robotArm,x4,y4,xArm,yArm)

        handCos, handSin = self.__getCosAndSin(self.handAngle+rotationAngle)
        xHand = xArm + self.handLength * handCos
        yHand = yArm - self.handLength * handSin

        self.canvas.coords(self.robotHand,xArm,yArm,xHand,yHand)


        # Position and Velocity Sign Post
#        time = len(self.positions) + 0.5 * sum(self.angleSums)
#        velocity = (self.positions[-1]-self.positions[0]) / time
#        if len(self.positions) == 1: return
        steps = (stepCount - self.lastStep)
        if steps==0:return
 #       pos = self.positions[-1]
#        velocity = (pos - self.lastPos) / steps
  #      g = .9 ** (10 * stepDelay)
#        g = .99 ** steps
#        self.velAvg = g * self.velAvg + (1 - g) * velocity
 #       g = .999 ** steps
 #       self.velAvg2 = g * self.velAvg2 + (1 - g) * velocity
        pos = self.positions[-1]
        velocity = pos - self.positions[-2]
        vel2 = (pos - self.positions[0]) / len(self.positions)
        self.velAvg = .9 * self.velAvg + .1 * vel2
        velMsg = f'100-step Avg Velocity: {self.velAvg:.2f}'
#        velMsg2 = '1000-step Avg Velocity: %.2f' % self.velAvg2
        velocityMsg = f'Velocity: {velocity:.2f}'
        positionMsg = f'Position: {pos:2.f}'
        stepMsg = f'Step: {stepCount}'
        if 'vel_msg' in dir(self):
            self.canvas.delete(self.vel_msg)
            self.canvas.delete(self.pos_msg)
            self.canvas.delete(self.step_msg)
            self.canvas.delete(self.velavg_msg)
 #           self.canvas.delete(self.velavg2_msg)
 #       self.velavg2_msg = self.canvas.create_text(850,190,text=velMsg2)
        self.velavg_msg = self.canvas.create_text(650,190,text=velMsg)
        self.vel_msg = self.canvas.create_text(450,190,text=velocityMsg)
        self.pos_msg = self.canvas.create_text(250,190,text=positionMsg)
        self.step_msg = self.canvas.create_text(50,190,text=stepMsg)
#        self.lastPos = pos
        self.lastStep = stepCount
#        self.lastVel = velocity

    def __init__(self, canvas):

        ## Canvas ##
        self.canvas = canvas
        self.velAvg = 0
#        self.velAvg2 = 0
#        self.lastPos = 0
        self.lastStep = 0
#        self.lastVel = 0

        ## Arm and Hand Degrees ##
        self.armAngle = self.oldArmDegree = 0.0
        self.handAngle = self.oldHandDegree = -PI/6

        self.maxArmAngle = PI/6
        self.minArmAngle = -PI/6

        self.maxHandAngle = 0
        self.minHandAngle = -(5.0/6.0) * PI

        ## Draw Ground ##
        self.totWidth = canvas.winfo_reqwidth()
        self.totHeight = canvas.winfo_reqheight()
        self.groundHeight = 40
        self.groundY = self.totHeight - self.groundHeight

        self.ground = canvas.create_rectangle(0,
            self.groundY,self.totWidth,self.totHeight, fill='blue')

        ## Robot Body ##
        self.robotWidth = 80
        self.robotHeight = 40
        self.robotPos = (20, self.groundY)
        self.robotBody = canvas.create_polygon(0,0,0,0,0,0,0,0, fill='green')

        ## Robot Arm ##
        self.armLength = 60
        self.robotArm = canvas.create_line(0,0,0,0,fill='orange',width=5)

        ## Robot Hand ##
        self.handLength = 40
        self.robotHand = canvas.create_line(0,0,0,0,fill='red',width=3)

        self.positions = [0,0]
  #      self.angleSums = [0,0]



if __name__ == '__main__':
    from graphicsCrawlerDisplay import *
    run()
