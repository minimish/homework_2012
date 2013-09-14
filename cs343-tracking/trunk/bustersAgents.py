# bustersAgents.py
# ----------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference

class BustersAgent:
  "An agent that tracks and displays its beliefs about ghost positions."
  
  def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None ):
    inferenceType = util.lookup(inference, globals())
    self.inferenceModules = [inferenceType(a) for a in ghostAgents]
    
  def registerInitialState(self, gameState):
    "Initializes beliefs and inference modules"
    import __main__
    self.display = __main__._display
    for inference in self.inferenceModules: inference.initialize(gameState)
    self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
    self.firstMove = True
    
  def observationFunction(self, gameState):
    "Removes the ghost states from the gameState"
    agents = gameState.data.agentStates
    gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
    return gameState

  def getAction(self, gameState):
    "Updates beliefs, then chooses an action based on updated beliefs."
    for index, inf in enumerate(self.inferenceModules):
      if not self.firstMove: inf.elapseTime(gameState)
      self.firstMove = False
      inf.observeState(gameState)
      self.ghostBeliefs[index] = inf.getBeliefDistribution()
    self.display.updateDistributions(self.ghostBeliefs)
    return self.chooseAction(gameState)

  def chooseAction(self, gameState):
    "By default, a BustersAgent just stops.  This should be overridden."
    return Directions.STOP

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
  "An agent controlled by the keyboard that displays beliefs about ghost positions."
  
  def __init__(self, index = 0, inference = "ExactInference", ghostAgents = None):
    KeyboardAgent.__init__(self, index)
    BustersAgent.__init__(self, index, inference, ghostAgents)
    
  def getAction(self, gameState):
    return BustersAgent.getAction(self, gameState)
    
  def chooseAction(self, gameState):
    return KeyboardAgent.getAction(self, gameState)

from distanceCalculator import Distancer
from game import Actions
from game import Directions

class GreedyBustersAgent(BustersAgent):
  "An agent that charges the closest ghost."
  
  def registerInitialState(self, gameState):
    "Pre-computes the distance between every two points."
    BustersAgent.registerInitialState(self, gameState)
    self.distancer = Distancer(gameState.data.layout, False)
    
  def chooseAction(self, gameState):
    """
    First computes the most likely position of each ghost that 
    has not yet been captured, then chooses an action that brings 
    Pacman closer to the closest ghost (in maze distance!).
    
    To find the maze distance between any two positions, use:
    self.distancer.getDistance(pos1, pos2)
    
    To find the successor position of a position after an action:
    successorPosition = Actions.getSuccessor(position, action)
    
    To get a list of booleans, one for each agent, indicating whether
    or not the agent is alive, use gameState.getLivingGhosts()
    Note that pacman is always agent 0, so the ghosts are agents 1, 
    onwards (just as before).
     
    You may remove Directions.STOP from the list of available actions.
    """
    pacmanPosition = gameState.getPacmanPosition()
    legal = [a for a in gameState.getLegalPacmanActions() if a != Directions.STOP]
    "*** YOUR CODE HERE ***"

    # find most likely ghost
    ghostList = gameState.getLivingGhosts()
    ghostPositionList = [None for i in range(len(ghostList))]
   
    for ghostId, ghostLiving in enumerate(ghostList):
       if ghostLiving:
	  # only process living ghosts
	  maxProb = 0
	  maxPosition = None
	  for key, value in self.ghostBeliefs[ghostId - 1].items(): # ghosts index from 0
	    if value > maxProb:
	      maxProb = value
	      maxPosition = key

	  ghostPositionList[ghostId] = maxPosition

    optAction = None
    optDistance = 99999
 
    # find optimal action
    for action in legal:
      nextPosition = Actions.getSuccessor(pacmanPosition, action)

      ghostDis = 99999
      for ghostPosition in ghostPositionList:
        if ghostPosition == None: continue

	distance = self.distancer.getDistance(nextPosition, ghostPosition)
	if distance < ghostDis:
	  ghostDis = distance

      if ghostDis < optDistance:
        optDistance = ghostDis
        optAction = action

    return optAction
    #util.raiseNotDefined()
