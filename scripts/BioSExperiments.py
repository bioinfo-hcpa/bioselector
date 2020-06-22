import sys
import os
from time import time

from engine.DataManager import DataManager
from engine.Hybrid import Hybrid
from engine.Heterogeneous import Heterogeneous
from engine.Homogeneous import Homogeneous
from engine.SingleFS import SingleFS
from engine.Evaluator import Evaluator
from engine.InformationManager import InformationManager


class BioSExperiments:

    def __init__(self, experiments, results_path):

        self.experiments = experiments
        self.results_path = results_path + "/"
        self.ths = [1, 5, 10, 15]   # i forgot to add those in the frontend, so for now they're fixed



    def mount_experiment_folder_name(self, i, count, exp, ds_path):

        sufix = "_E" + str(count+i) + "/"
        rad = exp.type

        for d in exp.datasets:
            dataset_file_name = d.split('/')[-1].split('.')[0]   # consider using dataset title in the future
            rad += "_" + dataset_file_name

        return rad+sufix



    def run(self):
        
        exp_count = sum(os.path.isdir(self.results_path+i) for i in os.listdir(self.results_path))
        if exp_count == 0:
            exp_count +=1   # just to start right since the below 'enumerate' starts with index 0


        for i, exp in enumerate(self.experiments):
            for dataset_path in exp.datasets:
            
                exp_name = self.mount_experiment_folder_name(i, exp_count, exp, dataset_path)
                complete_results_path = self.results_path + exp_name

                int_folds = round(int(exp.folds))
                int_seed = round(int(exp.seed))
                int_bootstraps = round(int(exp.bootstraps))

                if exp.type == 'sin':
                    self.perform_selection_single(dataset_path, complete_results_path, exp.selectors,
                                                    int_folds, int_seed, self.ths)

                elif exp.type == 'hom':
                    self.perform_selection_hom(dataset_path, complete_results_path,
                                                exp.selectors, exp.aggregators[0], int_folds,
                                                int_bootstraps, int_seed, self.ths)

                elif exp.type == 'het':
                    self.perform_selection_het(dataset_path, complete_results_path,
                                                exp.selectors, exp.aggregators[0], int_folds,
                                                int_seed, self.ths)
                    
                elif exp.type == 'hyb':
                    self.perform_selection_hyb(dataset_path, complete_results_path,
                                                exp.selectors, exp.aggregators[0], exp.aggregators[1], 
                                                int_folds, int_bootstraps, int_seed, self.ths)
        return


    def compute_print_time(self, st):
        
        print("\n\nTIME TAKEN:")
        end = time()
        try:
            hours, rem = divmod(end-st, 3600)
            minutes, seconds = divmod(rem, 60)
    
            print("{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds))
        except:
            print(end-st)
        
        sys.stdout.flush()
        return



    def perform_selection_hyb(self, dataset_path, results_path, selectors, aggregator1, aggregator2,
                                num_folds, num_bootstraps, seed, ths):
        
        str_aggregators = [aggregator1, aggregator2]
        str_selectors = [i[0] for i in selectors]

        dm = DataManager(results_path, dataset_path, num_bootstraps, num_folds, seed)
        dm.encode_main_dm_df()
        dm.create_results_dir()
        dm.init_data_folding_process()

        ev = Evaluator(dm, ths, False)
        im = InformationManager(dm, ev, str_selectors, str_aggregators)
        ensemble = Hybrid(dm, selectors, aggregator1, aggregator2, ths)

        st = time()
        ensemble.select_features()
        self.compute_print_time(st)

        print("\n\nDecoding dataframe...")
        sys.stdout.flush()
        dm.decode_main_dm_df()

        print("\nStarting evaluation process...")
        sys.stdout.flush()
        ev.evaluate_final_rankings()

        print("\n\nCreating csv files...")
        sys.stdout.flush()
        im.create_csv_tables()

        print("\nEvaluating inner levels...")
        sys.stdout.flush()
        level1_evaluation, level2_evaluation = ev.evaluate_intermediate_hyb_rankings()

        print("\n\nCreating csv files...")
        sys.stdout.flush()
        im.create_intermediate_csv_tables(level1_evaluation, level2_evaluation)

        print("\nDone!\n\n")
        print("#################################################################\n")
        sys.stdout.flush()
        return


    def perform_selection_het(self, dataset_path, results_path, selectors, 
                                aggregator, num_folds, seed, ths):

        str_aggregators = [aggregator]
        str_selectors = [i[0] for i in selectors]
        num_bootstraps = 0

        dm = DataManager(results_path, dataset_path, num_bootstraps, num_folds, seed)
        dm.encode_main_dm_df()
        dm.create_results_dir()
        dm.init_data_folding_process()
        
        ev = Evaluator(dm, ths, False)
        im = InformationManager(dm, ev, str_selectors, str_aggregators)
        ensemble = Heterogeneous(dm, selectors, aggregator, ths)

        st = time()
        ensemble.select_features()
        self.compute_print_time(st)

        print("\n\nDecoding dataframe...")
        sys.stdout.flush()
        dm.decode_main_dm_df()

        print("\nStarting evaluation process...")
        sys.stdout.flush()
        ev.evaluate_final_rankings()

        print("\n\nCreating csv files...")
        sys.stdout.flush()
        im.create_csv_tables()

        print("\nDone!\n\n")
        print("#################################################################\n")
        sys.stdout.flush()
        return

    

    def perform_selection_hom(self, dataset_path, results_path, selector, 
                                aggregator, num_folds, num_bootstraps, seed, ths):

        str_aggregators = [aggregator]
        str_selectors = selector[0][0]

        dm = DataManager(results_path, dataset_path, num_bootstraps, num_folds, seed)
        dm.encode_main_dm_df()
        dm.create_results_dir()
        dm.init_data_folding_process()

        ev = Evaluator(dm, ths, False)
        im = InformationManager(dm, ev, str_selectors, str_aggregators)
        ensemble = Homogeneous(dm, selector, aggregator, ths)

        st = time()
        ensemble.select_features() 
        self.compute_print_time(st)

        print("\n\nDecoding dataframe...")
        sys.stdout.flush()
        dm.decode_main_dm_df()

        print("\nStarting evaluation process...")
        sys.stdout.flush()
        ev.evaluate_final_rankings()

        print("\n\nCreating csv files...")
        sys.stdout.flush()
        im.create_csv_tables()

        print("\nDone!\n\n")
        print("#################################################################\n")
        sys.stdout.flush()
        return

    

    def perform_selection_single(self, dataset_path, results_path, 
                                selector, num_folds, seed, ths):

        str_aggregators = ["No aggregation"]
        num_bootstraps = 0
        str_selectors = selector[0][0]    # because selector is always a list, even when it have only one element

        dm = DataManager(results_path, dataset_path, num_bootstraps, num_folds, seed)
        dm.encode_main_dm_df()
        dm.create_results_dir()
        dm.init_data_folding_process()

        ev = Evaluator(dm, ths, False)
        im = InformationManager(dm, ev, str_selectors, str_aggregators)
        feature_selector = SingleFS(dm, selector, ths)

        st = time()
        feature_selector.select_features()
        self.compute_print_time(st)

        print("\n\nDecoding dataframe...")
        sys.stdout.flush()
        dm.decode_main_dm_df()

        print("\nStarting evaluation process...")
        sys.stdout.flush()
        ev.evaluate_final_rankings()

        print("\n\nCreating csv files...")
        sys.stdout.flush()
        im.create_csv_tables()

        print("\nDone!\n\n")
        print("#################################################################\n")
        sys.stdout.flush()
        return

