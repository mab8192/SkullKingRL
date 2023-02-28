import os

from env import SnakeEnv
from stable_baselines3 import PPO

models_dir = "models/Snake"
log_dir = "logs"

os.makedirs(models_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

env = SnakeEnv()
env.reset()

model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=log_dir)
TIMESTEPS = 10000
for i in range(1, 30):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{models_dir}/{TIMESTEPS*i}")

env.close()
