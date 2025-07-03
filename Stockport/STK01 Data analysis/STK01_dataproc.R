
library(tidyverse)


# this bit reads in the files and uses part of the filename to make a new "subj" variable
all_files <- list.files("Raw Data", full.names = TRUE) # needed for reading data
#test_files <- list.files("Raw Data", pattern = "test", full.names = TRUE) # needed for reading data

all_data <- NULL #create an empty data file to put the results of the loop

# this loops around all the files in the directory, reading in and processing each one
for (subj in 1:length(all_files)) {
  pData <- read_csv(all_files[subj], col_names = TRUE, show_col_types = FALSE) #read in the csv files
  
  pd1 <- 
    pData %>% 
    #select the important columns
    select(c(age,
             gender,
             tNum1 = stage1_trials.thisN,
             tNum2 = stage2_trials.thisN,
             tNum3 = stage3_trials.thisN,
             cue1, 
             cue2,
             cue3,
             outcome)) %>% 
    drop_na(cue1) %>% # drop na rows
    mutate(trial = rowSums(across(tNum1:tNum3)+1, na.rm = TRUE), .keep = "unused", .before = "cue1") %>% 
    mutate(pNum = sprintf("STK%03d", subj), # make a 3 digit code of the participant number 
           date_time = substr(all_files[subj], 31, 53), .before = "age") # get the date and time of session
           
  
  # these other columns are out of step (fuck knows why...)
  pd2 <- 
    pData %>% 
    # rename some columns
    select(resp = cue_o_mouse.clicked_name,
           accuracy = correct_answer,
           RT = cue_o_mouse.time, 
           order) %>% 
    drop_na(order) # drop NAs in the order column
  
  pAll <- cbind(pd1, pd2) # now we can put them back together
  
  pAll <- 
    pAll %>% 
    mutate(block = rep(1:21, each = 10), .before = trial) # create a block variable (blocks 1 to 21, 10 trials each)
  
  all_data <- rbind(all_data, pAll) # add this participant's data to the main dataframe (which is growing each loop)

}
  
# formatting of columns

# create a tt column - this stuff is particular to the design and may not be relevant
all_data <- 
  all_data %>% 
  mutate(across(c(cue1:cue3), ~ case_when(. %in% c("N","M") ~ NA,
                                          TRUE ~ .))) %>% 
  unite("tt", cue1:cue3, na.rm = TRUE, sep = "")

# recode outcome and response columns
all_data <- 
  all_data %>% 
  mutate(across(c(outcome:resp), ~ case_when(. == "o2_image" ~ "O2",
                                           . == "o1_image" ~ "O1")))

# make a phase variable
all_data <- 
  all_data %>% 
  mutate(phase = case_when(block %in% c(1:12) ~ "1",
                           block %in% c(13:18) ~ "2",
                           block %in% c(19:21) ~ "3"),
         .before = block)


save(all_data, file = "STK01_all_data.RData") # save the data as a .RData (which is a nice format)
