# Evolutionary Robotics Homework
Feel free to work together in groups, but each of you should turn in your own evolved robot brain.

#### Only pass in values between -1 and 1 to the robot's `move` function. I will generate random move commands for any values outside that range!

## Description

#### I have provided you with code that generates a random environment with some walls evenly spaced along the length of the world. I will test your robot in many randomly generated environments, so it makes sense to evolve your robots in a similarly randomly generated world (that keeps changing). 

#### The goal of this assignment is to evolve a robot that gets as close to the light source as you can within 500 steps of the simulator using an evolved controller. 
Note that trying to evolve something using 500 steps from the very begening will take a looonnnggg time (so I don't reccomend it). 

You should feel free to manipulate the fitness function, selection methods, recombination, diversity maintenance, and the structure of the neural network brain to evolve better robots. 

You may also use genetic programing to evolve a brain for this robot, in which case you'll want to also change the kinds of function nodes available to evolution.

## Evaluation (10 points)
For each *non-trivial* feature (i.e., more than changing a variable like `population_size`) you implement, you will get 2 points. 

If you evolve a robot that is able to find the light source within 500 steps (in most randomly generated environments), you will automatically get 8 points. 

If you succesfully use/implement one of the advanced approaches we learned about in class (e.g., NEAT, HyperNEAT, Novelty Search, etc.) you will also get an automatic 8 points. 

This means you could implement only one non-trivial feature, but it works so well that you nearly always find the light source, you'll get full points. Alternatively, you could implement 5 additional features, and even though you may not have evolved a solution that finds the light consistently, you will still get full points. 

If you score more than 10 points on this assignment, I will award the extra points as half extra credit. For example, if you get 16/10, you will get 6/2 points as extra credit.

