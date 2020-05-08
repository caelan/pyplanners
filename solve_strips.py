#!/usr/bin/env python

from __future__ import print_function

import argparse

from time import time
from misc.profiling import run_profile
from misc.functions import randomize, elapsed_time
from misc.utils import SEPARATOR
from strips.utils import default_plan
import strips.domains as domains

DIRECTORY = './simulations/strips/planning/'

def solve(problem, print_profile):
    initial, goal, operators = problem()

    #dt = datetime.datetime.now()
    #directory = DIRECTORY + '{}/{}/{}/'.format(problem.__name__,
    # dt.strftime('%Y-%m-%d'), dt.strftime('%H-%M-%S'))
    print(SEPARATOR + '\nSolving strips problem ' + problem.__name__)

    def execute():
        start_time = time()
        try:
            output = default_plan(initial, goal, randomize(operators))
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
        print(profile_output)
    print(SEPARATOR)

###########################################################################


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--problem', default='restack_blocks')
    parser.add_argument('-q', '--profile', action='store_true')
    args = parser.parse_args()

    if hasattr(domains, args.problem):
        problem = getattr(domains, args.problem)
    else:
        print(args.problem, 'is not a valid problem')
        return
    solve(problem, args.profile)

if __name__ == '__main__':
    main()
