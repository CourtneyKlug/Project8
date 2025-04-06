import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
import Player as playerClasses
from panda3d.core import Vec3
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from math import pi, sin, cos
import math, sys, random
from direct.task import Task
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from panda3d.core import AudioSound
from panda3d.core import loadPrcFileData
from panda3d.core import PNMImage
from panda3d.core import Notify
loadPrcFileData('', 'notify-level-ffmpeg error')

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        windowTitle = WindowProperties()
        windowTitle.setTitle("Space Jam")
        self.win.requestProperties(windowTitle)
        base.disableMouse()

        self.backgroundMusic = loader.loadSfx("./Assets/Music/ShootingStars.mp3")
        self.backgroundMusic.setLoop(True)  # Set to loop the music
        self.backgroundMusic.setVolume(0.8)  # Set the volume (0.0 to 1.0)
        self.backgroundMusic.play()

        self.circleScale = 5.0  # Initial scale of the circles
        self.accept("o", self.IncreaseCircleSize)
        self.accept("p", self.DecreaseCircleSize)
        self.CameraDefense(self.loader, self.render)
        self.currentSizeLevel = 1  # Start at level 1 (small)
        self.sizeLevels = {1: 5.0, 2: 10.0, 3: 15.0}  # Define sizes: small, medium, large

        self.cTrav = CollisionTraverser()
        self.cTrav.traverse(self.render)
        self.pusher = CollisionHandlerPusher()

        self.numRocks = 30  # Number of rocks
        self.SetScene()

        self.pusher.addCollider(self.Hero.collisionNode, self.Hero.modelNode)
        self.cTrav.addCollider(self.Hero.collisionNode, self.pusher)
        # self.cTrav.showCollisions(self.render)

        # Bind the key correctly within your class
        self.texture_set_index = 0
        self.texture_paths = [
            "./Assets/DroneDefender/Camera/sphere1_auv.jpg",
            "./Assets/DroneDefender/Camera/sphere1_flat2.jpg",
            "./Assets/DroneDefender/Camera/sphere1_flat.jpg"
        ]
        self.current_texture_index = 0  # Start with the first texture

        self.accept("t", self.textureChange)
        self.Hero.RemoveCameraDefenseModels()

    def SetScene(self):
        self.Universe = spaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.x", self.render, 'Universe', "./Assets/Universe/jeremy-thomas-4dpAqfTbvKA-unsplash.jpg", (0, 0, 0), 15000)
        self.Planet1 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet1', "./Assets/Planets/Preset 1/2k_earth_daymap.jpg", (-6000, -3000, -800), 250)
        self.Planet2 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet2', "./Assets/Planets/Preset 1/2k_jupiter.jpg", (1500, 5000, 280), 250) 
        self.Planet3 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet3', "./Assets/Planets/Preset 1/2k_venus_surface.jpg", (3000, 5000, -1000), 250)
        self.Planet4 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet4', "./Assets/Planets/Preset 1/2k_neptune.jpg", (300, 6000, 500), 150) 
        self.Planet5 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet5', "./Assets/Planets/Preset 1/2k_mars.jpg", (-1000, 5000, -1000), 450) 
        self.Planet6 = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, 'Planet6', "./Assets/Planets/Preset 1/2k_mercury.jpg", (0, -900, -1400), 700) 
        self.SpaceStation1 = spaceJamClasses.SpaceStation(self.loader, "./Assets/SpaceStation/spaceStation.egg", self.render, 'Space Station', "./Assets/SpaceStation/SpaceStation1_Dif2.png", (1500, 1000, -100), 40) 
        self.Hero = playerClasses.PlayerSpaceship (self.loader, self.accept, "./Assets/Spaceships/Dumbledore/Dumbledore.egg", self.render, 'Hero', "./Assets/Spaceships/Dumbledore/spacejet_C.png", Vec3(1000, 1200, -50), 50, self.taskMgr, self.render, self.numRocks)
        self.CameraDefenseSystem = spaceJamClasses.CameraDefense(self.loader, "./Assets/DroneDefender/Camera/sphere.x", self.render, 'CameraDefense', "./Assets/DroneDefender/Camera/sphere1_flat.jpg", (0, 0, 0), 1.0)
        self.Wanderer1 = spaceJamClasses.Wanderer(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Traveler", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Hero)
        self.Wanderer2 = spaceJamClasses.Wanderer2(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, "Walker", 6.0, "./Assets/DroneDefender/octotoad1_auv.png", self.Hero)

        self.taskMgr.add(self.Planet1.rotate, "RotatePlanet1")
        self.taskMgr.add(self.Planet2.rotate, "RotatePlanet2")
        self.taskMgr.add(self.Planet3.rotate, "RotatePlanet3")
        self.taskMgr.add(self.Planet4.rotate, "RotatePlanet4")
        self.taskMgr.add(self.Planet5.rotate, "RotatePlanet5")
        self.taskMgr.add(self.Planet6.rotate, "RotatePlanet6")

        # Define the list of planets
        planets = [self.Planet1, self.Planet2, self.Planet3, self.Planet4, self.Planet5, self.Planet6]

        self.AssignDroneToPlanet("Planet2Drone", "Cloud", 600, self.Planet2)
        self.AssignDroneToPlanet("Planet3Drone", "MLB", 800, self.Planet3)
        self.AssignDroneToPlanet("Planet4Drone", "MLB", 600, self.Planet4)
        self.AssignDroneToPlanet("Planet5Drone", "Cloud", 900, self.Planet5)

        self.rocks = []  # Initialize rocks list

        # Set up new rocks
        radius = 300    # Distance from the chosen planet

        for i in range(self.numRocks):
            # Randomly select a planet
            chosenPlanet = random.choice(planets)

            # Create and assign the chosen planet to the rock
            rock = spaceJamClasses.Rock(self.loader, "./Assets/Planets/protoPlanet.x", self.render, f"Rock{i+1}", "./Assets/Asteroids/10464_Asteroid_v1_diffuse.jpg", Vec3(0, 0, 0), 20)
            rock.assignedPlanet = chosenPlanet

            # Initial placement of the rock
            angle = random.uniform(0, 360)
            x = chosenPlanet.modelNode.getX() + radius * math.cos(math.radians(angle))
            y = chosenPlanet.modelNode.getY() + radius * math.sin(math.radians(angle))
            z = chosenPlanet.modelNode.getZ()
            rock.modelNode.setPos(x, y, z)

            self.rocks.append(rock)  # Add rock to the list
        
        self.taskMgr.add(self.OrbitRocks, "OrbitRocks")

        self.DroneSpawn()
        self.SetCamera()
        self.EnableHUD()

    def textureChange(self):
        self.change_textures()
        self.changeTexture()
        self.Hero.CycleMissileTexture()


    def AssignDroneToPlanet(self, droneName, orbitType, orbitRadius, planet):
        droneNickname = ""
        if orbitType == "Cloud":
            droneNickname = "CloudDrone" + str(spaceJamClasses.Drone.droneCount)
        elif orbitType == "MLB":
            droneNickname = "BaseballDrone" + str(spaceJamClasses.Drone.droneCount)

        spaceJamClasses.Drone.droneCount += 1  # Increment drone count for unique names

        # Create the Orbiter (drone)
        orbiter = spaceJamClasses.Orbiter(
            self.loader, self.taskMgr, "./Assets/DroneDefender/DroneDefender.obj", self.render,
            droneNickname, Vec3(6.0, 6.0, 6.0), "./Assets/DroneDefender/octotoad1_auv.png",
            planet, orbitRadius, orbitType, self.Hero
        )

        # Track the Orbiter
        if orbitType == "Cloud":
            if not hasattr(self, "cloudDrones"):
                self.cloudDrones = []  # Initialize list if not already present
            self.cloudDrones.append(orbiter)
        elif orbitType == "MLB":
            if not hasattr(self, "mlbDrones"):
                self.mlbDrones = []  # Initialize list if not already present
            self.mlbDrones.append(orbiter)

    def IncreaseCircleSize(self):
        # Move to the next size level, wrapping around if at the max level
        self.currentSizeLevel = (self.currentSizeLevel % 3) + 1  # Cycle through 1 → 2 → 3
        self.circleScale = self.sizeLevels[self.currentSizeLevel]
        self.UpdateCircleSize()

    def DecreaseCircleSize(self):
        # Move to the previous size level, wrapping around if at the smallest level
        self.currentSizeLevel = (self.currentSizeLevel - 2) % 3 + 1  # Cycle through 3 → 2 → 1
        self.circleScale = self.sizeLevels[self.currentSizeLevel]
        self.UpdateCircleSize()

    def UpdateCircleSize(self):
        # Update the visual scale of the parent model
        self.parent.setScale(self.circleScale, self.circleScale, self.circleScale)

        # Set a fixed collision size (independent of visual scale)
        if hasattr(self, 'parentCollision'):
            fixedCollisionScale = 1.0  # Use a fixed size you are comfortable with
            self.parentCollision.setScale(fixedCollisionScale, fixedCollisionScale, fixedCollisionScale)


    def CameraDefense(self, loader, render):
        self.parent = loader.loadModel("./Assets/DroneDefender/Camera/sphere.egg")
        texture = loader.loadTexture("./Assets/DroneDefender/Camera/sphere1_flat.jpg")
        self.parent.setTexture(texture, 1)
        self.parent.setScale(self.circleScale, self.circleScale, self.circleScale)

        # Create and attach a collision sphere to the parent node
        from panda3d.core import CollisionNode, CollisionSphere
        self.parentCollision = self.parent.attachNewNode(CollisionNode('parent_collision'))

        # Use a separate scaling factor for the collider
        colliderScale = 0.1  # Adjust this value to make the collider smaller
        self.parentCollision.node().addSolid(CollisionSphere(0, 0, 0, 1))  # Keep the base radius at 1
        self.parentCollision.setScale(colliderScale, colliderScale, colliderScale)  # Scale down the collision node

        # Pass the parent to the defense paths
        defensePaths.Camera(render, self.parent, 'x-axis', 150, (255, 0, 0, 1.0), 'xy-circle')
        defensePaths.Camera(render, self.parent, 'y-axis', 115, (0, 255, 0, 1.0), 'yz-circle')
        defensePaths.Camera(render, self.parent, 'z-axis', 135, (0, 0, 255, 1.0), 'xz-circle')

    def DrawBaseballSeams(self, centralobject, droneName, step, numSeams, radius=1): 
        unitVec = defensePaths.BaseballSeams(step, numSeams, B=0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralobject.modelNode.getPos()

        # Create the drone instance
        drone = spaceJamClasses.Drone(
            self.loader,
            "./Assets/DroneDefender/DroneDefender.obj",
            self.render,
            droneName,
            "./Assets/DroneDefender/octotoad1_auv.png",
            position,
            5
        )

        # Track the drone in a list for BaseballSeams
        if not hasattr(self, 'baseballSeamsDrones'):
            self.baseballSeamsDrones = []  # Initialize if not already present
        self.baseballSeamsDrones.append(drone)

    def DrawCloudDefense(self, centralobject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralobject.modelNode.getPos()

        # Create the drone instance
        drone = spaceJamClasses.Drone(
            self.loader,
            "./Assets/DroneDefender/DroneDefender.obj",
            self.render,
            droneName,
            "./Assets/DroneDefender/octotoad1_auv.png",
            position,
            10
        )

        # Track the drone in a list for CloudDefense
        if not hasattr(self, 'cloudDefenseDrones'):
            self.cloudDefenseDrones = []  # Initialize if not already present
        self.cloudDefenseDrones.append(drone)

    def SetCamera(self):
        self.disableMouse()
        self.camera.reparentTo(self.Hero.modelNode)
        self.camera.setFluidPos(0, 0.3, 0)
        # self.camera.setPos(0, -30, 10) 
        # self.camera.lookAt(self.Hero.modelNode)
    
    def DroneSpawn(self):
        fullCycle = 60
        for j in range(fullCycle):
            # Increment drone count for unique names
            spaceJamClasses.Drone.droneCount += 1

            # Differentiate nicknames for CloudDefense and BaseballSeams
            cloudDroneNickName = "CloudDrone" + str(spaceJamClasses.Drone.droneCount)
            baseballDroneNickName = "BaseballDrone" + str(spaceJamClasses.Drone.droneCount)

            # Create drones for CloudDefense and BaseballSeams
            self.DrawCloudDefense(self.Planet1, cloudDroneNickName)
            self.DrawBaseballSeams(self.Planet4, baseballDroneNickName, j, fullCycle, 2)

    def EnableHUD(self):
        self.Hud = OnscreenImage(image = "./Assets/Hud/RainbowReticle.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

    def OrbitRocks(self, task):
        for i, rock in enumerate(self.rocks):
            # Each rock will orbit its assigned planet
            assignedPlanet = rock.assignedPlanet

            # Calculate the orbit based on the assigned planet
            angle = (task.time * 50 + i * (360 / len(self.rocks))) % 360  # Adjust speed (50) here
            radius = 300  # Keep radius consistent for all rocks
            x = assignedPlanet.modelNode.getX() + radius * math.cos(math.radians(angle))
            y = assignedPlanet.modelNode.getY() + radius * math.sin(math.radians(angle))
            z = assignedPlanet.modelNode.getZ()
            rock.modelNode.setPos(x, y, z)
        return Task.cont
    
    # Define the method inside your class
    def change_textures(self):
        # Define your texture sets as a list of dictionaries
        texture_sets = [
            {
                "Universe": "./Assets/Universe/starfield-in-blue.jpg",
                "Planet1": "./Assets/Planets/Preset 2/earthmap1k.jpg",
                "Planet2": "./Assets/Planets/Preset 2/jupitermap.jpg",
                "Planet3": "./Assets/Planets/Preset 2/mars_1k_color.jpg",
                "Planet4": "./Assets/Planets/Preset 2/mercurymap.jpg",
                "Planet5": "./Assets/Planets/Preset 2/saturnmap.jpg",
                "Planet6": "./Assets/Planets/Preset 2/venusmap.jpg",
                "SpaceStation1": "./Assets/SpaceStation/SpaceStation1_NM.png",
                "Rocks": "./Assets/Asteroids/pexels-eberhardgross-966927.jpg",
                "Drones": "./Assets/DroneDefender/TC.jpg"
            },
            {
                "Universe": "./Assets/Universe/photos_2017_7_14_fst_night-space-sky-milky-way.jpg",
                "Planet1": "./Assets/Planets/Preset 3/Icy.png",
                "Planet2": "./Assets/Planets/Preset 3/Icy.png",
                "Planet3": "./Assets/Planets/Preset 3/Icy.png",
                "Planet4": "./Assets/Planets/Preset 3/Icy.png",
                "Planet5": "./Assets/Planets/Preset 3/Icy.png",
                "Planet6": "./Assets/Planets/Preset 3/Icy.png",
                "SpaceStation1": "./Assets/SpaceStation/tex1_128x128_m_10cd6b068952bdd3_14.png",
                "Rocks": "./Assets/Asteroids/tex1_128x128_m_738980493bc209fb_14.png",
                "Drones": "./Assets/DroneDefender/2445651-2218407-box_celd.png"
            },
            {
                "Universe": "./Assets/Universe/jeremy-thomas-4dpAqfTbvKA-unsplash.jpg",
                "Planet1": "./Assets/Planets/Preset 1/2k_earth_daymap.jpg",
                "Planet2": "./Assets/Planets/Preset 1/2k_jupiter.jpg",
                "Planet3": "./Assets/Planets/Preset 1/2k_venus_surface.jpg",
                "Planet4": "./Assets/Planets/Preset 1/2k_neptune.jpg",
                "Planet5": "./Assets/Planets/Preset 1/2k_mars.jpg",
                "Planet6": "./Assets/Planets/Preset 1/2k_mercury.jpg",
                "SpaceStation1": "./Assets/SpaceStation/SpaceStation1_Dif2.png",
                "Rocks": "./Assets/Asteroids/10464_Asteroid_v1_diffuse.jpg",
                "Drones": "./Assets/DroneDefender/octotoad1_auv.png"
            }
        ]

        # Get the current texture set based on the counter
        current_textures = texture_sets[self.texture_set_index]

        # Apply the textures
        self.Universe.change_texture(current_textures["Universe"])
        self.Planet1.change_texture(current_textures["Planet1"])
        self.Planet2.change_texture(current_textures["Planet2"])
        self.Planet3.change_texture(current_textures["Planet3"])
        self.Planet4.change_texture(current_textures["Planet4"])
        self.Planet5.change_texture(current_textures["Planet5"])
        self.Planet6.change_texture(current_textures["Planet6"])
        self.SpaceStation1.change_texture(current_textures["SpaceStation1"])
        
        for rock in self.rocks:
            rock.change_texture(current_textures["Rocks"])

        if hasattr(self, 'baseballSeamsDrones'):
            for drone in self.baseballSeamsDrones:
                drone.change_texture(current_textures["Drones"])
        
        if hasattr(self, 'cloudDefenseDrones'):
            for drone in self.cloudDefenseDrones:
                drone.change_texture(current_textures["Drones"])
        
        self.Wanderer1.change_texture(current_textures["Drones"])
        self.Wanderer2.change_texture(current_textures["Drones"])
        
        if hasattr(self, "cloudDrones"):
            for drone in self.cloudDrones:
                drone.change_texture(current_textures["Drones"])
        
        if hasattr(self, "mlbDrones"):
            for drone in self.mlbDrones:
                drone.change_texture(current_textures["Drones"])

        # Cycle to the next texture set
        self.texture_set_index = (self.texture_set_index + 1) % len(texture_sets) 

    def changeTexture(self):
        # Get the current texture path
        texturePath = self.texture_paths[self.current_texture_index]
        
        # Load and set the texture
        new_texture = self.loader.loadTexture(texturePath)
        self.parent.setTexture(new_texture, 1)
        
        # Update the texture index to cycle through the list
        self.current_texture_index = (self.current_texture_index + 1) % len(self.texture_paths)

app = MyApp()
app.run()