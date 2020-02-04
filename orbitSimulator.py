from graphics import GraphWin, Circle, color_rgb, Point, Line, Rectangle, Text
import time
import math

periastro = 0
apoastro = 0

class orbitSimulator(GraphWin):

    def __init__(self, gameSpeed = 1000, frameRate = 60):
        GraphWin.__init__(self, 'Orbit-Simulator', 1200, 600)
        self.setBackground(color_rgb(0,0,0))
        
        self.frameRate = frameRate
        self.gameSpeed = gameSpeed
        self.body = []
        self.selectedBody = None

        self.createHud()

        self.createSolarSystem()
        self.start()
    
    def createHud(self):
        self.mode = 'none'
        self.modeText = Text(Point(100,50), 'Mode: None')
        self.modeText.setTextColor(color_rgb(255,255,255))
        self.modeText.draw(self)

        self.action = Text(Point(600, 70), 'D - Delete\nM - Move\nR - Restart\nF - Increase Mass in 10%\nG - Decrease Mass by 10%\nUp - Increase GameSpeed\nDown - Decrease GameSpeed')
        self.action.setTextColor(color_rgb(255,255,255))
        self.action.draw(self)

        self.speedText = Text(Point(1100, 50), 'Game Speed: ' + str(self.gameSpeed / 1000) + 'x')
        self.speedText.setTextColor(color_rgb(255,255,255))
        self.speedText.draw(self)
    
    def start(self):
        while self.isOpen():
            self.render()
            
    def render(self):
        self.moveBody()
        self.applyGravity()
        self.checkMouseOnBody()
        self.checkKeyboard()
        time.sleep(1/self.frameRate)

    def createBody(self, name, size, mass, pX, pY, color, orbitLineSize = 0, fixed = False):
        self.body.append(body(self, name, size, mass, pX, pY, orbitLineSize, fixed))
        self.body[len(self.body) - 1].setFill(color)
        self.body[len(self.body) - 1].draw(self)

    def moveBody(self):
        for body in self.body:
            if not body.fixed:
                previousPosition = body.getCenter()
                body.move(body.speedX * (self.gameSpeed/1000), body.speedY * (self.gameSpeed/1000))
                body.orbitLine.insert(0, Line(previousPosition, body.getCenter()))
                body.orbitLine[0].setFill(color_rgb(255,255,255))
                body.orbitLine[0].draw(self)
                if len(body.orbitLine) > body.orbitLineSize:
                    body.orbitLine[body.orbitLineSize].undraw()

    def checkMouseOnBody(self):
        mouseClick = self.checkMouse()
        if mouseClick != None:
            if self.selectedBody != None and self.mode == 'move':
                self.body[self.selectedBody].move(mouseClick.getX() - self.body[self.selectedBody].getCenter().getX(), mouseClick.getY() - self.body[self.selectedBody].getCenter().getY())
                self.action.setText('moved ' + self.body[self.selectedBody].name)
                self.selectedBody = None
            else:
                for body in self.body:
                    if mouseClick.getX() <= body.getCenter().getX() + body.size and mouseClick.getX() >= body.getCenter().getX() - body.size:
                        if mouseClick.getY() <= body.getCenter().getY() + body.size and mouseClick.getY() >= body.getCenter().getY() - body.size:
                            if self.mode == 'delete':
                                self.action.setText(body.name + ' deleted')
                                for orbitline in body.orbitLine:
                                    orbitline.undraw()
                                body.undraw()
                                self.body.remove(body)
                            if self.mode == 'move' and self.selectedBody == None:
                                self.action.setText(body.name + ' selected\nClick to place')
                                self.selectedBody = self.body.index(body)
                            if self.mode == 'increase10':
                                self.action.setText(body.name + ' mass increased')
                                body.mass *= 1.1
                            if self.mode == 'decrease10':
                                self.action.setText(body.name + ' mass decreased')
                                body.mass *= 0.9

    def checkKeyboard(self):
        key = self.checkKey()
        if key == 'd':
            self.modeText.setText('Mode: Delete')
            self.mode = 'delete'
        if key == 'm':
            self.modeText.setText('Mode: Move')
            self.mode = 'move'
        if key == 'r':
            self.restart()
        if key == 'f':
            self.modeText.setText('Mode: Increase Mass 10%')
            self.mode = 'increase10'
        if key == 'g':
            self.modeText.setText('Mode: Decrease Mass 10%')
            self.mode = 'decrease10'
        if key == 'Up':
            if self.gameSpeed >= 1:
                self.gameSpeed += 10**(len(str(self.gameSpeed)) - 1)
            self.speedText.setText('Game Speed: ' + str(self.gameSpeed / 1000) + 'x')
        if key == 'Down':
            if self.gameSpeed > 1:
                self.gameSpeed -= 10**(len(str(self.gameSpeed - 1)) - 1)
            self.speedText.setText('Game Speed: ' + str(self.gameSpeed / 1000) + 'x')
            

    def restart(self):
        self.destroy()
        self.close()
        self.__init__(self.gameSpeed, self.frameRate)
    
    def applyGravity(self):
        for body1 in self.body:
            for body2 in self.body:
                if body1 != body2:
                    distanceX = abs(body1.getCenter().getX() - body2.getCenter().getX())
                    distanceY = abs(body1.getCenter().getY() - body2.getCenter().getY())
                    distance = abs(math.sqrt(math.pow(distanceX, 2) + math.pow(distanceY , 2)))
                    if body1.periasis == -1:
                        body1.periasis = distance
                    if distance > body1.apoasis:
                        body1.apoasis = distance

                    elif distance < body1.periasis:
                        body1.periasis = distance

                    force = (body1.mass * body2.mass) / math.pow(distance, 2)
                    acceleration = 5e-29 * (force / body1.mass)
                    sen = distanceX / distance
                    cos = distanceY / distance

                    if body1.getCenter().getX() < body2.getCenter().getX():
                        body1.speedX += acceleration * sen * (self.gameSpeed/1000)
                    else:
                        body1.speedX -= acceleration * sen * (self.gameSpeed/1000)
                    
                    if body1.getCenter().getY() < body2.getCenter().getY():
                        body1.speedY += acceleration * cos * (self.gameSpeed/1000)
                    else:
                        body1.speedY -= acceleration * cos * (self.gameSpeed/1000)

    def createSolarSystem(self):
        self.createBody('earth', 7, 5.9e+24, 500, 300, color_rgb(0,255,50), 580)
        self.createBody('mars', 6, 6.4e+23, 448, 300, color_rgb(255,0,0),1100)
        self.createBody('venus', 7, 4.8e+24, 528, 300, color_rgb(255,100,50),340)
        self.createBody('mercury', 5, 3.2e+23, 560, 300, color_rgb(150,100,50),140)
        self.createBody('jupiter', 10, 1.9e+27, 80, 300, color_rgb(255,125,55), 2000)
        self.createBody('sun', 15, 2e+30, 600, 300, color_rgb(255,255,0))

        self.body[0].speedY = 1
        self.body[1].speedY = 0.8
        self.body[2].speedY = 1.16
        self.body[3].speedY = 1.56
        self.body[4].speedY = 0.43

    
            
    
class body(Circle):
    def __init__(self, graphWin, name, size, mass, pX, pY, orbitLineSize = 0, fixed = False):
        Circle.__init__(self, Point(pX, pY), size)
        self.size = size
        self.mass = mass
        self.name = name
        self.speedX = 0
        self.speedY = 0
        self.fixed = fixed
        self.apoasis = -1
        self.periasis = -1
        self.orbitLine = []
        self.orbitLineSize = orbitLineSize

class rocket(Rectangle):
    def __init__(self, pX, pY):
        Rectangle.__init__(self, Point(pX, pY), Point(pX + 1,pY + 1))
        self.setFill(color_rgb(255,255,255))

    

        

