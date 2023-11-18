import pygame,math,random,sys,os,copy,numpy
from UIpygame import PyUI as pyui
pygame.init()
screenw = 1200
screenh = 600
screen = pygame.display.set_mode((screenw, screenh),pygame.RESIZABLE)
ui = pyui.UI()
done = False
clock = pygame.time.Clock()
ui.styleload_teal()

class Render_3D:
    def __init__(self):
        #x,y,z, xr,yr,zr
        self.camera = [0,0,-200,0,0,0]
        self.focallength = 1000
        self.fov = 45


        self.mesh = []
        self.lightvector = [20,10,30]
        self.refreshdisplay()
        
    def projectpoly(self,poly):
        adjustedpoly = []
        cam = self.camera
        for a in poly[1]:
            x0 = a[0]-cam[0]
            y0 = a[1]-cam[1]
            z0 = a[2]-cam[2]
            #rotates for left/right turning
            x1 = x0*math.cos(-cam[4])+z0*math.sin(-cam[4])
            y1 = y0
            z1 = z0*math.cos(-cam[4])-x0*math.sin(-cam[4])
            #rotates for up/down turning
            x2 = x1
            y2 = y1*math.cos(-cam[3])-z1*math.sin(-cam[3])
            z2 = y1*math.sin(-cam[3])+z1*math.cos(-cam[3])
            #rotates world clockwise/anticlockwise
            x3 = x2*math.cos(-cam[5])-y2*math.sin(-cam[5])
            y3 = x2*math.sin(-cam[5])+y2*math.cos(-cam[5])
            z3 = z2
            adjustedpoly.append([x3,y3,z3])
            
        projectedpoly = []
        for a in adjustedpoly:
            projectedpoly.append([(self.focallength)/(a[2])*(a[0])+ui.screenw/2,(self.focallength )/(a[2])*(a[1])+ui.screenh/2])
            
        angle = poly[4]
        col = (poly[0][0]*angle,poly[0][1]*angle,poly[0][2]*angle)
        return [col,projectedpoly,poly[2],poly[3],poly[4]]
    
    def refreshdisplay(self):
        for a in range(len(self.mesh)):
            self.mesh[a][3] = self.avpoint(self.mesh[a][1])
            self.mesh[a][2] = self.pythag3d(self.camera,self.mesh[a][3])
            self.mesh[a][4] = self.lightcalc(self.mesh[a][1])
        self.mesh.sort(key=lambda x: x[2],reverse=True)
        self.projected = []
        for a in self.mesh:
            poly = self.projectpoly(a)
            if poly[2]>40 and self.getclockwise(poly):
                self.projected.append(self.projectpoly(a))
                
    def pythag3d(self,p1,p2):
        return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)**0.5
    def avpoint(self,points):
        tot = [0,0,0]
        for a in points:
            tot[0]+=a[0]
            tot[1]+=a[1]
            tot[2]+=a[2]
        tot[0]/=len(points)
        tot[1]/=len(points)
        tot[2]/=len(points)
        return tot
    def getclockwise(self,poly):
        points = copy.deepcopy(poly[1])
        yvals = [a[1] for a in points]
        index = yvals.index(min(yvals))
        while index!=0:
            points.append(points.pop(0))
            index-=1
##        if points[1][0] == points[2][0]:
##            if 
##        if points[1][0]>points[2][0]:
##            return True

##        if (points[0][0]-points[1][0])<0:
##            if points[2][0]-points[0][0] < (points[0][1]-points[1][1])/(points[0][0]-points[1][0])*(points[2][1]-points[0][1]):
##                return True
##        elif (points[0][0]-points[1][0]) == 0:
##            if points[2][1]<points[1][1]:
##                return True
##        elif points[2][0]-points[0][0] > (points[0][1]-points[1][1])/(points[0][0]-points[1][0])*(points[2][1]-points[0][1]):
##            return True
##        print(points,math.atan2(points[0][1]-points[1][1],points[0][0]-points[1][0]),math.atan2(points[0][1]-points[2][1],points[0][0]-points[2][0]))

        if points[0][1] == points[2][1]:
            return points[0][0]>points[2][0]
        elif points[0][1] == points[1][1]:
            return points[0][0]<points[1][0]
        elif math.atan2(points[0][1]-points[1][1],points[0][0]-points[1][0])<math.atan2(points[0][1]-points[2][1],points[0][0]-points[2][0]):
            return True
    
        
        return False
        
            
    def lightcalc(self,poly):
        light = self.lightvector
        v1 = [poly[1][0]-poly[0][0],poly[1][1]-poly[0][1],poly[1][2]-poly[0][2]]
        v2 = [poly[2][0]-poly[0][0],poly[2][1]-poly[0][1],poly[2][2]-poly[0][2]]
        n = [v1[1]*v2[2]-v1[2]*v2[1],
             v1[2]*v2[0]-v1[0]*v2[2],
             v1[0]*v2[1]-v1[1]*v2[0]]
        try:
            costheta = (n[0]*light[0]+n[1]*light[1]+n[2]*light[2])/(pythag3d([0,0,0],n)*pythag3d([0,0,0],light))
        except:
            costheta = 1

        return (costheta+1)/2

    def polypreprocess(self,poly):
        npoly = []
        for a in poly:
            if len(a[1]) == 3:
                npoly.append([a[0],a[1],0])
            elif len(a[1]) == 4:
                temp = copy.deepcopy(a[1])
                del temp[3]
                npoly.append([a[0],temp,0])
                temp2 = copy.deepcopy(a[1])
                del temp2[1]
                npoly.append([a[0],temp2,0])
            else:
                print(len(a[1]),a)
        for a in range(len(npoly)):
            npoly[a].append(self.avpoint(npoly[a][1]))
            npoly[a].append(self.lightcalc(npoly[a][1]))
        return npoly

    def cameracontroller(self):
        precam = self.camera[:]
        speed = 3
        kprs = pygame.key.get_pressed()
        rel = pygame.mouse.get_rel()
        mprs = pygame.mouse.get_pressed()
##        if not mprs[1]: rel = [0,0]
        if kprs[pygame.K_w]:
            self.camera[2]+=speed*math.cos(self.camera[4])
            self.camera[0]+=speed*math.sin(self.camera[4])
        elif kprs[pygame.K_s]:
            self.camera[2]-=speed*math.cos(self.camera[4])
            self.camera[0]-=speed*math.sin(self.camera[4])
        if kprs[pygame.K_a]:
            self.camera[2]+=speed*math.cos(self.camera[4]-math.pi/2)
            self.camera[0]+=speed*math.sin(self.camera[4]-math.pi/2)
        elif kprs[pygame.K_d]:
            self.camera[2]+=speed*math.cos(self.camera[4]+math.pi/2)
            self.camera[0]+=speed*math.sin(self.camera[4]+math.pi/2)
        if kprs[pygame.K_SPACE]: self.camera[1]-=5
        elif kprs[pygame.K_LSHIFT]: self.camera[1]+=5

        self.camera[3]-=rel[1]/1000
        self.camera[4]+=rel[0]/1000
        if self.camera[3]>math.pi/2: self.camera[3] = math.pi/2
        elif self.camera[3]<-math.pi/2: self.camera[3] = -math.pi/2

        if self.camera!=precam:
            self.refreshdisplay()
            
    def cubecameracontroller(self):
        precam = self.camera[:]
        speed = 10
        kprs = pygame.key.get_pressed()
        rel = pygame.mouse.get_rel()
        mprs = pygame.mouse.get_pressed()

        # Up/down, left/right
        inpu = [0,0]
        inpu[0]+=int(kprs[pygame.K_s])
        inpu[0]-=int(kprs[pygame.K_w])
        inpu[1]+=int(kprs[pygame.K_d])
        inpu[1]-=int(kprs[pygame.K_a])

        if mprs[0]:
            inpu[0]-=rel[1]/10
            inpu[1]-=rel[0]/10
        
        self.camera[2]+=speed*math.cos(self.camera[4]-math.pi/2)*math.cos(self.camera[3])*inpu[1]
        self.camera[0]+=speed*math.sin(self.camera[4]-math.pi/2)*math.cos(self.camera[3])*inpu[1]

        self.camera[1]-=speed*inpu[0]

        
        
        self.camera[3] = math.atan2(self.camera[1],((self.camera[0]**2+self.camera[2]**2)**0.5))
        self.camera[4] = math.atan2(self.camera[0],self.camera[2])-math.pi

        distance = 350/self.pythag3d((0,0,0),self.camera)
        self.camera[0]*=distance
        self.camera[1]*=distance
        self.camera[2]*=distance
    
        if self.camera!=precam:
            self.refreshdisplay()

    def drawmesh(self,screen):
        for a in self.projected:
            pygame.draw.polygon(screen,a[0],a[1])

    def makecube(self,x,y,z,side,cols=(150,150,150),border=-1,bordercol=(0,0,0)):
##        bordercol = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        if border == -1:
            border = int(side/10)
            
        if type(cols) == list:
            if len(cols) == 6:
                ncols = []
                for a in cols:
                    ncols+=[a,a]
                cols = ncols
        elif type(cols) == tuple:
            cols = [cols for a in range(12)]
            
        mesh = []
        sid = side/2
        corners = [(x+sid,y+sid,z+sid),(x-sid,y+sid,z+sid),(x-sid,y+sid,z-sid),(x+sid,y+sid,z-sid),
                   (x+sid,y-sid,z+sid),(x-sid,y-sid,z+sid),(x-sid,y-sid,z-sid),(x+sid,y-sid,z-sid)]
        connections = [(5,4,6),(7,6,4),(3,2,7),(6,7,2),(2,1,6),(5,6,1),(1,0,5),(4,5,0),(0,3,4),(7,4,3),(0,1,3),(2,3,1)]
        for i,a in enumerate(connections):
            if cols[i] != -1:
                if border == 0:
                    mesh.append([cols[i],[corners[a[0]],corners[a[1]],corners[a[2]]]])
                else:

                    c0 = corners[a[0]]
                    c1 = corners[a[1]]
                    c2 = corners[a[2]]
                    a = numpy.array(c1)
                    b = numpy.array(c2)
                    c = numpy.array(c0)
                    b0 = border
                    b1 = b0/self.pythag3d(a-b,(0,0,0))
                    p0 = c+(b0/self.pythag3d(a+b-2*c,(0,0,0)))*(a+b-2*c)
                    p1 = a+b1*(b-a)
                    p2 = b+b1*(a-b)

                    mesh.append([cols[i],[p0,p1,p2]])
                    mesh.append([bordercol,[b,p0,p2]])
                    mesh.append([bordercol,[b,c,p0]])
                    mesh.append([bordercol,[c,a,p0]])
                    mesh.append([bordercol,[a,p1,p0]])
                    
                    
        self.mesh+=self.polypreprocess(mesh)
        self.refreshdisplay()
        

class Cube:
    def __init__(self,n=3):
        # 0 top white,
        # 1 front green
        # 2 right red
        # 3 back blue
        # 4 left orange
        # 5 bottom yellow
        
        self.colkey = {0:(255,255,255),1:(0,200,0),2:(255,0,0),3:(0,0,255),4:(255,107,0),5:(255,242,0)}
        self.n = n
        self.reset(False)

        self.movemap = {'U':self.makemovemapinner(0)+self.makemovemapouter([(1,'u',True),(4,'u',True),(3,'u',True),(2,'u',True)]),
                        'F':self.makemovemapinner(1)+self.makemovemapouter([(0,'d',False),(2,'l',False),(5,'u',True),(4,'r',True)]),
                        'R':self.makemovemapinner(2)+self.makemovemapouter([(1,'r',True),(0,'r',True),(3,'l',False),(5,'r',True)]),
                        'B':self.makemovemapinner(3)+self.makemovemapouter([(0,'u',True),(4,'l',False),(5,'d',False),(2,'r',True)]),
                        'L':self.makemovemapinner(4)+self.makemovemapouter([(1,'l',False),(5,'l',False),(3,'r',True),(0,'l',False)]),
                        'D':self.makemovemapinner(5)+self.makemovemapouter([(1,'d',False),(2,'d',False),(3,'d',False),(4,'d',False)]),
                        'M':self.makemovemapouter([(1,'v',False),(5,'v',False),(3,'v',True),(0,'v',False)]),
                        'E':self.makemovemapouter([(1,'h',False),(2,'h',False),(3,'h',False),(4,'h',False)]),
                        'S':self.makemovemapouter([(0,'h',False),(2,'v',False),(5,'h',True),(4,'v',True)])}
        self.movemap['X'] = self.movemap['R']+self.movemapflip(self.movemap['L'])+self.movemapflip(self.movemap['M'])
        self.movemap['Y'] = self.movemap['U']+self.movemapflip(self.movemap['E'])+self.movemapflip(self.movemap['D'])
        self.movemap['Z'] = self.movemap['F']+self.movemap['S']+self.movemapflip(self.movemap['B'])
        
        primes = {m+"'":self.movemapflip(copy.deepcopy(self.movemap[m])) for m in self.movemap}
        doubles = {m+"2":self.movemapdouble(copy.deepcopy(self.movemap[m])) for m in self.movemap}

        
        
        self.movemap.update(primes)
        self.movemap.update(doubles)

        self.renderer = Render_3D()
        self.resetcamera()
        self.genmesh()
        
    def reset(self,update=True):
        self.cube = {s:[[s for x in range(self.n)] for y in range(self.n)] for s in range(6)}
        if update:
            self.resetcamera()
            self.genmesh()
    def resetcamera(self):
        self.renderer.camera = [-80,80,-200,0,0,math.pi]
        
### Move map functions ###                    
    def makemovemapinner(self,face):
        return [[(face,0,0),(face,0,2),(face,2,2),(face,2,0)],[(face,0,1),(face,1,2),(face,2,1),(face,1,0)]]
    def makemovemapouter(self,sides):
        info = []
        for s in sides:
            if s[1] == 'r': new=[(s[0],0,2),(s[0],1,2),(s[0],2,2)]
            elif s[1] == 'l': new=[(s[0],0,0),(s[0],1,0),(s[0],2,0)]
            elif s[1] == 'u': new=[(s[0],0,0),(s[0],0,1),(s[0],0,2)]
            elif s[1] == 'd': new=[(s[0],2,0),(s[0],2,1),(s[0],2,2)]
            elif s[1] == 'v': new=[(s[0],0,1),(s[0],1,1),(s[0],2,1)]
            elif s[1] == 'h': new=[(s[0],1,0),(s[0],1,1),(s[0],1,2)]
            if s[2]:
                new.reverse()
            info+=new
        n = int(len(info)/len(sides))
        finals = [[] for a in range(n)]
        for s in range(n):
            for b in range(4):
                finals[s].append(info[b*n+s])  
        return finals
    def movemapflip(self,moves):
        c = copy.deepcopy(moves)
        for a in c:
            a.reverse()
        return c
    def movemapdouble(self,moves):
        nmoves = []
        for b in moves:
            nmoves.append([a for i,a in enumerate(b) if i%2==0])
            nmoves.append([a for i,a in enumerate(b) if i%2==1])
        return nmoves

### Moving cube functions ###
    def move(self,move,update=True):
        for cycle in self.movemap[move]:
            storeprev = self.getat(cycle[-1])
            for loc in cycle:
                store = self.getat(loc)
                self.setat(loc,storeprev)
                storeprev = store
        if update:
            self.genmesh()
    def getat(self,location):
        return self.cube[location[0]][location[1]][location[2]]
    def setat(self,location,value):
        self.cube[location[0]][location[1]][location[2]] = value
    def scramble(self):
        scram = self.makescramble()
        st = ''
        for a in scram:
            st+=a+' '
            self.move(a,False)
        ui.IDs['scramble text'].settext(st)
        self.resetcamera()
        self.genmesh()

    def makescramble(self,length=20):
        self.reset(False)
        basics = ['R','L','U','F','D','B']
        moves = [a for a in self.movemap if a[0] in basics]
        scramble = []
        for a in range(length):
            move = random.choice(moves)
            while move[0] in [m[0] for m in scramble[len(scramble)-2:]]:
                move = random.choice(moves)
            scramble.append(move)
        return scramble
    def output(self):
        for s in self.cube:
            print(f'-- {s} --')
            for y in self.cube[s]:
                for x in y:
                    print(x,end='')
                print()
    def inputkey(self):
        key = ui.IDs['cube input'].text
        if key in self.movemap:
            self.move(key)
            ui.IDs['cube input'].settext()
### Rendering Functions ###
    def genmesh(self,posx=0,posy=0,posz=0,sides=40):

        self.renderer.mesh = []
        
        decoder = [[[[-1,-1,-1,(3,0,2),(4,0,0),(0,0,0)],[-1,-1,-1,(3,0,1),-1,(0,0,1)],[-1,-1,(2,0,2),(3,0,0),-1,(0,0,2)]],
                    [[-1,-1,-1,-1,(4,0,1),(0,1,0)],[-1,-1,-1,-1,-1,(0,1,1)],[-1,-1,(2,0,1),-1,-1,(0,1,2)]],
                    [[-1,(1,0,0),-1,-1,(4,0,2),(0,2,0)],[-1,(1,0,1),-1,-1,-1,(0,2,1)],[-1,(1,0,2),(2,0,0),-1,-1,(0,2,2)]]],
                   
                   [[[-1,-1,-1,(3,1,2),(4,1,0),-1],[-1,-1,-1,(3,1,1),-1,-1],[-1,-1,(2,1,2),(3 ,1,0),-1,-1]],
                    [[-1,-1,-1,-1,(4,1,1),-1],[-1,-1,-1,-1,-1,-1],[-1,-1,(2,1,1),-1,-1,-1]],
                    [[-1,(1,1,0),-1,-1,(4,1,2),-1],[-1,(1,1,1),-1,-1,-1,-1],[-1,(1,1,2),(2,1,0),-1,-1,-1]]],
                   
                   [[[(5,2,0),-1,-1,(3,2,2),(4,2,0),-1],[(5,2,1),-1,-1,(3,2,1),-1,-1],[(5,2,2),-1,(2,2,2),(3,2,0),-1,-1]],
                    [[(5,1,0),-1,-1,-1,(4,2,1),-1],[(5,1,1),-1,-1,-1,-1,-1],[(5,1,2),-1,(2,2,2),-1,-1,-1]],
                    [[(5,0,0),(1,2,0),-1,-1,(4,2,2),-1],[(5,0,1),(1,2,1),-1,-1,-1,-1],[(5,0,2),(1,2,2),(2,2,0),-1,-1,-1]]]]
        
        cols = [self.colkey[5],self.colkey[1],self.colkey[2],self.colkey[3],self.colkey[4],self.colkey[0]]
 
        for y in range(len(decoder)):
            for z in range(len(decoder[y])):
                for x in range(len(decoder[y][z])):
                    cols = []
                    for a in decoder[y][z][x]:
                        if a == -1:
                            cols.append(-1)
                        else:
                            cols.append(self.colkey[self.getat(a)])
                    self.renderer.makecube(posx-(x-1)*sides,posy-(y-1)*sides,posz-(z-1)*sides,sides,cols)
                    
    def update(self,screen):
        self.renderer.cubecameracontroller()
        self.renderer.drawmesh(screen)

    
cube = Cube()

ui.makebutton(10,10,'Scramble',40,cube.scramble)
ui.makebutton(10,55,'Solve',40,cube.reset)
ui.makebutton(10,100,'Center',40,cube.resetcamera)
ui.maketext(155,15,'',40,ID='scramble text')
ui.maketextbox(10,145,'',70,1,textsize=40,verticalspacing=4,command=cube.inputkey,ID='cube input',chrlimit=2)


while not done:
    for event in ui.loadtickdata():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            cube.renderer.refreshdisplay()
    
    screen.fill(pyui.Style.wallpapercol)
    cube.update(screen)

    
    ui.rendergui(screen)
    pygame.display.flip()
    clock.tick(60)                                               
pygame.quit() 











