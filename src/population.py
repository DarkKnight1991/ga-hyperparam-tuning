#
# Copyright (c) 2019. Asutosh Nayak (nayak.asutosh@ymail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

from utils import *
import numpy as np
from individual import Individual
from copy import deepcopy

# TODO accept function as param for evaluate_model


class Population:
    def __init__(self, search_space, func_eval, mode, population_size=5, individuals=None):
        self.search_space = search_space
        self.population_size = population_size
        self.func_eval = func_eval
        self.mode = mode
        self.individuals = [None] * population_size
        if individuals is None:
            self.individuals = [deepcopy(Individual(choose_from_search_space(search_space))) for i in
                                range(population_size)]
        else:
            if not (population_size == len(individuals)):
                raise Exception("population size and length of individuals passed are different")
            self.individuals = individuals
        self.__fitness_scores = []
        self.calc_fitness_scores()
        log("initial population scores", self.__fitness_scores)

    def get_individual_models(self):
        return [individual.get_model() for individual in self.individuals]

    def calc_fitness_score(self, individual: Individual):
        mul = get_mode_multiplier(self.mode)
        score = mul * self.func_eval(individual.get_model(), batch_size=individual.get_nn_params()['batch_size'])
        return score

    def calc_fitness_scores(self):
        self.__fitness_scores.clear()
        for individual in self.individuals:
            individual.set_fitness_score(self.calc_fitness_score(individual))
            self.__fitness_scores.append(individual.get_fitness_score())

    def get_n_best_individual(self, n) -> Individual:
        assert n > 0, "argument to this function should be > 0. n=1 gives the best score"
        best_index = np.argsort(self.__fitness_scores)[-n]
        # print("get_n_best", best_index, self.get_individual_values_as_list(), self.fitness_scores)
        return self.individuals[best_index]

    def add_individual(self, new_individual, fitness_score=-np.inf):
        worst_index = np.argsort(self.__fitness_scores)[0]  # least fit individual
        if fitness_score == -np.inf:
            new_individual.set_fitness_score(self.calc_fitness_score(new_individual))
        else:
            new_individual.set_fitness_score(fitness_score)
        # print("add_ind", self.individuals[worst_index].get_nn_params())
        self.__fitness_scores[worst_index] = new_individual.get_fitness_score()
        self.individuals[worst_index] = new_individual
        return worst_index
        # print("add_individual", worst_index, self.get_individual_values_as_list(), self.fitness_scores)

    def set_fitness_scores(self, scores):
        self.__fitness_scores = get_mode_multiplier(self.mode)*scores
        for i, score in enumerate(self.__fitness_scores):
            self.individuals[i].set_fitness_score(score)

    def get_fitness_scores(self):
        return self.__fitness_scores
