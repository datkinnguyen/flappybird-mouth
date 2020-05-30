# FlappyBird Mouth

FlappyBird Mouth game is a Flinders Univeristy assignment for Image Processing topic, written in Python using image processing techniques to detect mouth and mouth open/close states to control the game play.

This project focuses on the Image processing part, the game Flappy Bird is just to demo the Image processing part.
The code for Gameplay of FlappyBird is based on https://github.com/0-whatsis-1/FlappyBird-using-Eye-Blink.

In this project, dlib's face detector(HOG-based) is used to detect player's face and the facial landmark predictor is used to detects mouth of the player. Then a mouth aspect ratio will be calculated to detect if the mouth is in OPEN or CLOSE state. If in OPEN state, the game will trigger a jump action of the bird.

Video demo : https://youtu.be/1dysqhl6hMw<br/>

<br/>
<a href="http://www.youtube.com/watch?feature=player_embedded&v=1dysqhl6hMw
" target="_blank"><img src="http://img.youtube.com/vi/1dysqhl6hMw/0.jpg" 
alt="FlappyMouth" width="480" height="320" border="10" /></a>

<br/>
Usage:<br/>

- First run command below to install dependencies
`pip install -r requirements.txt`

- Run the file main.py in the terminal 
`python main.py`
or run file main.py from any python IDE.

Any questions, please contact Tien Dat Nguyen (nguy1025@flinders.edu.au).
