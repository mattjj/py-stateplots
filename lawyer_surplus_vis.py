#!/usr/bin/env python
from __future__ import division
import states_plot as sp
from matplotlib import pyplot as pp
from matplotlib import cm

def main():
    # data loading
    surplusses = {}
    with open('law_surplus_data.txt','r') as infile:
        for line in infile:
            if line.strip() == '':
                continue
            linesplit = line.strip().split('\t')
            state, surplus = linesplit[0], int(linesplit[4].replace(',',''))
            if not linesplit[1].replace(',','').isdigit():
                state += ' ' + linesplit[1]
                surplus = int(linesplit[5].replace(',',''))
            if state in sp.continental_states:
                surplusses[state] = surplus
            else:
                print 'discarded %s' % state

    # data plotting SEE HOW SHORT THIS IS?!
    pp.set_cmap(cm.hot)
    sp.plot_dict(surplusses)
    pp.title('Lawyer Surplus by State')
    pp.show()

if __name__ == '__main__':
    main()
