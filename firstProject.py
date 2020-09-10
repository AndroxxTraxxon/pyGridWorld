from gridworld.actor import ActorWorld, Bug, Rock

if __name__ == "__main__":
    world = ActorWorld()
    world.add(Bug())
    world.add(Rock())
    world.show()