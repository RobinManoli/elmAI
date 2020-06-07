# on certain computers elmaphys is not loadable outside its own dir, so load benchmark from here
import sys
sys.path.append("agents")
import benchmark as b

episodes = int( sys.argv[1] ) if len(sys.argv) > 1 and sys.argv[1].isnumeric else 1000
seed = int( sys.argv[2] ) if len(sys.argv) > 2 and sys.argv[2].isnumeric else None

#b.elmaphys_only()
#b.elmaphys_using_step()
b.elmaphys_ribot_algorithm(episodes, seed)