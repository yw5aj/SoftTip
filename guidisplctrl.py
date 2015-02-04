import Tkinter as tk
import tkMessageBox
import ttk

import numpy as np
import time

from displctrl import Session


class Application(ttk.Frame):

    def __init__(self, master=None):
        # Initialize the frame
        ttk.Frame.__init__(self, master)
        self.grid()
        # Create widgets
        self.init_ui()
        return

    def init_ui(self):
        self.controlLabelframe = ControlLabelframe(self)
        self.controlLabelframe.grid(sticky='nwse')
        self.outputLabelframe = OutputLabelframe(self)
        self.outputLabelframe.grid(sticky='nwse')
        self.evalSoftTip = EvalSoftTip(self)
        self.evalSoftTip.grid(sticky='nwse')
        return


class ControlLabelframe(ttk.Labelframe):

    def __init__(self, master=None):
        ttk.Labelframe.__init__(self, master, text='Control')
        self.grid()
        self.init_ui()
        return

    def init_ui(self):
        # The velocity part
        self.vel = tk.StringVar(value=1)
        self.vel_label = ttk.Label(self, text='Current velocity (mm/s):')
        self.vel_label.grid(column=0, row=0, columnspan=2, sticky=(tk.E))
        self.vel_value_label = ttk.Label(self, textvariable=self.vel)
        self.vel_value_label.grid(column=2, row=0, columnspan=2, sticky=(tk.W))
        self.vel_rb_list = [ttk.Radiobutton(self, text=str(vel),
                                            variable=self.vel, value=vel)
                            for vel in [.01, .1, 1, 10]]
        for i, vel_rb in enumerate(self.vel_rb_list):
            vel_rb.grid(column=i, row=1)
        # Create control buttons
        self.displ_control_label = ttk.Label(self,
                                             text='Move relative displ (mm)')
        self.displ_control_label.grid(column=0, row=2, columnspan=4)
        # Coarse up
        self.coarse_up_displ = tk.StringVar(value=0.1)

        def coarse_up():
            session.move_rel(displ=-float(self.coarse_up_displ.get()),
                             vel=float(self.vel.get()))
            return
        self.coarse_up_button = ttk.Button(self, text='Coarse up',
                                           command=coarse_up)
        self.coarse_up_button.grid(column=0, row=3)
        self.coarse_up_entry = ttk.Entry(self,
                                         textvariable=self.coarse_up_displ)
        self.coarse_up_entry.grid(column=1, row=3)
        # Coarse down
        self.coarse_down_displ = tk.StringVar(value=0.1)

        def coarse_down():
            session.move_rel(displ=float(self.coarse_down_displ.get()),
                             vel=float(self.vel.get()))
            return
        self.coarse_down_button = ttk.Button(self, text='Coarse down',
                                             command=coarse_down)
        self.coarse_down_button.grid(column=0, row=4)
        self.coarse_down_entry = ttk.Entry(self,
                                           textvariable=self.coarse_down_displ)
        self.coarse_down_entry.grid(column=1, row=4)
        # Fine up
        self.fine_up_displ = tk.StringVar(value=0.01)

        def fine_up():
            session.move_rel(displ=-float(self.fine_up_displ.get()),
                             vel=float(self.vel.get()))
            return
        self.fine_up_button = ttk.Button(self, text='Fine up', command=fine_up)
        self.fine_up_button.grid(column=2, row=3)
        self.fine_up_entry = ttk.Entry(self,
                                       textvariable=self.fine_up_displ)
        self.fine_up_entry.grid(column=3, row=3)
        # Fine down
        self.fine_down_displ = tk.StringVar(value=0.01)

        def fine_down():
            session.move_rel(displ=float(self.fine_down_displ.get()),
                             vel=float(self.vel.get()))
            return
        self.fine_down_button = ttk.Button(self, text='Fine down',
                                           command=fine_down)
        self.fine_down_button.grid(column=2, row=4)
        self.fine_down_entry = ttk.Entry(self,
                                         textvariable=self.fine_down_displ)
        self.fine_down_entry.grid(column=3, row=4)
        # Absolute move
        self.displ_abs = tk.StringVar(value=0.)
        self.displ_abs_button = ttk.Button(self,
                                           text='Move to absolute displ (mm)')
        self.displ_abs_button.grid(column=0, row=5, columnspan=2, sticky='we')
        self.displ_abs_entry = ttk.Entry(self, textvariable=self.displ_abs)
        self.displ_abs_entry.grid(column=2, row=5, columnspan=2, sticky='we')

        def displ_abs():
            session.move_abs(float(self.displ_abs.get()),
                             float(self.vel.get()))
            return
        self.displ_abs_button['command'] = displ_abs
        return


class OutputLabelframe(ttk.Labelframe):

    def __init__(self, master=None):
        ttk.Labelframe.__init__(self, master, text='Output')
        self.init_ui()
        return

    def init_ui(self):
        # Read force value
        self.force = tk.StringVar(value=0)

        def refresh_force():
            force_n = session.get_current_force()
            force_mn = np.round(1e3 * force_n, 2)
            self.force.set(force_mn)
            return
        self.force_button = ttk.Button(self, text='Refresh force (mN):',
                                       command=refresh_force)
        self.force_button.grid(column=0, row=0, sticky='we')
        self.force_val_label = ttk.Label(self, textvariable=self.force)
        self.force_val_label.grid(column=1, row=0, sticky='we')
        # Read displ value
        self.displ = tk.StringVar(value=0)

        def refresh_displ():
            displ = session.get_current_displ()
            self.displ.set(displ)
            return
        self.displ_button = ttk.Button(self, text='Refresh displ (mm):',
                                       command=refresh_displ)
        self.displ_button.grid(column=2, row=0, sticky='we')
        self.displ_val_label = ttk.Label(self, textvariable=self.displ)
        self.displ_val_label.grid(column=3, row=0, sticky='we')
        for col in range(self.grid_size()[0]):
            self.grid_columnconfigure(col, weight=1)
        return


class EvalSoftTip(ttk.Labelframe):

    def __init__(self, master=None):
        ttk.Labelframe.__init__(self, master, text='Evaluate soft tip')
        self.init_ui()
        return

    def init_ui(self):
        # Tip number
        self.tip_id = tk.StringVar(value=0)
        self.tip_id_label = ttk.Label(self, text='Tip id:')
        self.tip_id_label.grid(column=0, row=0)
        self.tip_id_entry = ttk.Entry(self, textvariable=self.tip_id)
        self.tip_id_entry.grid(column=0, row=1)
        # Tip diameter
        self.tip_dia = tk.StringVar(value='1/16 in')
        self.tip_dia_label = ttk.Label(self, text='Tip diameter:')
        self.tip_dia_label.grid(column=1, row=0)
        self.tip_dia_spinbox = tk.Spinbox(self, textvariable=self.tip_dia,
                                          values=['1/16 in', '1/8 in'])
        self.tip_dia_spinbox.grid(column=1, row=1)
        # Substrate type
        self.substrate_type = tk.StringVar(value='soft')
        self.substrate_type_label = ttk.Label(self, text='Substrate type:')
        self.substrate_type_label.grid(column=2, row=0)
        self.substrate_type_spinbox = tk.Spinbox(
            self, textvariable=self.substrate_type, values=['soft', 'rigid'])
        self.substrate_type_spinbox.grid(column=2, row=1)
        # Change tip and recalibrate loadcell
        self.reset_button = ttk.Button(self, text='Reset force offset',
                                       command=session.get_force_offset)
        self.reset_button.grid(columnspan=4, sticky='nwse')
        # Evaluate button
        self.eval_button = ttk.Button(self, text='Evaluate soft tip',
                                      command=self.eval_func)
        self.eval_button.grid(columnspan=4, sticky='nwse')
        return

    def eval_func(self, max_force=.5, force_threshold=10e-3, clearance=.2):
        # Find contact and max position
        session.move_abs(5., 10.)
        contact_pos = session.find_force_pos(force_threshold) - clearance
        max_pos = session.find_force_pos(max_force)
        # Perform two sets of ramp and hold: slow and fast
        session.move_abs(contact_pos, 10.)
        # First, slow
        session.displ_ramp_hold(max_pos - contact_pos, .01, 10.)
        session.move_abs(contact_pos, 10.)
        # Second, fast
        session.displ_ramp_hold(max_pos - contact_pos, 1., 10.)
        session.move_abs(contact_pos, 10.)
        # Move back to zero position
        session.move_abs(0, 10.)
        # Take note on the tip number we just tested
        fname = time.strftime('./csvs/%Y%m%d%H%M%S.txt', time.localtime())
        with open(fname, 'w') as f:
            f.write('Tip id: ' + self.tip_id.get() + '\nTip diameter: '
                    + self.tip_dia.get() + '\nSubstrate type: ' +
                    self.substrate_type.get())
        # Show a message box
        tkMessageBox.showinfo(message='Done!')
        return


if __name__ == '__main__':
    # Open connection to the controller
    session = Session()
    root = tk.Tk()
    root.title('Manual displ control interface')
    app = Application(root)
    root.mainloop()
