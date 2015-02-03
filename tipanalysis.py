# -*- coding: utf-8 -*-
"""
Created on Wed May 21 14:14:25 2014

@author: Yuxiang Wang
"""


import numpy as np
import matplotlib.pyplot as plt
import os, re


class TipEval:
    
    def __init__(self, note_fname):
        self.note_fname = note_fname
        self.parse_note()
        return
    
    def parse_note(self):
        with open('./csvs/'+self.note_fname, 'r') as f:
            note_text = f.read()
        note_data = [re.findall(r':.+', note_text)[i][2:] for i in range(3)]
        self.tip_id, self.tip_dia, self.substrate = note_data
        return
    
    def get_data(self, relax_duration=0.):
        relax_duration_index = int(relax_duration*1e3)
        # Find data file names
        data_fnames_all = np.array([int(fname[:-4]) for fname in 
            os.listdir('./csvs/') if fname.endswith('.csv')])
        data_fnames_array = np.sort(data_fnames_all[data_fnames_all < 
            int(self.note_fname[:-4])])[-2:]
        self.data_fname_list = ['%d.csv' % data_fname for data_fname in 
            data_fnames_array]
        # Read traces
        self.traces = dict(slow={}, fast={})
        self.traces['slow']['time'], self.traces['slow']['displ'],\
            self.traces['slow']['force'] = np.genfromtxt('./csvs/'
            +self.data_fname_list[0], delimiter=',').T
        self.traces['slow']['force'] -= self.traces['slow']['force'][0]
        self.traces['fast']['time'], self.traces['fast']['displ'],\
            self.traces['fast']['force'] = np.genfromtxt('./csvs/'
            +self.data_fname_list[1], delimiter=',').T            
        for vel, traces in self.traces.items():
            contact_index = (traces['force'] > 10e-3).nonzero()[
                0][0]
            max_index = traces['force'].argmax()
            for trace_name, trace in traces.items():
                self.traces[vel][trace_name] = trace[contact_index:
                    max_index+relax_duration_index] - trace[contact_index]
        return


def main():
    pass


if __name__ == '__main__':
    main()
    tipEval_list = []
    tip_to_eval = ['rigid', '27-1', '27-2', '40-1', '40-2', '50-1', '50-2',] 
#        '60-1', '60-2', '70-1', '70-2', '85-1', '85-2', '95-1', '95-2']
    for fname in os.listdir('./csvs/'):
        if fname.endswith('.txt'):
            tipEval_list.append(TipEval(fname))
    fig, axs = plt.subplots(1, 1)
    for tipEval in tipEval_list:
        if tipEval.tip_id in tip_to_eval and tipEval.substrate == 'soft':
            print(tipEval.tip_id + ' is done.')
            tipEval.get_data()
            axs.plot(tipEval.traces['slow']['force']*1e3,
                tipEval.traces['slow']['displ']*1e3, label=tipEval.tip_id)
    handles, labels = axs.get_legend_handles_labels()
    handles = np.array(handles)
    labels = np.array(labels)
    handles = handles[np.argsort(labels)]
    labels = np.sort(labels)
    axs.legend(handles, labels, loc=2)
    axs.set_xlabel('Force (mN)')
    axs.set_xlim(-50, 500)
    axs.set_ylabel(r'Displacement ($\mu$m)')
    axs.set_title('Force-displ curve for 1.59 mm dia. tips')
    fig.tight_layout()
    fig.savefig('./plots/tip_force_displ.png', dpi=300)
    
            
    