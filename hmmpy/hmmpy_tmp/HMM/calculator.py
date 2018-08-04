#!/usr/bin/python
# -*- coding: utf-8 -*-
from operator import itemgetter
import math


class HMM(object):

    def __init__(
        self,
        pi,
        tran,
        emm,
        ):
        self.States = []
        self.Symbols = []
        self.Pi = pi
        self.Tran = tran
        self.Emm = emm
        self.Alpha = {}
        self.Beta = {}
        self.Gamma = {}
        self.Delta = {}
        self.Prob = {}
        self.learnSample = []

    def generate(self, learnSample):
        self.learnSample = learnSample
        for (key, value) in self.Pi.iteritems():
            self.States.append(key)
        sym = []
        for r in learnSample:
            sym.extend(set(r[0]))
        self.Symbols = list(set(sym))

    def forward(self):
        for r in self.learnSample:
            for j in xrange(0, len(r[0])):
                if j == 0:
                    for state in self.States:
                        self.Alpha[(' '.join(r[0]), j + 1, state)] = \
                            self.Pi[state] * self.Emm[(state, r[0][j])]
                else:
                    for s1 in self.States:
                        alpha = 0.0
                        for s2 in self.States:
                            alpha += self.Alpha[(' '.join(r[0]), j,
                                    s2)] * self.Tran[(s2, s1)] \
                                * self.Emm[(s1, r[0][j])]
                        self.Alpha[(' '.join(r[0]), j + 1, s1)] = alpha

    def backward(self):
        for r in self.learnSample:
            rdash = (r[0])[:]
            rdash.reverse()

            for state in self.States:
                self.Beta[(' '.join(r[0]), len(r[0]), state)] = 1

            for j in xrange(0, len(r[0]) - 1):
                for s1 in self.States:
                    beta = 0.0
                    for s2 in self.States:
                        beta += self.Beta[(' '.join(r[0]), len(r[0])
                                - j, s2)] * self.Tran[(s1, s2)] \
                            * self.Emm[(s2, rdash[j])]
                    self.Beta[(' '.join(r[0]), len(r[0]) - j - 1,
                              s1)] = beta

    def sampleProb(self):
        for r in self.learnSample:
            p = 0.0
            for s in self.States:
                p += self.Alpha[(' '.join(r[0]), len(r[0]), s)]
            self.Prob[' '.join(r[0])] = p

    def forwardbackward(self):
        self.sampleProb()
        for r in self.learnSample:
            for j in xrange(0, len(r[0]) - 1):
                for s1 in self.States:
                    for s2 in self.States:
                        if self.Prob[' '.join(r[0])] == 0:
                            self.Gamma[(' '.join(r[0]), j + 1, s1,
                                    s2)] = 0
                        else:
                            self.Gamma[(' '.join(r[0]), j + 1, s1,
                                    s2)] = self.Alpha[(' '.join(r[0]),
                                    j + 1, s1)] * self.Tran[(s1, s2)] \
                                * self.Emm[(s2, r[0][j + 1])] \
                                * self.Beta[(' '.join(r[0]), j + 2,
                                    s2)] / self.Prob[' '.join(r[0])]

    def calcDelta(self):
        for r in self.learnSample:
            for j in xrange(0, len(r[0]) - 1):
                for s1 in self.States:
                    delta = 0.0
                    for s2 in self.States:
                        delta += self.Gamma[(' '.join(r[0]), j + 1, s1,
                                s2)]
                    self.Delta[(' '.join(r[0]), j + 1, s1)] = delta

    def nextHmm(self):
        I = {}

        for state in self.States:
            I[state] = 0.0
            for r in self.learnSample:
                I[state] += self.Delta[(' '.join(r[0]), 1, state)] \
                    * r[1]

        sum = 0.0
        for s in self.States:
            sum += I[s]

        for state in self.States:
            if sum == 0:
                self.Pi[state] = 0
            else:
                self.Pi[state] = I[state] / sum

        K = {}

        for s1 in self.States:
            for s2 in self.States:
                gamma = 0.0
                for r in self.learnSample:
                    for j in xrange(0, len(r[0]) - 1):
                        gamma += self.Gamma[(' '.join(r[0]), j + 1, s1,
                                s2)] * r[1]
                K[(s1, s2)] = gamma

            sum = 0.0
            for state in self.States:
                sum += K[(s1, state)]

            for s2 in self.States:
                if sum == 0:
                    self.Tran[(s1, s2)] = 0
                else:
                    self.Tran[(s1, s2)] = K[(s1, s2)] / sum

        L = {}

        for state in self.States:
            for symbol in self.Symbols:
                delta = 0.0
                for r in self.learnSample:
                    for i in xrange(0, len(r[0]) - 1):
                        if r[0][i] == symbol:
                            delta += self.Delta[(' '.join(r[0]), i + 1,
                                    state)] * r[1]
                L[(state, symbol)] = delta

            sum = 0.0
            for symbol in self.Symbols:
                sum += L[(state, symbol)]

            for symbol in self.Symbols:
                if sum == 0:
                    self.Emm[(state, symbol)] = 0
                else:
                    self.Emm[(state, symbol)] = L[(state, symbol)] / sum

    def likelyhood(self):
        L = 0.0
        Pr = {}
        for r in self.learnSample:
            Pr[' '.join(r[0])] = 0.0
            for s in self.States:
                Pr[' '.join(r[0])] += self.Alpha[(' '.join(r[0]),
                        len(r[0]), s)]
            if Pr[' '.join(r[0])] == 0:
                L += 0
            else:
                L += r[1] * math.log(Pr[' '.join(r[0])])
        return L

    def optimize(self):
        self.forward()
        self.backward()
        self.forwardbackward()
        self.calcDelta()
        self.nextHmm()



			