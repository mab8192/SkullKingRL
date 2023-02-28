import random
import time
from collections import deque

import cv2
import gym
import numpy as np
from gym import spaces

SNAKE_LEN_GOAL = 30


def collision_with_apple(apple_position, score):
    apple_position = [random.randrange(1,50)*10,random.randrange(1,50)*10]
    score += 1
    return apple_position, score

def collision_with_boundaries(snake_head):
    if snake_head[0]>=500 or snake_head[0]<0 or snake_head[1]>=500 or snake_head[1]<0 :
        return 1
    else:
        return 0

def collision_with_self(snake_position):
    snake_head = snake_position[0]
    if snake_head in snake_position[1:]:
        return 1
    else:
        return 0


class SnakeEnv(gym.Env):
    metadata = {'render_modes': ["human"]}

    def __init__(self) -> None:
        super(SnakeEnv, self).__init__()

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=-500, high=500, shape=(5 + SNAKE_LEN_GOAL,), dtype=np.float32)

    def reset(self):
        self.done = False
        self.reward = 0

        self.grid = np.zeros((500,500,3),dtype='uint8')

        # Initial Snake and Apple position
        self.snake_positions = [[250,250],[240,250],[230,250]]
        self.apple_position = [random.randrange(1,50)*10,random.randrange(1,50)*10]

        self.score = 0
        self.prev_button_direction = 1
        self.button_direction = 1
        self.snake_head = [250, 250]

        self.prev_actions = deque(maxlen=SNAKE_LEN_GOAL)  # Needs to be fixed length
        for _ in range(SNAKE_LEN_GOAL):
            self.prev_actions.append(-1)

        return self.observation

    def step(self, action):
        self.prev_actions.append(action)

        cv2.imshow('a', self.grid)
        cv2.waitKey(1)
        self.grid = np.zeros((500,500,3),dtype='uint8')
        # Display Apple
        cv2.rectangle(self.grid,(self.apple_position[0],self.apple_position[1]),(self.apple_position[0]+10,self.apple_position[1]+10),(0,0,255),3)
        # Display Snake
        for position in self.snake_positions:
            cv2.rectangle(self.grid,(position[0],position[1]),(position[0]+10,position[1]+10),(0,255,0),3)

        # Change the head position based on the button direction
        if action == 1:
            self.snake_head[0] += 10
        elif action == 0:
            self.snake_head[0] -= 10
        elif action == 2:
            self.snake_head[1] += 10
        elif action == 3:
            self.snake_head[1] -= 10

        # Increase Snake length on eating apple
        if self.snake_head == self.apple_position:
            self.apple_position, self.score = collision_with_apple(self.apple_position, self.score)
            self.snake_positions.insert(0,list(self.snake_head))

        else:
            self.snake_positions.insert(0,list(self.snake_head))
            self.snake_positions.pop()

        # On collision kill the snake and print the score
        if collision_with_boundaries(self.snake_head) == 1 or collision_with_self(self.snake_positions) == 1:
            font = cv2.FONT_HERSHEY_SIMPLEX
            self.grid = np.zeros((500,500,3),dtype='uint8')
            cv2.putText(self.grid, 'Your Score is {}'.format(self.score),(140,250), font, 1,(255,255,255),2,cv2.LINE_AA)
            cv2.imshow('a', self.grid)
            self.done = True

        if self.done:
            self.reward = -10
        else:
            self.reward = self.score*10

        return self.observation, self.reward, self.done, {}

    @property
    def observation(self):
        # Feature engineering!
        # head_x, head_y, apple_delta_x, apple_delta_y, snake_length, previous moves
        head_x = self.snake_head[0]
        head_y = self.snake_head[1]
        apple_delta_x = self.apple_position[0] - head_x
        apple_delta_y = self.apple_position[1] - head_y
        snake_length = len(self.snake_positions)

        obs = [head_x, head_y, apple_delta_x, apple_delta_y, snake_length] + list(self.prev_actions)
        obs = np.array(obs)
        return obs.astype(np.float32)
