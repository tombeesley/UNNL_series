# This script stitches together the data files into one dataframe.
# It then does some basic data cleaning, such as editing column names

# NOTE THIS IS NOT FINISHED YET

library(tidyverse)

# this bit reads in the files and uses part of the filename to make a new "subj" variable
all_files <- list.files("raw_data", full.names = TRUE) # needed for reading data
test_files <- list.files("raw_data", pattern = "test", full.names = TRUE) # needed for reading data
training_files <- setdiff(all_files, test_files) # find those that are not test files

data <- NULL
for (subj in 1:length(training_files)) { 
  pData <- read_csv(training_files[subj], col_types = cols(), col_names = TRUE) # read the data from csv
  if (ncol(pData) == 14){
    pData <- 
      pData %>% 
      mutate(out_response = NA, .before = accuracy)
  }
  # add in block column
  pData <- 
    pData %>% 
    mutate(block = rep(1:20, each = 8), .after = phase)
  # add in between_subjects condition
  pData <- 
    pData %>% 
    group_by(pNum) %>% 
    mutate(cert_cond = if_else(cert_cond[1L] == 1, "certain","uncertain")) %>% 
    mutate(prob_resp = case_when(cert_cond == "certain" ~ accuracy,
                                 cue1 == out_response ~ 1,
                                 TRUE ~ 0), 
           .after = accuracy)
    

  data <- rbind(data, pData) # combine data array with existing data
  
  
}

data <- 
  data %>% 
  mutate(cue = cue1, .after = block, .keep = "unused") %>% 
  mutate(cue_type = case_when(cue == 1 | cue == 3 ~ "10_trials",
                              cue == 2 | cue == 4 ~ "2_trials"),
         .after = block)

test_data <- NULL
for (subj in 1:length(test_files)) { 
  pData <- read_csv(test_files[subj], col_types = cols(), col_names = TRUE) # read the data from csv
  test_data <- rbind(test_data, pData) # combine data array with existing data
}
# add in association and cue type columns
test_data <- 
  test_data %>% 
  mutate(association = case_when(cue == 1 & outcome == 1 ~ "phase_1",
                                 cue == 1 & outcome == 2 ~ "phase_1_alt",
                                 cue == 1 & outcome == 3 ~ "phase_2_3",
                                 cue == 1 & outcome == 4 ~ "not_paired",
                                 cue == 2 & outcome == 1 ~ "phase_1_alt",
                                 cue == 2 & outcome == 2 ~ "phase_1",
                                 cue == 2 & outcome == 3 ~ "phase_2_3",
                                 cue == 2 & outcome == 4 ~ "not_paired",
                                 cue == 3 & outcome == 1 ~ "phase_2_3",
                                 cue == 3 & outcome == 2 ~ "not_paired",
                                 cue == 3 & outcome == 3 ~ "phase_1",
                                 cue == 3 & outcome == 4 ~ "phase_1_alt",
                                 cue == 4 & outcome == 1 ~ "phase_2_3",
                                 cue == 4 & outcome == 2 ~ "not_paired",
                                 cue == 4 & outcome == 3 ~ "phase_1_alt",
                                 cue == 4 & outcome == 4 ~ "phase_1"),
         cue_type = case_when(cue == 1 | cue == 3 ~ "10_trials",
                              cue == 2 | cue == 4 ~ "2_trials"),
         .after = cue)

# get participant numbers and conditions
p_conditions <- 
  data %>% 
  select(pNum, cert_cond) %>% 
  group_by(pNum) %>% 
  slice(1)

# join to test data
test_data <- 
  test_data %>% 
  left_join(y = p_conditions, by = "pNum") %>% 
  relocate(cert_cond, .after = pNum)

data_dem <- 
  data %>% 
  group_by(pNum) %>% 
  slice(1) %>% 
  select(exp_code, pNum, cert_cond, age, gender)

save(data, test_data, data_dem, file = "UNW01_proc_data.RData")

# creating save file for MK
Ps_MK <- data_dem$pNum[c(1:12, 17:27, 35:57)]

data <- 
  data %>% filter(pNum %in% Ps_MK)

data_dem <- 
  data_dem %>% filter(pNum %in% Ps_MK)

test_data <- 
  test_data %>% filter(pNum %in% Ps_MK)

save(data, test_data, data_dem, file = "UNW01_proc_data_MK.RData")

