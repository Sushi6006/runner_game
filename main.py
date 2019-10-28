# runner_game/main.py
# Terry

from tkinter import *
from random import randint


# GUI - Managing the window, root
class GUI:

	# Height and width of the window
	WIDTH = 600
	HEIGHT = 400
	FONT = ("Courier", 40)
	# The program looks nicer in this way
	PACK_PADDING = 80

	def __init__(self):

		# Create the window
		self.root = Tk()
		self.root.title("Jumping Square")
		self.root.geometry("{}x{}".format(self.WIDTH, self.HEIGHT))
		self.root.resizable(False, False)

		# Screens of the program
		self.menu = MenuScreen(self.root, self)
		self.game = None  # Create the game later

		# Start with the menu screen
		self.switch_screen("init")

		self.root.mainloop()

	# Switch screen between game and menu
	def switch_screen(self, o_win):
		if o_win == "menu":  # If the original window is menu
			self.menu.main_frame.pack_forget()
			self.game = GameScreen(self.root, self)  # Create a new game
			self.bind_keys("game")  # Bind keys
			self.game.main_frame.pack()
		elif o_win == "game":  # If the original window is game
			self.game.main_frame.pack_forget()
			self.bind_keys("menu")  # Unbind keys
			self.menu.main_frame.pack(pady=self.PACK_PADDING)
		elif o_win == "init":
			self.bind_keys("menu")
			self.menu.main_frame.pack(pady=self.PACK_PADDING)  # Just pack the menu if there are nothing on the screen

	# Bind keys - True = bind; False = unbind (space, return, mouse left button, up)
	def bind_keys(self, b):
		# self.root.bind_all('<Tab>', self.nothing)  # Disable tab selection which causes error
		if b == "game":  # Keybinding for game screen
			self.root.bind_all('<space>', self.tapped)
			self.root.bind_all('<Return>', self.tapped)
			self.root.bind_all('<Button-1>', self.tapped)
			self.root.bind_all('<Up>', self.tapped)
		elif b == "menu":  # Keybinding for menu screen
			# Start when the spacebar / return is pressed, does the same thing as the button
			self.root.bind_all('<space>', lambda event: self.menu.start())
			self.root.bind_all('<Return>', lambda event: self.menu.start())
			# self.root.unbind('<space>')
			# self.root.unbind('<Return>')
			self.root.unbind('<Button-1>')
			self.root.unbind('<Up>')
		else:  # Keybinding for end game screen
			#self.root.bind_all('<space>', self.nothing)
			#self.root.bind_all('<Return>', self.nothing)
			self.root.unbind('<space>')
			self.root.unbind('<Return>')
			self.root.unbind('<Button-1>')
			self.root.unbind('<Up>')

	# Jump / Start game
	def tapped(self, event):
		if len(self.game.spikes) == 0:  # If the game has not started, start the game
			self.game.start_moving()
		# print("tapped", self.game.ball.on_line(), self.game.ball.y_vel)
		if self.game.ball.y_vel == 0 and self.game.ball.on_line():  # Jump only when the ball is on the line
			self.game.canv.itemconfig(self.game.ball.ball, fill="#%06x" % randint(0, 0xFFFFFF))  # Change the colour of the square everytime it jumps
			self.game.ball.y_vel = Ball.INIT_V  # Jump


class MenuScreen:
	def __init__(self, window, gui_object):
		self.root = window
		self.gui_object = gui_object

		# Stuff on the menu screen
		self.main_frame = Frame(self.root)
		self.title = Label(self.main_frame, text="Jumping Square", font=GUI.FONT)
		self.start_button = Button(self.main_frame, text="Start", command=self.start, takefocus=0)
		self.title.pack(pady=20)
		self.start_button.pack(pady=20)

	# Start the game
	def start(self):
		self.gui_object.switch_screen("menu")


# GameScreen - In where the animations of the game is happening
class GameScreen:

	BASE_Y = GUI.HEIGHT - 50  # 50px from the bottom
	MIN_D = 130  # Minimum distance between spikes
	MAX_D = 250  # Maximum ...

	def __init__(self, window, gui_object):
		# Main game screen objects
		self.root = window
		self.gui_object = gui_object
		self.main_frame = Frame(self.root)
		self.canv = Canvas(self.main_frame, width=GUI.WIDTH, height=GUI.HEIGHT)
		self.canv.pack()
		"""
		# Testing switch_screen()
		test_button = Button(self.main_frame, text="Test", command=lambda: self.gui_object.switch_screen("game"))
		test_button.pack()
		"""
		# Main in-game objects
		self.ball = Ball(self.canv)  # It's a square
		self.spikes = []  # List of spikes
		self.d_in_spikes = randint(self.MIN_D, self.MAX_D)  # Distance between each spike

		# Other objects
		line_coooooooord = [0, self.BASE_Y, GUI.WIDTH, self.BASE_Y]
		self.line = self.canv.create_line(*line_coooooooord, width=2, fill="black")
		slp = 40  # Score label paddings
		self.score = 0
		self.score_label = self.canv.create_text(GUI.WIDTH - slp, slp, anchor="ne", text=str(self.score), font=GUI.FONT)

		# For canceling root.after()
		self.a = False

	# Start the game
	def start_moving(self):
		self.a = self.root.after(16, self.move_objects)  # Start looping
		self.spawn_spikes()  # Spawn the first spike

	# Move everything
	def move_objects(self):

		# print("Looping")

		# Spikes
		for spike in self.spikes:
			spike.move()
		if GUI.WIDTH - self.spikes[-1].get_rx() >= self.d_in_spikes:  # Spawn spikes after a distance
			self.spawn_spikes()  # Spawn next spike
			self.d_in_spikes = randint(self.MIN_D, self.MAX_D)  # Re-randomise the distance between before next spike
		if self.spikes[0].get_rx() <= 0:  # If the spike is out of the window, delete the spike
			self.spikes[0].destroy()
			self.spikes.pop(0)

		# Ball
		self.ball.move()
		if not self.ball.above_line():  # If the ball falls below the line, move it back and set the velocity to 0
			self.canv.move(self.ball.ball, 0, self.BASE_Y - self.canv.coords(self.ball.ball)[3])
			self.ball.y_vel = 0

		# Set score
		self.score += 0.05  # Add 0.05/16ms
		self.canv.itemconfig(self.score_label, text=str(int(self.score)))  # Change the score

		self.a = self.root.after(16, self.move_objects)  # Loop

		# Check collision
		if self.spikes[0].spike in self.canv.find_overlapping(*self.canv.coords(self.ball.ball)):
			self.end_game(int(self.score))  # End the game

	def spawn_spikes(self):  # Spawn one spike (could be 2 in 1 ^^ or 3 in 1 ^^^)
		self.spikes.append(Spike(self.canv))

	def end_game(self, current_score):

		def go_menu():  # Go to menu after game finishes
			self.gui_object.switch_screen("game")

		# print("Stop looping")
		self.root.after_cancel(self.a)  # Stop looping (window.after)
		self.canv.pack_forget()  # Unpack the canvas
		self.gui_object.bind_keys("end game")  # Unbind & bind the keys for end game screen

		# Game over screen - title, score, and continue button
		end_screen = Frame(self.main_frame)
		end_screen.pack(pady=GUI.PACK_PADDING)
		go_label = Label(end_screen, text="Game Over\nScore: {}".format(current_score), font=GUI.FONT)  # game over label
		continue_button = Button(end_screen, text="Continue", command=go_menu, takefocus=0)  # Continue button, goes to menu once clicked
		go_label.pack(pady=20)
		continue_button.pack(pady=20)


# A rectangle with a dream of becoming a circle; that is why it is called "Ball"
class Ball:

	RADIUS = 15
	GRAVITY = 1
	X_POS = 50  # How many pixels from the left edge
	INIT_V = -15  # Move up by 20px

	def __init__(self, canvas):
		self.canv = canvas
		# Coords of the ball
		ball_coord = [self.X_POS, GameScreen.BASE_Y - 2 * self.RADIUS, self.X_POS + 2 * self.RADIUS, GameScreen.BASE_Y]  # Init coord of the ball
		self.ball = self.canv.create_rectangle(*ball_coord, fill="black", width=0)
		self.y_vel = 0

	# Return True if the ball is above the line
	def above_line(self):
		return self.canv.coords(self.ball)[3] < GameScreen.BASE_Y

	# Return True if the ball is on the line
	def on_line(self):
		return self.canv.coords(self.ball)[3] == GameScreen.BASE_Y

	def move(self):
		self.canv.move(self.ball, 0, self.y_vel)
		if self.above_line():  # Change the velocity
			self.y_vel += self.GRAVITY


class Spike:

	ST_HEIGHT = 30  # Standard height of spikes, long spikes = 2 * length of standard height
	WIDTH = 10  # Half of the width of spikes
	MAX_NUM = 3  # Maximum 3 spikes in one group (connected to each other)
	VEL = -4  # Moving to the left at the speed of 4px/frame

	def __init__(self, canvas):
		self.canv = canvas
		# Set the amount of spikes in one group of spikes
		number = randint(1, 3)  # Randonise the number of spikes in one group
		coords = [GUI.WIDTH, GameScreen.BASE_Y]  # First point
		# Besides the starting point, every 2 points create one spike
		for i in range(number):
			coords.append(GUI.WIDTH + (i * 2 + 1) * self.WIDTH)  # x2 (top)
			coords.append(GameScreen.BASE_Y - randint(1, 2) * self.ST_HEIGHT)  # y2 (top)
			coords.append(GUI.WIDTH + (i + 1) * 2 * self.WIDTH)  # x3 (bottom right)
			coords.append(GameScreen.BASE_Y)  # y3 (bottom right)
		self.spike = self.canv.create_polygon(*coords)  # Create the group of spikes

	# Get the x coordinates of the right / left side of the spikes
	def get_rx(self):
		return self.canv.coords(self.spike)[2]

	def move(self):
		self.canv.move(self.spike, self.VEL, 0)

	# Delete the group of spikes from the canvas
	def destroy(self):
		self.canv.delete(self.spike)


GUI()
