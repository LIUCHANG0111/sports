import random as r
import matplotlib.pyplot as plt
import copy
import numpy as np
from fpdf import FPDF
import pandas as pd

# Create a class called bingo
class Bingo():
    # Construction input and recording methods
    def __init__(self): 
        while True:
            self.card_num = input("enter the number of cards")# Definition of card quantities
            self.sim_num = input("enter the number of simulation")# Definition of simulation times
            # Perform input type detection to ensure that user input values are integers
            if self.card_num.isdigit() and self.sim_num.isdigit():
                self.card_num = int(self.card_num)
                self.sim_num = int(self.sim_num)
                break
            else:
                print("You need to input an *integer*.")

        self.countlst = [[0]*75 for i in range(self.sim_num)] # Generate i matrices to record bingo numbers and set the initial value to 75 zeros
        self.countlst2 = [[] for i in range(self.sim_num)] # Generate a list to record the cumulative number of simulations
        print("\n")
        
        
    # Define the card display method
    def show_one(self,lst):
        # Set up a list containing 25 numbers separated by spaces
        for i in range(5):
            for j in range(5):
                print(lst[i][j],end = "\t") 
                # Set 5*5 matrix format
                if j % 5 == 4:
                    print("\n") 


    # Play the bingo game
    def generator(self):
        # Create bingo cards
        card_lst = [] 
        for i in range(self.card_num):
            lst = [r.sample(range(15 * j + 1, 15 * j + 16), 5) for j in range(5)]  # Randomly generate a list of 25 non-repeating numbers
            lst = list(map(list, zip(*lst))) # Row Swap
            lst[2][2] = "*"  # Set free cell
            card_lst.append(lst) # Store all cards as a list
        
        # Output cards as pdf
        card_pdf = FPDF(format='letter', unit='in')# Set the paper size and units for the card pdf
        for card_index in range(self.card_num):
            card_pdf.add_page()# Add a page
            # Setup card format
            card_pdf.set_left_margin(1.8)
            card_pdf.set_right_margin(1.8)
            epw = 5 
            col_width = epw / 5 
            card_pdf.ln(1) 
            # Set font formatting and title content
            card_pdf.set_font('Times', 'B', 20.0)
            card_pdf.cell(epw, 0.0, 'CARD'+str(card_index+1), align='C')
            card_pdf.set_font('Times', '', 13.0)
            card_pdf.ln(1) 
            # Set table content and formatting
            th = 1 
            for i in range(5):
                for j in range(5):
                    card_pdf.cell(col_width, th, str(card_lst[card_index][i][j]), border=1, align="C")# Show cards
                card_pdf.ln(th)
        card_pdf.output('card_table.pdf', 'F')# Output pdf
        
        # Conduct simulation
        for j in range(self.sim_num): 
            numlst = r.sample(range(1, 76), 75)  # Generate 75 non-repeating random numbers
            print("Simulation{} starts~".format(j+1), end="\n")
            print("\n")
            # Simulation in each card
            for i in range(self.card_num): 
                self.show_one(card_lst[i]) # Show generated cards
                print("This is Card{}".format(i+1), end="\n\n")
                # Set original value
                count = 0
                bingo = 0
                temp = copy.deepcopy(card_lst[i]) # Make temp completely independent card_lst
                line = [5] * 2 + [4] + [5] * 4 + [4] + [5] * 2 + [4] * 2# Set initial line values (0-4 vertical, 5-9 horizontal, 10 primary diagonal, 11 secondary diagonal)
                while bingo != 1 and count <= 74:
                     choice = numlst[count] # Set choice=count of random numbers
                     count += 1
                     print("Round {}: The random number is {}.".format(count, choice))
                     # Set bingo rules
                     for row in range(5):
                        if choice in temp[row]: 
                            num_col = temp[row].index(choice) 
                            temp[row][num_col] = "*" + str(temp[row][num_col]) # Mark the numbers that have been called
                            line[num_col] -= 1 # Number on vertical row-1
                            line[row + 5] -= 1 # Number on horizontal row-1
                            if num_col == row: # Number on main diagonal-1
                                line[10] -= 1
                            if num_col + row == 4: # Numbers on the sub diagonal-1
                                line[11] -= 1
                            print("There is {} in Card{}.".format(choice, i+1))
                            self.show_one(temp) 
                            # Count when bingo appears
                            if 0 in line: 
                                print("Card{} Bingo!!!".format(i+1))
                                bingo = 1
                                self.countlst[j][count-1] += 1 # Record the number of bingo people in each call
                                break
                       

    # Convert the list of recorded single bingo's into a cumulative list
    def transfer(self): 
        for i in range(self.sim_num):
            for j in range(75):
               self.countlst2[i].append(sum(self.countlst[i][j] for j in range(j+1)))
    
    
    # Drawings and calculations    
    def analysis(self): 
        x = [i for i in range(75)] # Set x-axis
        # Longitudinal calculation of mean,max,min,std,median
        ymean = np.average(self.countlst2, axis=0) 
        ymax = np.max(self.countlst2, axis=0) 
        ymin = np.min(self.countlst2, axis=0) 
        ystd = np.std(self.countlst2, axis=0) 
        ymedian = np.median(self.countlst2, axis=0)
        # Calculate quantiles
        yquantile0_25 = [] 
        yquantile0_75 = []
        for j in range(75):
            t = pd.Series([self.countlst2[i][j] for i in range(self.sim_num)])
            yquantile0_25.append(t.quantile(0.25)) # Calculate 0.25 quantile per column
            yquantile0_75.append(t.quantile(0.75)) # Calculate 0.75 quantile per column
        # Plot average, maximum and minimum curves
        plt.plot(x, ymean, linewidth=2) 
        plt.plot(x, ymax, linewidth=2, linestyle = "--") 
        plt.plot(x, ymin, linewidth = 2, linestyle = "--") 
        # Plotting standard deviation ranges
        plt.fill_between(x, ymean-ystd, ymean+ystd, alpha = 0.3) 
        # Set horizontal and vertical coordinates and title
        plt.xlabel("Total Numbers Called")
        plt.ylabel("Winners")
        plt.title("Number of Winners per numbers called")
        plt.show()


        # Print Calculation Form
        pdf = FPDF(format='letter', unit='in')
        pdf.add_page()# Add new page.
        # Set format
        epw = pdf.w - 2* pdf.l_margin# Effective page width
        col_width = 1
        data = [[' ', 'mean', 'max', 'min', 'std', 'median','quantile(0.25)','quantile(0.75)']]# Headers from data matrix.
        # Generate the calculated list
        for i in range(75):
            data.append([i+1, ymean[i], ymax[i], ymin[i], round(ystd[i],2),ymedian[i],yquantile0_25[i], yquantile0_75[i]])
        # Set format
        pdf.set_font('Times', 'B', 14.0)# Document title centered, 'B'old, 14 pt
        pdf.cell(epw, 0.0, 'Centrality', align='C')
        pdf.set_font('Times', '', 10.0)
        pdf.ln(0.5)
        th = pdf.font_size# Text height
        # Generate table
        for row in data:
            for datum in row:
                pdf.cell(col_width, th, str(datum), border=1, align="C")# Enter data in colums
            pdf.ln(th)
        pdf.output('table.pdf', 'F')


    # Setup to run
    def run(self): 
        self.generator()
        self.transfer()
        self.analysis()


b = Bingo()
b.run()