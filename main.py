import cv2
import numpy as np
import dlib
import pygame
import random
import imutils
import math
from imutils.video import VideoStream

# CONSTANTS ------------------------

SHAPE_DETECTOR = "shape_predictor_68_face_landmarks.dat"  # Face landmarks data file using for shape detector
MAR_THRESHOLD = 1.5  # Ratio to detect if mouth is opened
MAR_CONSECUTIVE_FRAMES = 3  # Number of consecutive frames the mouth must be above for considered action taken

# Indexes of the facial landmarks for the mouth
(MOUTH_LM_INDEX_START, MOUTH_LM_INDEX_END) = (48, 68)

# UI Configurations
FONT = cv2.FONT_HERSHEY_SIMPLEX
PREVIEW_TEXT_COLOUR = (0, 255, 255)
PREVIEW_MOUTH_COLOUR = (0, 255, 0)
GAME_SCORE_TEXT_COLOUR = (255, 255, 255)
GAME_BG_COLOUR = (212, 182, 115)

# Game Control
JUMP_HEIGHT = 17
JUMP_GRAVITY = 5
JUMP_SPEED = 10
BIRD_Y_DEFAULT = 150
BIRD_X = 70
WALL_GAP = 220


# HELPER FUNCTIONS ------------------------

# Convert landmark shape to numpy array
def landmark_shape_to_np(lm_shape):
	# initialize the list of (x, y)-coordinates
	coordinates = np.zeros((lm_shape.num_parts, 2), dtype="int")

	# convert all facial landmarks to tuples of (x, y)-coordinates
	for i in range(0, lm_shape.num_parts):
		coordinates[i] = (lm_shape.part(i).x, lm_shape.part(i).y)

	return coordinates


# Calculate euclidean distance between 2 points
def distance(point1, point2):
	dx = point1[0] - point2[0]
	dy = point1[1] - point2[1]
	return math.sqrt(dx * dx + dy * dy)


# Calculate mouth aspect ratio
def mouth_aspect_ratio(mouth_landmarks):
	# calculate the vertical distances of 2 vertical mouth landmarks
	vertical1_d = distance(mouth_landmarks[2], mouth_landmarks[10])  # indexes 51, 59
	vertical2_d = distance(mouth_landmarks[4], mouth_landmarks[8])  # indexes 53, 57

	# calculate the horizontal distance of horizontal mouth landmarks
	horizontal_d = distance(mouth_landmarks[0], mouth_landmarks[6])  # indexes 49, 55

	# calculate the mouth aspect ratio
	mar = (vertical1_d + vertical2_d) / horizontal_d
	return mar


# Draw text on image
def draw_text(image, text, origin, colour):
	cv2.putText(image, text, origin, FONT, 0.7, colour, 2)


# MAIN GAME LOGIC ------------------------

class FlappyBird:
	def __init__(self):
		self.screen = pygame.display.set_mode((500, 800))
		self.bird = pygame.Rect(65, 50, 50, 50)
		self.background = pygame.image.load("images/bg.png").convert()
		self.birdSprites = [pygame.image.load("images/1.png").convert_alpha(),
							pygame.image.load("images/2.png").convert_alpha(),
							pygame.image.load("images/dead.png")]
		self.wallUp = pygame.image.load("images/bottom.png").convert_alpha()
		self.wallDown = pygame.image.load("images/top.png").convert_alpha()
		self.gap = WALL_GAP
		self.wallx = 400
		self.birdY = BIRD_Y_DEFAULT
		self.jump = 0
		self.jumpSpeed = JUMP_SPEED
		self.gravity = JUMP_GRAVITY
		self.dead = False
		self.sprite = 0
		self.counter = 0
		self.offset = random.randint(-110, 110)

	def updateWalls(self):
		self.wallx -= 2
		if self.wallx < -80:
			self.wallx = 400
			self.counter += 1
			self.offset = random.randint(-110, 110)

	def birdUpdate(self):
		if self.jump:
			self.jumpSpeed -= 1
			self.birdY -= self.jumpSpeed
			self.jump -= 1
		else:
			self.birdY += self.gravity
			self.gravity += 0.15
		self.bird[1] = int(self.birdY)
		wall_up_react = pygame.Rect(self.wallx, 360 + self.gap - self.offset + 10, self.wallUp.get_width() - 10,
									self.wallUp.get_height())
		wall_down_react = pygame.Rect(self.wallx, 0 - self.gap - self.offset - 10, self.wallDown.get_width() - 10,
									  self.wallDown.get_height())
		if wall_up_react.colliderect(self.bird):
			self.dead = True
		if wall_down_react.colliderect(self.bird):
			self.dead = True
		if not 0 < self.bird[1] < 720:
			self.bird[1] = BIRD_Y_DEFAULT
			self.birdY = BIRD_Y_DEFAULT
			self.dead = False
			self.counter = 0
			self.wallx = 400
			self.offset = random.randint(-110, 110)
			self.gravity = JUMP_GRAVITY

	def run(self):
		counter_consec_frame = 0  # Consecutive Frame counter
		total_open = 0  # total number of mouth opens

		# Initialize dlib's face detector(HOG-based) & then create the facial landmark predictor
		detector = dlib.get_frontal_face_detector()
		predictor = dlib.shape_predictor(SHAPE_DETECTOR)

		# Start the video stream thread
		vs = VideoStream(src=0).start()

		clock = pygame.time.Clock()
		pygame.font.init()
		game_font = pygame.font.SysFont("Arial", 50)

		game_over = False
		while not game_over:
			# Capture the frame from the threaded video stream, resize it & convert it to grayscale
			frame = vs.read()
			# Resize image smaller for easier processing
			frame = imutils.resize(frame, width=450)

			# Convert colour image to grayscale image for face detection
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			# Detect faces in the grayscale frame
			rects = detector(gray, 0)
			count_face = len(rects)
			if count_face == 0:
				draw_text(frame, "No face detected".format(len(rects)), (10, 30), PREVIEW_TEXT_COLOUR)
			elif count_face > 1:
				draw_text(frame, "Only support 1 face. Detected {0} faces".format(count_face), (10, 30),
						  PREVIEW_TEXT_COLOUR)
			else:
				rect = rects[0]
				# Extract the shape of the face from the gray image by its detected rectangle
				shape = predictor(gray, rect)
				shape = landmark_shape_to_np(shape)

				# Extract the mouth coordinates
				mouth = shape[MOUTH_LM_INDEX_START:MOUTH_LM_INDEX_END]

				# Compute the convex hull for the mouth
				hull = cv2.convexHull(mouth)

				# Draw the mouth shape on the colour image
				cv2.drawContours(frame, [hull], -1, PREVIEW_MOUTH_COLOUR, 1)

				# Calculate mouth aspect ratio + show on the colour image
				mar = mouth_aspect_ratio(mouth)
				draw_text(frame, "Mouth Aspect Ratio: {:.2f}".format(mar), (10, 30), PREVIEW_TEXT_COLOUR)

				# print("counter_consec_frame: {0}, isDead: {1}".format(counter_consec_frame, self.dead))

				# Draw text if mouth is open
				if mar < MAR_THRESHOLD:
					counter_consec_frame += 1  # Increment the frame counter
				else:
					# If the mouth is opened for a number of frames and game is not over, jump the bird
					draw_text(frame, "Mouth OPEN", (10, 60), PREVIEW_TEXT_COLOUR)
					if counter_consec_frame >= MAR_CONSECUTIVE_FRAMES and not self.dead:
						total_open += 1  # Increment the total number of blinks
						self.jump = JUMP_HEIGHT
						self.gravity = JUMP_GRAVITY
						self.jumpSpeed = JUMP_SPEED

					# Reset the frame counter
					counter_consec_frame = 0

			# Show the camera image with mouth shape detected to a window
			cv2.imshow("Flappy Bird", frame)
			clock.tick(60)

			# Draw background and walls (pipes)
			self.screen.fill(GAME_BG_COLOUR)
			self.screen.blit(self.background, (0, 0))
			self.screen.blit(self.wallUp, (self.wallx, 360 + self.gap - self.offset))
			self.screen.blit(self.wallDown, (self.wallx, 0 - self.gap - self.offset))

			# Draw score
			self.screen.blit(game_font.render(str(self.counter), -1, GAME_SCORE_TEXT_COLOUR), (250, 50))

			# Draw bird with its status/action
			if self.dead:
				self.sprite = 2
			elif self.jump:
				self.sprite = 1
			self.screen.blit(self.birdSprites[self.sprite], (BIRD_X, int(self.birdY)))

			if not self.dead:
				self.sprite = 0

			# Update walls positions
			self.updateWalls()

			# Update current bird info + check if game over by colliding with walls or hit top/bottom of screen
			self.birdUpdate()

			# Update main game screen display
			pygame.display.update()

			# Listen to key event, and quit game if user pressed "q"
			key = cv2.waitKey(1) & 0xFF
			if key == ord('q'):
				game_over = True

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					game_over = True

		# End Game loop, clean up resources
		cv2.destroyAllWindows()
		vs.stop()


if __name__ == "__main__":
	FlappyBird().run()
