import os

import gym
from stable_baselines3 import PPO

models_dir = "models/PPO"

os.makedirs(models_dir, exist_ok=True)

env = gym.make("LunarLander-v2")
env.reset()

model = PPO.load(f"{models_dir}/170000.zip")

for ep in range(10):
    obs = env.reset()
    done = False

    while not done:
        env.render()
        action, _ = model.predict(obs)
        obs, reward, done, info = env.step(action)

env.close()
