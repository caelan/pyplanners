#!/usr/bin/env python

from __future__ import print_function

import argparse
import random

from time import time
from misc.profiling import run_profile, str_profile
from misc.functions import randomize, elapsed_time
from misc.utils import SEPARATOR
from strips.utils import default_plan, SEARCHES, EVALUATORS, HEURISTICS, SUCCESSORS
#from planner.main import simple_debug, pause_debug
import strips.domains as domains

DIRECTORY = './simulations/strips/planning/'

def solve_strips(problem, print_profile=False, **kwargs):
    initial, goal, operators = problem()
    operators = randomize(operators)

    #dt = datetime.datetime.now()
    #directory = DIRECTORY + '{}/{}/{}/'.format(problem.__name__,
    # dt.strftime('%Y-%m-%d'), dt.strftime('%H-%M-%S'))
    print('Solving strips problem ' + problem.__name__ + '\n' + SEPARATOR)

    def execute():
        start_time = time()
        try:
            output = default_plan(initial, goal, operators, debug=None, **kwargs) # None | simple_debug
        except KeyboardInterrupt:
            output = None, elapsed_time(start_time)
        #make_dir(directory)
        #print('Created directory:', directory)
        return output

    (plan, state_space), profile_output = run_profile(execute)
    #print('Wrote', directory+'profile')
    print(SEPARATOR)

    data = (str(plan) if plan is not None else 'Infeasible') + '\n\n' + str(state_space)
    print(data)
    #write(directory + 'planner_statistics', data)
    #print('Wrote', directory+'planner_statistics')

    if print_profile:
        print(SEPARATOR)
        print(str_profile(profile_output))
    print(SEPARATOR)

###########################################################################


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--problem', default='restack_blocks')
    parser.add_argument('-q', '--profile', action='store_true')
    parser.add_argument('-s', '--search', type=str,
                        default='eager', choices=sorted(SEARCHES), help='')
    parser.add_argument('-e', '--evaluator', type=str,
                        default='greedy', choices=sorted(EVALUATORS), help='')
    parser.add_argument('-heu', '--heuristic', type=str,
                        default='ff', choices=sorted(HEURISTICS), help='')
    parser.add_argument('-suc', '--successors', type=str,
                        default='all', choices=sorted(SUCCESSORS), help='')
    parser.add_argument('-seed', '--seed', default=None, help='')
    args = parser.parse_args()
    print(args)

    random.seed(args.seed)
    print('Random seed:', args.seed)
    print('Random value:', random.random())

    if hasattr(domains, args.problem):
        problem = getattr(domains, args.problem)
    else:
        print(args.problem, 'is not a valid problem')
        return
    solve_strips(problem, args.profile, search=args.search, evaluator=args.evaluator,
                 heuristic=args.heuristic, successors=args.successors)

if __name__ == '__main__':
    main()
