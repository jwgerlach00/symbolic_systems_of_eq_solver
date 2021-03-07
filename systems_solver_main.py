import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
from sympy import parse_expr, solve, symbols, sqrt, cos, sin, diff
from sympy.parsing.sympy_parser import standard_transformations,\
     implicit_multiplication_application


selected = None # points to selected entrybox
entryEqs = [] # container for entry.get equation input
textAnswer = "" # new answer to append to history
history = "" # stores all previous answers until cleared


class Left(tk.Frame):
    """Left Frame:
    contains buttons for notating various operations to the solver"""
    
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        self.master = root
        
        # place frame
        self.grid(row=0, rowspan=2, column=0)
        self.grid_propagate(False)
        
        # Operation guis
        self.lblOpPrompt = tk.Label(self, text="Operations:", bg="#CC0000")
        self.lblOpPrompt.grid(row=0, column=0)

        self.btnSqrt = tk.Button(self, text="√(_)", command=lambda: self.eq_operations('√()'))
        self.btnSqrt.grid(row=1, column=0)
        
        self.btnDiff = tk.Button(self, text = "∂(...)/∂_", command=lambda: self.eq_operations('∂(...)/∂()'))
        self.btnDiff.grid(row=2, column=0)

            
    def eq_operations(self, operator):
        """places notation at cursor location
        if cursor is not inside of an entry, returns error prompt"""
        
        global selected
        
        try:
            selected.insert(tk.INSERT, operator)
            selected.icursor(selected.index(tk.INSERT) - 1)
        except:
            # if no entry is selected
            pass
            
            

class Middle(tk.Frame):
    """Middle Frame:
    contains entries for input of equations
    contains button to add new entries
    contains buttons to remove each corresponding entry"""

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        self.master = root
        global entryEqs
        global selected
        self.eqNum = 2
        self.btnXs = []
        
        self.grid(row=0, column = 1)
        self.grid_propagate(False)

        entryEqs.extend([tk.Entry(self, width=26), tk.Entry(self, width=26)])
        self.btnXs.extend([[tk.Label(self, text="= 0", bg="#4B9CD3"), tk.Button(self, width=1, height=1, text="X", command=lambda: self.del_equation(self.eqNum - 2))],\
                           [tk.Label(self, text="= 0", bg="#4B9CD3"), tk.Button(self, width=1, height=1, text="X", command=lambda: self.del_equation(self.eqNum - 1))]])
        
        self.btnAddEq = tk.Button(self, text="ADD EQ", command=self.add_equation)

        entryEqs[0].grid(row=0, column=1, pady=3, padx=2)
        entryEqs[1].grid(row=1, column=1, pady=3, padx=2)
        self.btnXs[0][0].grid(row=0, column=2)
        self.btnXs[1][0].grid(row=1, column=2)
        self.btnXs[0][1].grid(row=0, column=3)
        self.btnXs[1][1].grid(row=1, column=3)
        
        self.btnAddEq.grid(row=self.eqNum, column=1)
        
        entryEqs[0].focus_set()
        selected = entryEqs[0]

        for entry in entryEqs:
            entry.bind("<1>", lambda event, e=entry: self.select_entry(e))
            
            
    def select_entry(self, entry):
        """recognizes cursor selection on equation entry"""
        
        global selected
        selected = entry

        
    def add_equation(self):
        """adds new equation entry gui along with corresponding entry remove button
        appends entryEqs list with new entry input"""
        
        global selected
        
        entryEqs.append(tk.Entry(self, width=26))
        self.btnXs.append([tk.Label(self, text="= 0", bg="#4B9CD3"), tk.Button(self, width=1, height=1, text="X", command=lambda: self.del_equation(self.eqNum))])
        
        entryEqs[self.eqNum].grid(row=self.eqNum, column=1, pady=3, padx=2)
        self.btnAddEq.grid(row=self.eqNum + 1, column=1)
        self.btnXs[self.eqNum][0].grid(row=self.eqNum, column=2)
        self.btnXs[self.eqNum][1].grid(row=self.eqNum, column=3)

        # increment equation number
        self.eqNum += 1
        # select new entry
        selected = entryEqs[self.eqNum - 1]
        entryEqs[self.eqNum - 1].focus_set
        # bind selection to new equation
        entryEqs[self.eqNum - 1].bind("<1>", lambda event, e=entryEqs[self.eqNum - 1]: self.select_entry(e))

        
    def del_equation(self, equation):
        """deletes corresponding equation and del, 'x' button
        removes equation element from entryEqs"""
        
        entryEqs[equation - 1].destroy()
        self.btnXs[equation - 1][0].destroy()
        self.btnXs[equation - 1][1].destroy()

        del entryEqs[equation - 1]
        del self.btnXs[equation- 1]

        for entry in entryEqs:
            entry.grid(row=entryEqs.index(entry))
        for x in self.btnXs:
            x[0].grid(row=self.btnXs.index(x))
            x[1].grid(row=self.btnXs.index(x))
            x[1]["command"] = lambda: self.del_equation(self.btnXs.index(x))

        self.eqNum -= 1
        
        

class Right(tk.Frame):
    """Right Frame:
    contains solve, clear buttons and sigfig input
    computes optimization on equations
    reformats special notation"""
    
    
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        global entryEqs
        self.transformations = (standard_transformations + (implicit_multiplication_application,))

        self.master = root
        
        self.grid(row=0, column = 2)
        self.grid_propagate(False)

        self.btnSolve = tk.Button(self, text="SOLVE", command=self.eq_optimize)
        self.btnSolve.grid(row=1, column=1, sticky='SE')
        
        self.btnClear = tk.Button(self, text="CLEAR", command=self.clear_output)
        self.btnClear.grid(row=2, column=1, sticky='SE')
        
        self.lblSigFig = tk.Label(self, text="s.f:", bg="cyan")
        self.lblSigFig.grid(row=0, column=0, sticky='W')
        
        self.entrySigFig = tk.Entry(self, width=5)
        self.entrySigFig.grid(row=0, column=1, sticky='W')
        
        
    def eq_optimize(self):
        """computes optimization on systems
        utilizes sympy symbolic solve function
        reformats "√", "^", "cos", "sin", "∂(...)∂_" notation to symbolically recognizable notation"""
        
        eqs = []; syms = []; parseSyms = []
        deltaCount = 0
        
        try:
            for entry in entryEqs:
                strEntry = entry.get()

                if ("cos" or "sin" in entry):
                    strEntry = strEntry.replace("cos", "")
                    strEntry = strEntry.replace("sin", "")
                for i, c in enumerate(strEntry):
                    if c == '∂' and deltaCount%2 == 0: # deltaCount is even (starting val = 0)
                        strEntry = strEntry[:i] + "diff" + strEntry[i + 1:]
                        deltaCount += 1
                    elif c == '∂' and deltaCount%2 != 0: # deltaCount is odd
                        strEntry = strEntry[:i + 1] + ',' + strEntry[i + 5:]
                        deltaCount += 1
                    elif (c.isalpha() and c not in syms):
                        syms.append(c)
                        parseSyms.append(parse_expr(c))
                print(strEntry)

                symEntry = parse_expr(strEntry.replace("√", "sqrt").replace("^", "**"), transformations=self.transformations)
                eqs.append(symEntry)


            parseSyms = symbols(syms)
            solution = solve(eqs, parseSyms, dict=True)
            self.disp_output(solution, parseSyms, syms)
        except:
            Bottom.bottom_label(frame4, "enter a solvable equation\n", clear=False)
       
    
    def clear_output(self):
        """calls bottom label output with CLEAR parameter set to true"""
        Bottom.bottom_label(frame4, " ", clear=True)
        

    def disp_output(self, solutions, parseSyms, syms):
        """formats output and calls bottom label"""
        
        global history
        global textAnswer
        self.answers = []
        self.historyLine = "\n" + 20*"-" + " history " + 20*"-"
        
        for i in range(len(solutions)):
            for j in range(len(syms)):
                self.answers.append(solutions[i][parseSyms[j]])
                
                try:
                    sigFig = int(self.entrySigFig.get())
                    self.answers[j] = np.format_float_positional(self.answers[j], precision=sigFig, fractional=False)
                except:
                    pass
                
                textAnswer = "".join((textAnswer, " ", str(syms[j]),  ": ", str(self.answers[j])))
                
        Bottom.bottom_label(frame4, "".join((history, self.historyLine, "\n", textAnswer)), clear=False)
        
        history += ("\n" + textAnswer)
        textAnswer = ""
        
        

class Bottom(tk.Frame):
    """Bottom Frame:
    displays solver output"""
    
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.grid(row=2, column=0, columnspan=3)
        self.lblSolutions = tk.Label(self)
 

    def bottom_label(self, textAnswer, *, clear):
        """generates output label"""
        
        if clear == False:
            self.lblSolutions.destroy()
            self.lblSolutions = tk.Label(self, text=textAnswer, justify=tk.LEFT, anchor='w')
            self.lblSolutions.grid(row=0, column=0, sticky = 'NSEW')
        else:
            self.lblSolutions.destroy()
       
        

root = tk.Tk()

root.title("System Solver - Jacob Gerlach")
root.geometry("400x400")
root.resizable(width=False, height=False)

frame1 = Left(root, width=100, height=300, bg="#CC0000")
frame2 = Middle(root, width=206, height=300, bg="#4B9CD3")
frame3 = Right(root, width=94, height=300, bg="cyan")
frame4 = Bottom(root, width=400, height=100)

root.mainloop()