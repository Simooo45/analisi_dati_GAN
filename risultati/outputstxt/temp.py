from plotter import n_connections

n_conn = n_connections(533, [200, 1024, 16], 1)

for l1 in range(50, 2000, 50):
   for l2 in range(50, 2000, 100):
      for l3 in range(50, 2000, 100):
         if n_connections(533, [l1, l2, l3], 1) < (n_conn):
            print(f"{l1},{l2},{l3}")