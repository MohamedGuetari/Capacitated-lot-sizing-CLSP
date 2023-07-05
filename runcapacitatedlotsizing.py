
import gurobipy as gp
from gurobipy import GRB
import readIn


def solve_CLSP(test_file_name):
    # The following are the indices and parameters that we are going to use
    # N number of products
    # T number of macro periods
    # M number of machines
    # K: K number of tools
    # h: holding cost
    # b: penalty cost for the backlog of product i of T
    # sigma: setup cost for changeover
    # d: demand of product i at period T
    # I0: initial inventory level of product
    # c: time for producing one unit of product i on machine m using tool k
    # s: setup time for changeover
    # R: production of product i produced in period t on machine m with tool k
    # S: set of possible tools that can be used for product i
    # alpha0: initial setup statement

    N, T, M, K, h, b, sigma, d, I0, c, s, R, S, alpha0 = readIn.readFile(test_file_name)

    micro_period = 10    # We choose this value on our own and change it to test different values

    # We start by defining the model
    model = gp.Model("CLSP")


    # GLSP variables

    # Then we add the decision variables (the ones for GLSP)

    Bit = {}      # Backlog of product i at the end of macro-period t
    Iit = {}      # Inventory level of product i at the end of macro-period t
    ustrmk = {}   # Start time of micro-period r in macro-period t on machine m
    ufrmk = {}    # Release time of the tool used in micro-period r in macro-period t on machine m
    Utrmr0 = {}   # 1 if in macro-period t micro-period r on machine m starts after micro-period r0 of machine m0, 0 otherwise
    xitrmk = {}   # Production quantity of product i on machine m in macro-period t during micro-period r using tool k
    ytrmk = {}    # 1 if tool k is attached to machine m in macro-period t during micro-period r, 0 otherwise
    ztrmkl = {}   # 1 if there is a switch from tool k to tool l on machine m in macro-period t during micro-period r

    # Add variables to the model
    for i in range(N):
        for t in range(T):
            Bit[i, t] = model.addVar(N,T,vtype=gp.GRB.CONTINUOUS, obj=b[i][t], name=f"Bit_{i}_{t}")
            Iit[i, t] = model.addVar(vtype=gp.GRB.CONTINUOUS, obj=I0[i], name=f"Iit_{i}_{t}")
        for m in range(M):
            for m0 in range(M):
                for r in range(micro_period):
                    if m==m0:
                        continue
                    else:
                        ustrmk[t, m, r] = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f"ustrmk_{t}_{m}_{r}")
                        ufrmk[t, m, r] = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f"ufrmk_{t}_{m}_{r}")
                        Utrmr0[t, m, r, m0] = model.addVar(vtype=gp.GRB.BINARY, name=f"Utrmr0_{t}_{m}_{r}_{m0}")
                        for k in range(K):
                            xitrmk[t, r, m, k] = model.addVar(vtype=gp.GRB.CONTINUOUS, name=f"xitrmk_{t}_{r}_{m}_{k}")
                            ytrmk[t, r, m, k] = model.addVar(vtype=gp.GRB.BINARY, name=f"ytrmk_{t}_{r}_{m}_{k}")
                            for l in range(K):
                                ztrmkl[t, r, m, k, l] = model.addVar(vtype=gp.GRB.BINARY, name=f"ztrmkl_{t}_{r}_{m}_{k}_{l}")


    # Here we define the additional decision variables for CLSP
    stmk = {}   # Start time of tool attachment of tool k to machine m in period t
    ftmk = {}   # End time of tool exchange where tool k is removed from machine m in period t
    maxtm = {}  # End time of the last tool exchange performed on machine m in period t
    Xitmk = {}  # Production of product i produced in period t on machine m with tool k
    tmk = {}    # 1 if tool k is attached to machine m at the beginning of period t, 0 otherwise
    Ttmkl = {}  # 1 if there is a switch from tool k to l on machine m in period t, 0 otherwise
    Wtmm0k = {}  # 1 if tool k is used on machine m after being used on machine m0 in period t, 0 otherwise

    # We add variables to the model
    for t in range(T):
        for m in range(M):
            for k in range(K):
                stmk[t, m, k] = model.addVar(vtype=gp.GRB.CONTINUOUS, obj=s[m][t][k], name=f"stmk_{t}_{m}_{k}")
                ftmk[t, m, k] = model.addVar(vtype=gp.GRB.CONTINUOUS, obj=s[m][t][k], name=f"ftmk_{t}_{m}_{k}")
                maxtm[t, m] = model.addVar(vtype=gp.GRB.CONTINUOUS, obj=s[m][t][K-1] + sigma[m][t][K-1], name=f"maxtm_{t}_{m}")
                for i in range(N):
                    Xitmk[i, t, m, k] = model.addVar(vtype=gp.GRB.CONTINUOUS, obj=S[i][m][t], name=f"Xitmk_{i}_{t}_{m}_{k}")
                tmk[t, m, k] = model.addVar(vtype=gp.GRB.BINARY, name=f"tmk_{t}_{m}_{k}")
                for l in range(K):
                    Ttmkl[t, m, k, l] = model.addVar(vtype=gp.GRB.BINARY, name=f"Ttmkl_{t}_{m}_{k}_{l}")
                for m0 in range(M):
                    Wtmm0k[t, m, m0, k] = model.addVar(vtype=gp.GRB.BINARY, name=f"Wtmm0_{t}_{m}_{m0}_{k}")

    #Then we define Objective function-----------------------------------------------

    obj = (gp.quicksum((h[i][t] * Iit[i, t]) + b[i][t] * Bit[i, t]
                       for t in range(T) for i in range(N))
           + gp.quicksum(sigma[m][k][l] * Ttmkl[t, m, k, l]
                         for t in range(T) for m in range(M)
                         for k in range(K) for l in range(K)))
    model.setObjective(obj, GRB.MINIMIZE)
    #-Here we start adding the constraints-----------------------------------------------
    for i in range(N): # constraint (19)
        for t in range(T):
            if t-1 > 0:
                model.addConstr(Iit[i, t] - Bit[i, t] - Iit[i, t-1] + Bit[i, t-1]
                            - gp.quicksum(Xitmk[i,t, m, k] for m in range(M) for k in range(K))
                            + d[i][t] == 0)

    for i in range(N): # constraint (20)
        for t in range(T):
            for m in range(M):
                for k in range(K):
                    model.addConstr(c[i][m][k] * Xitmk[i, t, m, k]
                            <= gp.quicksum(Ttmkl[t, m, l, k] + tmk[t, m, k] for l in range(K)))

    for t in range(T): # constraint (21)
        for m in range(M):
            model.addConstr(gp.quicksum(tmk[t, m, k] for k in range(K)) == 1)

    for t in range(T): # constraint (22)
        for k in range(K):
            model.addConstr(gp.quicksum(tmk[t, m, k] for m in range(M)) <= 1)

    for t in range(T-1): # constraint (23)
        for m in range(M):
            for k in range(K):
                    model.addConstr(gp.quicksum(Ttmkl[t, m, l, k] + tmk[t, m, k] for l in range(K)) == gp.quicksum(Ttmkl[t, m, l, k] + tmk[t+1, m, k] for l in range(K)))

    for t in range(T-1): # constraint (24)
        for m in range(M):
            for k in range(K):
                for l in range(K):
                    model.addConstr(ftmk[t, m, k] - s[m][k][l] * Ttmkl[t, m, k, l] + Ttmkl[t, m, k, l] - 1 - tmk[t+1, m, l] <= stmk[t, m, l] )

    for t in range(T-1): # constraint (25)
        for m in range(M):
            for k in range(K):
                for l in range(K):
                    model.addConstr(ftmk[t, m, k] - s[m][k][l] * Ttmkl[t, m, k, l] + Ttmkl[t, m, k, l] - 1 - tmk[t+1, m, l] >= stmk[t, m, l] + Ttmkl[t, m, k, l] - 1 - tmk[t+1, m, l])

    for t in range(T-1): # (26)
            for m in range(M):
                for k in range(K):
                    model.addConstr(stmk[t, m, k] + gp.quicksum(c[i][m][k] * Xitmk[i, t, m, k] for i in range(N)) + gp.quicksum(s[m][k][l] * Ttmkl[t, m, l, k] + s[m][k][l] * Ttmkl[t, m, k, l] -  tmk[t+1, m, k] for l in range(K)) <= ftmk[t, m, k])

    for t in range(T): # constraint (27)
            for m in range(M):
                for k in range(K):
                    model.addConstr(stmk[t, m, k] + gp.quicksum(c[i][m][k] * Xitmk[i, t, m, k] for i in range(N)) + gp.quicksum(s[m][k][l] * Ttmkl[t, m, k, l] for l in range(K)) <= ftmk[t, m, k])

    for t in range(T): # constraint (28)
            for m in range(M):
                for k in range(K):
                    model.addConstr(stmk[t, m, k] <= 1- tmk[t, m, k])

    for t in range(T-1): # constraint (29)
            for m in range(M):
                for k in range(K):
                    model.addConstr(ftmk[t, m, k] >= tmk[t +1, m, k] - gp.quicksum(Ttmkl[t, m, l, k] for l in range(K)))

    for t in range(T): # constraint (30)
        for m in range(M):
            for m0 in range(M):
                if m == m0:
                    continue
                else:
                    model.addConstr(ftmk[t, m0, k] <= stmk[t, m, k] + 1 - Wtmm0k[t, m, m0, k])

    for t in range(T): # constraint (31)
        for m in range(M):
            for m0 in range(M):
                if m == m0:
                    continue
                else:
                    model.addConstr(Wtmm0k[t, m, m0, k] + stmk[t, m0, k] >= ftmk[t, m, k])

    for t in range(T-1): # constraint (32)
        for m in range(M):
            for k in range(K):
                for l in range(K):
                    model.addConstr(maxtm[t, m] >= ftmk[t, m, k] + Ttmkl[t, m, k, l] + tmk[t+1, m, l] -2)

    for t in range(T-1): # constraint (33)
        for m in range(M):
            for k in range(K):
                for l in range(K):
                    model.addConstr(ftmk[t, m, k] >= maxtm[t, m] + Ttmkl[t, m, k, l] + tmk[t+1, m, l] + 2)

    for t in range(T-1): # constraint (34)
        for m in range(M):
            for k in range(K):
                for l in range(K):
                    model.addConstr(maxtm[t, m] <= 1 - gp.quicksum(c[i][m][k] * Xitmk[i, t, m, k] + (1 + tmk[t, m, k] - tmk[t+1, m, k]) for i in range(N)))

    for t in range(T): # constraint (35)
        for m in range(M):
            model.addConstr(maxtm[t, m] <= 1)


    for t in range(T-1): # constraint (36)
        for m in range(M):
            for m0 in range(M):
                if m == m0:
                    continue
                else:
                    model.addConstr(maxtm[t, m0] - gp.quicksum( s[m0][l][k] * Ttmkl[t, m0, l, k] + (2 - 2 * tmk[t+1, m0, k]) for l in range(k)) >= ftmk[t, m, k] + gp.quicksum(Ttmkl[t, m, l, k] + tmk[t, m, k] -1 for l in range(k)))

    for i in range(N): # Constraint (37)
        for t in range(T):
            for m in range(M):
                for k in range(K):
                    if (i != S[i][m][0] and t != S[i][m][1] and m != S[i][m][2] and k !=S[i][m][3]):
                        model.addConstr(Xitmk[i, t, m, k] == 0)

    for i in range(N): # Constraint (38)
        for t in range(T):
            for m in range(M):
                for k in range(K):
                    model.addConstr(Iit[i, t] >= 0)
                    model.addConstr(Bit[i, t] >= 0)
                    model.addConstr(Xitmk[i, t, m, k] >= 0)
                    model.addConstr(stmk[t, m, k] >= 0)
                    model.addConstr(ftmk[t, m, k] >= 0)
                    model.addConstr(maxtm[t, m, ] >= 0)

    model.update()
    model.Params.TimeLimit = 3600 # maximum run time is 1 hour
    model.optimize()

    return model


# call the method to see the results
solve_CLSP('inst_P10_T4_M2_K8_C95_S5_V0')

