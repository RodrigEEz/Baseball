import sqlite3
import numpy as np
import io
import time
import functions

select = """
            SELECT 
                PLAYER_ID,
                PITCHING_DISTRIBUTION
            FROM 
                PITCHER_STATS
        """

values = functions.execute_select(select)
first_pitcher = np.random.multivariate_normal((0,0), ((80,0), (0,80)), 100) 
second_pitcher = np.random.multivariate_normal((0,0), ((80,0), (0,80)), 100) 

np.save('pitching_distributions/PLAYER_1.npy', first_pitcher)

np.save('pitching_distributions/PLAYER_10.npy', second_pitcher)
