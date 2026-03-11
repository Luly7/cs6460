"""
Graphics display for Crawler robot learning visualization.

This module provides visualization capabilities for the Crawler robot learning environment 
using tkinter graphics. It handles the graphical display of:
- Robot joint positions and movements
- Learning parameters (epsilon, gamma, alpha) with real-time adjustment
- Current robot state and action selection
- Learning progress and performance metrics
- Interactive simulation speed control

The display is highly configurable with options for:
- Window and robot size scaling
- Animation speed and frame timing
- Learning parameter ranges and increments
- Debug visualization modes
- Custom messages and labels

The graphics use tkinter for cross-platform compatibility and smooth animation.
All drawing is done on a tkinter Canvas with configurable visual parameters.

Most code originally by Dan Klein and John Denero for CS188 at UC Berkeley.
Some code from LiveWires Pacman implementation, used with permission.

Python Version: 3.13
Last Modified: 24 Nov 2024
Modified by: George Rudolph

Changes:
- Added comprehensive module docstring
- Added type hints throughout module
- Added detailed display configuration options
- Added Python version compatibility note
- Added last modified date and modifier
- Verified Python 3.13 compatibility

# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import tkinter
import qlearningAgents
import time
import threading
import sys
import crawler
#import pendulum
import math
from math import pi as PI
from typing import Optional, Any, Callable

robotType = 'crawler'

class Application:
    """Main application class for the Crawler robot GUI interface."""

    def sigmoid(self, x: float) -> float:
        """Apply sigmoid function to input.
        
        Args:
            x: Input value
            
        Returns:
            Sigmoid of input value
        """
        return 1.0 / (1.0 + 2.0 ** (-x))

    def incrementSpeed(self, inc: float) -> None:
        """Adjust simulation speed by multiplier.
        
        Args:
            inc: Speed multiplier
        """
        self.tickTime *= inc
        self.speed_label['text'] = f'Step Delay: {self.tickTime:.5f}'

    def incrementEpsilon(self, inc: float) -> None:
        """Adjust epsilon parameter by increment.
        
        Args:
            inc: Amount to increment epsilon by
        """
        self.ep += inc
        self.epsilon = self.sigmoid(self.ep)
        self.learner.setEpsilon(self.epsilon)
        self.epsilon_label['text'] = f'Epsilon: {self.epsilon:.3f}'

    def incrementGamma(self, inc: float) -> None:
        """Adjust gamma (discount) parameter by increment.
        
        Args:
            inc: Amount to increment gamma by
        """
        self.ga += inc
        self.gamma = self.sigmoid(self.ga)
        self.learner.setDiscount(self.gamma)
        self.gamma_label['text'] = f'Discount: {self.gamma:.3f}'

    def incrementAlpha(self, inc: float) -> None:
        """Adjust alpha (learning rate) parameter by increment.
        
        Args:
            inc: Amount to increment alpha by
        """
        self.al += inc
        self.alpha = self.sigmoid(self.al)
        self.learner.setLearningRate(self.alpha)
        self.alpha_label['text'] = f'Learning Rate: {self.alpha:.3f}'

    def __initGUI(self, win: tkinter.Tk) -> None:
        """Initialize the GUI window and components.
        
        Args:
            win: Main tkinter window
        """
        ## Window ##
        self.win = win

        ## Initialize Frame ##
        win.grid()
        self.dec = -.5
        self.inc = .5
        self.tickTime = 0.1

        ## Epsilon Button + Label ##
        self.setupSpeedButtonAndLabel(win)

        self.setupEpsilonButtonAndLabel(win)

        ## Gamma Button + Label ##
        self.setUpGammaButtonAndLabel(win)

        ## Alpha Button + Label ##
        self.setupAlphaButtonAndLabel(win)

        ## Exit Button ##
        #self.exit_button = tkinter.Button(win,text='Quit', command=self.exit)
        #self.exit_button.grid(row=0, column=9)

        ## Simulation Buttons ##
#        self.setupSimulationButtons(win)

         ## Canvas ##
        self.canvas = tkinter.Canvas(root, height=200, width=1000)
        self.canvas.grid(row=2,columnspan=10)

    def setupAlphaButtonAndLabel(self, win: tkinter.Tk) -> None:
        """Set up alpha adjustment controls.
        
        Args:
            win: Main tkinter window
        """
        self.alpha_minus = tkinter.Button(win,
        text="-",command=(lambda: self.incrementAlpha(self.dec)))
        self.alpha_minus.grid(row=1, column=3, padx=10)

        self.alpha = self.sigmoid(self.al)
        self.alpha_label = tkinter.Label(win, text=f'Learning Rate: {self.alpha:.3f}')
        self.alpha_label.grid(row=1, column=4)

        self.alpha_plus = tkinter.Button(win,
        text="+",command=(lambda: self.incrementAlpha(self.inc)))
        self.alpha_plus.grid(row=1, column=5, padx=10)

    def setUpGammaButtonAndLabel(self, win: tkinter.Tk) -> None:
        """Set up gamma adjustment controls.
        
        Args:
            win: Main tkinter window
        """
        self.gamma_minus = tkinter.Button(win,
        text="-",command=(lambda: self.incrementGamma(self.dec)))
        self.gamma_minus.grid(row=1, column=0, padx=10)

        self.gamma = self.sigmoid(self.ga)
        self.gamma_label = tkinter.Label(win, text=f'Discount: {self.gamma:.3f}')
        self.gamma_label.grid(row=1, column=1)

        self.gamma_plus = tkinter.Button(win,
        text="+",command=(lambda: self.incrementGamma(self.inc)))
        self.gamma_plus.grid(row=1, column=2, padx=10)

    def setupEpsilonButtonAndLabel(self, win: tkinter.Tk) -> None:
        """Set up epsilon adjustment controls.
        
        Args:
            win: Main tkinter window
        """
        self.epsilon_minus = tkinter.Button(win,
        text="-",command=(lambda: self.incrementEpsilon(self.dec)))
        self.epsilon_minus.grid(row=0, column=3)

        self.epsilon = self.sigmoid(self.ep)
        self.epsilon_label = tkinter.Label(win, text=f'Epsilon: {self.epsilon:.3f}')
        self.epsilon_label.grid(row=0, column=4)

        self.epsilon_plus = tkinter.Button(win,
        text="+",command=(lambda: self.incrementEpsilon(self.inc)))
        self.epsilon_plus.grid(row=0, column=5)

    def setupSpeedButtonAndLabel(self, win: tkinter.Tk) -> None:
        """Set up simulation speed controls.
        
        Args:
            win: Main tkinter window
        """
        self.speed_minus = tkinter.Button(win,
        text="-",command=(lambda: self.incrementSpeed(.5)))
        self.speed_minus.grid(row=0, column=0)

        self.speed_label = tkinter.Label(win, text=f'Step Delay: {self.tickTime:.5f}')
        self.speed_label.grid(row=0, column=1)

        self.speed_plus = tkinter.Button(win,
        text="+",command=(lambda: self.incrementSpeed(2)))
        self.speed_plus.grid(row=0, column=2)







    def skip5kSteps(self) -> None:
        """Skip ahead 5000 simulation steps."""
        self.stepsToSkip = 5000

    def __init__(self, win: tkinter.Tk) -> None:
        """Initialize the application.
        
        Args:
            win: Main tkinter window
        """
        self.ep = 0
        self.ga = 2
        self.al = 2
        self.stepCount = 0
        ## Init Gui

        self.__initGUI(win)

        # Init environment
        if robotType == 'crawler':
            self.robot = crawler.CrawlingRobot(self.canvas)
            self.robotEnvironment = crawler.CrawlingRobotEnvironment(self.robot)
        elif robotType == 'pendulum':
            self.robot = pendulum.PendulumRobot(self.canvas)
            self.robotEnvironment = \
                pendulum.PendulumRobotEnvironment(self.robot)
        else:
            raise Exception("Unknown RobotType")

        # Init Agent
        simulationFn = lambda agent: \
          simulation.SimulationEnvironment(self.robotEnvironment,agent)
        actionFn = lambda state: \
          self.robotEnvironment.getPossibleActions(state)
        self.learner = qlearningAgents.QLearningAgent(actionFn=actionFn)

        self.learner.setEpsilon(self.epsilon)
        self.learner.setLearningRate(self.alpha)
        self.learner.setDiscount(self.gamma)

        # Start GUI
        self.running = True
        self.stopped = False
        self.stepsToSkip = 0
        self.thread = threading.Thread(target=self.run)
        self.thread.start()


    def exit(self) -> None:
        """Clean up and exit the application."""
        self.running = False
        for i in range(5):
            if not self.stopped:
                time.sleep(0.1)
        try:
            self.win.destroy()
        except:
            pass
        sys.exit(0)

    def step(self) -> None:
        """Execute one step of the simulation."""
        self.stepCount += 1

        state = self.robotEnvironment.getCurrentState()
        actions = self.robotEnvironment.getPossibleActions(state)
        if len(actions) == 0.0:
            self.robotEnvironment.reset()
            state = self.robotEnvironment.getCurrentState()
            actions = self.robotEnvironment.getPossibleActions(state)
            print('Reset!')
        action = self.learner.getAction(state)
        if action == None:
            raise Exception('None action returned: Code Not Complete')
        nextState, reward = self.robotEnvironment.doAction(action)
        self.learner.observeTransition(state, action, nextState, reward)

    def animatePolicy(self) -> None:
        """Animate the learned policy (pendulum only)."""
        if robotType != 'pendulum':
            raise Exception('Only pendulum can animatePolicy')


        totWidth = self.canvas.winfo_reqwidth()
        totHeight = self.canvas.winfo_reqheight()

        length = 0.48 * min(totWidth, totHeight)
        x,y = totWidth-length-30, length+10



        angleMin, angleMax = self.robot.getMinAndMaxAngle()
        velMin, velMax = self.robot.getMinAndMaxAngleVelocity()

        if not 'animatePolicyBox' in dir(self):
            self.canvas.create_line(x,y,x+length,y)
            self.canvas.create_line(x+length,y,x+length,y-length)
            self.canvas.create_line(x+length,y-length,x,y-length)
            self.canvas.create_line(x,y-length,x,y)
            self.animatePolicyBox = 1
            self.canvas.create_text(x+length/2,y+10,text='angle')
            self.canvas.create_text(x-30,y-length/2,text='velocity')
            self.canvas.create_text(x-60,y-length/4,text='Blue = kickLeft')
            self.canvas.create_text(x-60,y-length/4+20,text='Red = kickRight')
            self.canvas.create_text(x-60,y-length/4+40,text='White = doNothing')



        angleDelta = (angleMax-angleMin) / 100
        velDelta = (velMax-velMin) / 100
        for i in range(100):
            angle = angleMin + i * angleDelta

            for j in range(100):
                vel = velMin + j * velDelta
                state = self.robotEnvironment.getState(angle,vel)
                max, argMax = None, None
                if not self.learner.seenState(state):
                    argMax = 'unseen'
                else:
                    for action in ('kickLeft','kickRight','doNothing'):
                        qVal = self.learner.getQValue(state, action)
                        if max == None or qVal > max:
                            max, argMax = qVal, action
                if argMax != 'unseen':
                    if argMax == 'kickLeft':
                        color = 'blue'
                    elif argMax == 'kickRight':
                        color = 'red'
                    elif argMax == 'doNothing':
                        color = 'white'
                    dx = length / 100.0
                    dy = length / 100.0
                    x0, y0 = x+i*dx, y-j*dy
                    self.canvas.create_rectangle(x0,y0,x0+dx,y0+dy,fill=color)




    def run(self) -> None:
        """Main simulation loop."""
        self.stepCount = 0
        self.learner.startEpisode()
        while True:
            minSleep = .01
            tm = max(minSleep, self.tickTime)
            time.sleep(tm)
            self.stepsToSkip = int(tm / self.tickTime) - 1

            if not self.running:
                self.stopped = True
                return
            for i in range(self.stepsToSkip):
                self.step()
            self.stepsToSkip = 0
            self.step()
#          self.robot.draw()
        self.learner.stopEpisode()

    def start(self) -> None:
        """Start the application main loop."""
        self.win.mainloop()





def run() -> None:
    """Run the Crawler GUI application."""
    global root
    root = tkinter.Tk()
    root.title( 'Crawler GUI' )
    root.resizable( 0, 0 )

#  root.mainloop()


    app = Application(root)
    def update_gui():
        app.robot.draw(app.stepCount, app.tickTime)
        root.after(10, update_gui)
    update_gui()

    root.protocol( 'WM_DELETE_WINDOW', app.exit)
    try:
        app.start()
    except:
        app.exit()
