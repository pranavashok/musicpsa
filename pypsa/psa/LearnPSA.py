from __future__ import division
from ..tree.Tree import Tree
import math
import random
import numpy
import array

class LearnPSA(object):
    def __init__(self, e, n, L, Sigma):
        self.e = e
        self.n = n
        self.L = L
        self.Sigma = Sigma
        self.e2 = e/(48*L)
        self.gamma_min = e/(48*L*len(Sigma))
        self.e0 = e/(2*n*L*math.log(48*L*len(Sigma)/e, 10))
        self.e1 = e*math.log(48*L*len(Sigma)/e, 10)/(9216*L*len(Sigma))
        self.sample = []
        self.PST = None
        self._P2Store = {}
        self._P1Store = {}
    
    def _X(self, sample, sequence, start, end):
        count = 0
        flag = 1
        for i in range(start, end):
            j = i
            for element in sequence:
                if sample[j] == element:
                    flag = 0
                else:
                    flag = 1
                    break
                j = j + 1
            if flag == 0:
                count += 1
        return count

    def _remove(self, l, subl):
        flag = 1
        for i in range(0, len(l)-len(subl)+1):
            j = i
            for element in subl:
                if l[j] == element:
                    flag = 0
                else:
                    flag = 1
                    break
                j = j + 1
            if flag == 0:
                for j in range(i, i+len(subl)):
                    l.remove(l[i])

    def add_sample(self, s):
        split = s.split(" ")
        self.sample.append(split)
    
    def generate_pst(self):
        self.PST = self._learn()

    def _P1(self, s):
        u'''
        P(s) is roughly the relative number of times s appears in the sample
        This implementation of P is slightly modified. It divides with |r| - L 
        for each string r in sample and each |r| does not need to be equal to l
        '''
        p = self._P1Store.get(" ".join(s), -1)
        if p == -1:
            p = 0
            for r in self.sample:
                p += self._X(r, s, self.L-len(s), len(r)-len(s)+1)/(len(r)-self.L)
            if p == 0:
                pass
            else:
                p = p/(len(self.sample))
            self._P1Store[" ".join(s)] = p
        return p

    def _P2(self, sigma, s):
        u'''
        P(sigma|s) is roughly the relative number of times sigma appears after s
        '''
        p = self._P2Store.get((sigma, " ".join(s)), -1)
        if p == -1:
            countssigma = 0.0
            counts = 0.0
            ssigma = []
            for e in s:
                ssigma.append(e)
            ssigma.append(sigma)
            for r in self.sample:
                countssigma += self._X(r, ssigma, 0, len(r)-len(ssigma)+1)
                counts += self._X(r, s, 0, len(r)-len(s)) #len(s) + 1 or not???
            if countssigma == 0:
                p = 0
            else:
                p = countssigma/counts
            self._P2Store[(sigma, " ".join(s))] = p
        return p

    def _PI(self):
        PI = {}
        for sigma in self.Sigma:
            count = 0
            for r in self.sample:
                if r[0] == sigma:
                    count += 1
            PI[sigma] = count/len(self.sample)
        return PI

    def _add_missing_children(self, tree):
        #Filter out leaves
        if len(tree.children) == 0:
            return tree
        else:
            missing_children = []
            if tree.data[1] == 1:
                for sigma in self.Sigma:
                    if tree.data[0] == u'0':
                        missing_children.append([sigma])
                    else:
                        newnode = [sigma]
                        newnode.extend(tree.data[0])
                        missing_children.append(newnode)
            else:
                return tree

            for child in tree.children:
                child = self._add_missing_children(child)
                if child.data[1] == 1:
                    self._remove(missing_children, child.data[0])
                    missing_children.remove(missing_children[missing_children.index(child.data[0])])

            for s in missing_children:
                tree = tree.insert(Tree([s, 0]))

            return tree

    def _learn(self):
        print("P1 > %s" % (float(1-self.e1)*float(self.e0)))
        print("P2 > %s" % (float(1+self.e2)*float(self.gamma_min)))
        self._P1Store = {}
        self._P2Store = {}

        T = Tree([u"0", 1])
        S = []
        removed_from_S = []
        for sigma in self.Sigma:
            if self._P1([sigma]) >= (1-self.e1)*self.e0:
                S.append([sigma])

        while len(S) > 0:
            s = S.pop()

            for sigma in self.Sigma:
                u'''suffix(s) = s[1:]'''
                if len(s) == 1:
                    if (self._P2(sigma, s) >= (1+self.e2)*self.gamma_min):
                        T = T.insert(Tree([s, 1]))
                        break
                else:
                    if self._P2(sigma, s[1:]) != 0:
                        if (self._P2(sigma, s) >= (1+self.e2)*self.gamma_min) and ((self._P2(sigma, s)/self._P2(sigma, s[1:])) > 1+3*self.e2):
                            u'''
                            This will insert all suffixes uptil s
                            '''
                            i = len(s)-1
                            while i >= 0:
                                x = T.bfs(s[i:])
                                if x == None:
                                    parent = T.bfs(s[i+1:])
                                    parent = parent.insert(Tree([s[i:], 1]))
                                i = i - 1
                            i = len(s)-1
                            while i > 0:
                                if removed_from_S.count(s[i:]) == 0:
                                    S.append(s[i:]) #Insert only uniques
                                i = i - 1
                            break
                        else:
                            if self._P2(sigma, s) >= (1+self.e2)*self.gamma_min:
                                u'''
                                This will insert all suffixes uptil s
                                '''
                                i = len(s)-1
                                while i >= 0:
                                    x = T.bfs(s[i:])
                                    if x == None:
                                        parent = T.bfs(s[i+1:])
                                        parent = parent.insert(Tree([s[i:], 1]))
                                    i = i - 1
                                break

            if len(s) < self.L:
                for sigma in self.Sigma:
                    sigmas = [sigma]
                    sigmas.extend(s)
                    if self._P1(sigmas) >= (1-self.e1)*self.e0:
                        S.append(sigmas)

            removed_from_S.append(s)

        _T = T
        _T = self._add_missing_children(_T)
        #_T = self._compute_gamma_s_sigma(_T)
        
        return _T

    def _compute_gamma_s_sigma(self, tree):
        s = tree.data[0]
        gamma_s_sigma = {}
        for child in tree.children:
            child = self._compute_gamma_s_sigma(child)
        for sigma in self.Sigma:
            gamma_s_sigma[sigma] = self._P2(sigma, (s[1:])[::-1])*(1-len(self.Sigma)*self.gamma_min)+self.gamma_min
            tree.data.append(gamma_s_sigma)
        return tree

    def print_tree(self):
        bfsqueue = []
        for c in self.PST.children:
            bfsqueue.append(c)
        while len(bfsqueue) > 0:
            e = bfsqueue.pop()
            print(e.data[0])
            for c in e.children:
                bfsqueue.append(c)

    def _get_pst_states(self):
        states = []
        bfsqueue = []
        for c in self.PST.children:
            bfsqueue.append(c)
        while len(bfsqueue) > 0:
            e = bfsqueue.pop()
            states.append([e.data[0]])
            for c in e.children:
                bfsqueue.append(c)
        return states
    
    def generate_psa(self):
        min_prob = 1.0
        psa = []
        states = self._get_pst_states()
        for state in states:
            state.reverse()
            psa.extend(state)

        psa.sort()
        transition = {}
        nextstate = {}
        for state in psa:
            for sigma in self.Sigma:
                print(" ".join(state), sigma)
                transition[(" ".join(state), sigma)] = self._P2(sigma, state)
                if transition[(" ".join(state), sigma)] > 0:
                    if transition[(" ".join(state), sigma)] < min_prob:
                        min_prob = transition[(" ".join(state), sigma)]
                    #If state+sigma or it's suffix is present
                    ssigma = state[:]
                    ssigma.append(sigma)
                    for i in range(0, len(ssigma)):
                        #Add ssigma only if there is a possibility of ssigma
                        if psa.count(ssigma[i:]) == 1 and self._P1(ssigma[i:]) > (1-self.e1)*self.e0:
                            nextstate[(" ".join(state), sigma)] = (ssigma)[i:]
                            break
        if min_prob < 0.2:
            #TWEAK ---- Distribute the probabilities
            increase_min_to = 0.3
            factor = (0.5 - increase_min_to)/(0.5 - min_prob)
            for state in psa:
                for sigma in self.Sigma:
                    if transition[(" ".join(state), sigma)] > 0 and transition[(" ".join(state), sigma)] < 1:
                        transition[(" ".join(state), sigma)] = 0.5 + (transition[(" ".join(state), sigma)] - 0.5)*factor-0.2
            #END TWEAK

        return psa, transition, nextstate

    def _first_transition(self, transition):
        PI = self._PI()
        pi = []
        p = []
        P = {}

        for sigma in self.Sigma:
            p.append((PI.get(sigma, 0), sigma))
        p.sort()
        pi = []
        for element in p:
            pi.append(element[0])
            P[element[1]] = 0
        prob = numpy.array(pi)
        cumprob = numpy.cumsum(prob)

        i = 0
        for element in p:
            P[element[1]] = cumprob[i]
            i += 1

        r = random.randrange(1, 999)/1000
        
        for sigma in P:
            if P[sigma]-r >= 0 and P[sigma] > 0:
                flag = 0
                for next in self.Sigma:
                    if transition.get((sigma, next), 0) > 0:
                        flag = 1
                        break
                if flag == 1:
                    return sigma
                
    def generate_run(self, states, transition, nextstate, N):
        run = u""
        first = self._first_transition(transition)
        run += first
        cur_state = [first]
        while len(run.split(" ")) <= N:
            p = []
            T = {}
            for sigma in self.Sigma:
                p.append((transition.get((" ".join(cur_state), sigma), 0), sigma))
            p.sort()

            po = []
            for element in p:
                po.append(element[0])
                T[element[1]] = 0
            prob = numpy.array(po)
            cumprob = numpy.cumsum(prob)

            i = 0
            for element in p:
                T[element[1]] = cumprob[i]
                i += 1

            r = random.randrange(1, 999)/1000

            for sigma in T:
                if T[sigma]-r >= 0 and T[sigma] > 0:
                    run += u" "+sigma
                    #Find a next possible state which has some non-zero symbol probability
                    if random.randrange(1, 999) > 300:
                        next_possible_state = nextstate.get((" ".join(cur_state), sigma), [first])
                    else: #TWEAK ---- To increase randomness
                        next_possible_state = nextstate.get((cur_state[-1], sigma), [first])
                    #next_possible_state = nextstate.get((" ".join(cur_state), sigma), [first])
                    flag = 0
                    for sigma in self.Sigma:
                        if transition.get((" ".join(next_possible_state), sigma), 0) > 0:
                            flag = 1
                            break
                    if flag == 1:
                        cur_state = next_possible_state
                        break
                    else:
                        #just setting cur_state to first in case we reach a dead end.
                        cur_state = [first]
                        break #???
        return run