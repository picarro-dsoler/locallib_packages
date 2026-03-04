import pandas as pd
import numpy as np

class CustomBinnedRER:
    def __init__(self,A,B,bin_floors):
        self.A = A
        self.B = B
        self.bin_floors = bin_floors
        #Set the bin labels       
        self.A_inv = list(reversed(self.A))

        #Set the system PBA matrix
        self.system_PBA =  pd.DataFrame(np.array([[0,0,0.16,0.84],[0,0.17,0.66,0.17],[0.17,0.66,0.17,0],[0.84,0.16,0,0]]),columns = self.B)
        self.system_PBA.index = self.A

        #Set the posterior probability matrix
        self.posterior_PAB = pd.DataFrame(columns=self.A, index=self.B)

        #Set the actual leak distribution
        self.actual_leak_distribution = pd.DataFrame(columns =['Probability', 'AverageFlow'], index = self.A)
        self.posterior_leak_distribution = pd.DataFrame(columns =['Probability', 'AverageFlow'], index = self.B)

        #Set the experiments variabl
        self.experiments = None


    #Set the experimental data and calculate the actual leak distribution
    def set_experiments(self, experiments):
        self.experiments = experiments
        self.set_actual_leak_distribution()


    def set_actual_leak_distribution(self, actual_leak_distribution = None):
        if actual_leak_distribution is not None:
            self.actual_leak_distribution = actual_leak_distribution
        else:
            if self.experiments is None:
                raise ValueError("Neither experimental data nor actual leak distribution is set")
            else:
                #Aggregate the data into bins
                df = pd.DataFrame(self.experiments, columns=['A'])
                df["Bin"] = pd.cut(df["A"], bins=self.bin_floors, labels=self.A_inv)
                out = df.groupby('Bin').agg({'A': ['count', 'mean', 'std']})
                out['Prob'] = out['A']['count']/out['A']['count'].sum()
                self.actual_leak_distribution['Probability'] = out['Prob']
                self.actual_leak_distribution['AverageFlow'] = out['A']['mean']
        return self.actual_leak_distribution

    def get_actual_leak_distribution(self):
        return self.actual_leak_distribution

    def get_posterior_probability_matrix(self):

        for b in self.B:
            for a in self.A:
                self.posterior_PAB.loc[b][a] = (self.system_PBA.loc[a][b]*self.actual_leak_distribution.loc[a]['Probability'])/self.system_PBA[b].dot(self.actual_leak_distribution['Probability'])
        return self.posterior_PAB

    def get_posterior_leak_distribution(self):
        for b in self.B:
            self.posterior_leak_distribution.loc[b]['Probability'] = self.system_PBA[b].dot(self.actual_leak_distribution['Probability'])
            self.posterior_leak_distribution.loc[b]['AverageFlow'] = self.posterior_PAB.loc[b].dot(self.actual_leak_distribution['AverageFlow'])
        return self.posterior_leak_distribution


class BinnedDistribution():
    def __init__(self,experiments = None,bin_labels = ['A-1','A0','A1','A2'],bin_floors = [1E-5,0.1,1,10,1E5]):
        self.experiments = experiments
        self.bin_labels = bin_labels
        self.bin_floors = bin_floors
        self.binned_distribution = pd.DataFrame()

    def set_binned_distribution(self):
        if self.experiments is None:
            raise ValueError("Neither experimental data nor actual leak distribution is set")
        else:
            #Aggregate the data into bins
            df = pd.DataFrame(self.experiments, columns=['A'])
            df["Bin"] = pd.cut(df["A"], bins=self.bin_floors, labels=self.bin_labels)
            out = df.groupby('Bin').agg({'A': ['count', 'mean', 'std']})
            out['Prob'] = out['A']['count']/out['A']['count'].sum()
            self.binned_distribution['Probability'] = out['Prob']
            self.binned_distribution['AverageFlow'] = out['A']['mean']
        return self.binned_distribution


class BinnedRER(CustomBinnedRER):
    def __init__(self):
        B = ['B-2','B-1','B0','B1']
        A = ['A1','A0','A-1','A-2']
        bin_floors = [1E-5,0.1,1,10,1E5]
        super().__init__(A,B,bin_floors)