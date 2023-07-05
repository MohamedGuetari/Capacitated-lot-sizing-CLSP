import re
import json
def readFile(filename):
    #filename = 'inst_P10_T4_M2_K4_C75_S1_V0.dat'

    lines = open(f'{filename}.dat').read().split(";")

    for index, line in enumerate(lines):
        if line.strip():
            line = line.rstrip().strip()
            if line.startswith('N ='):
                N = int(re.split('\s+', line)[2])
            elif line.startswith('T ='):
                T = int(re.split('\s+', line)[2])
            elif line.startswith('M ='):
                M = int(re.split('\s+', line)[2])
            elif line.startswith('K ='):
                K = int(re.split('\s+', line)[2])
            elif line.startswith('h = '):
                h = re.split('h = ', line)[1].replace(' ',',')
                h = json.loads(h)
            elif line.startswith('b = '):
                b = re.split('b = ', line)[1].replace(' ',',')
                b = json.loads(b)
            elif line.startswith('sigma = '):
                sigma = re.split('sigma = ', line)[1].replace(' ',',').replace('\n', ',')
                sigma = json.loads(sigma)
            elif line.startswith('d = '):
                d = re.split('d = ', line)[1].replace(' ',',')
                d = json.loads(d)
            elif line.startswith('I0 = '):
                I0 = re.split('I0 = ', line)[1].replace(' ',',')
                I0 = json.loads(I0)
            elif line.startswith('c = '):
                c = re.split('c = ', line)[1].replace(' ',',').replace('\n', ',')
                c = json.loads(c)
            elif line.startswith('s = '):
                s = re.split('s = ', line)[1].replace(' ',',').replace('\n', ',')
                s = json.loads(s)
            elif line.startswith('R = '):
                R = re.split('R = ', line)[1].replace(' ',',')
                R = json.loads(R)
            elif line.startswith('S = '):
                S = re.split('S = ', line)[1].replace(' ',',').replace('\n', ',')
                S = json.loads(S)
            elif line.startswith('alpha0 = '):
                alpha0 = re.split('alpha0 = ', line)[1].replace(' ',',')
                alpha0 = json.loads(alpha0)

    return N, T, M, K, h, b, sigma, d, I0, c, s, R, S, alpha0


