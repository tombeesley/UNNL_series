
library(calmr)
library(tidyverse)

theme_set(theme_minimal(base_size = 14))

simple_uncertainty_LP_design <- data.frame(
  Group = c("certain_LP", "uncertain_LP", "partial_simple"),
  Phase1 = c("20AV(O1)/20AW(O1)/20BV(O2)/20BW(O2)", # certain AX-1, AY-1, BX-2, BY-2
             "16AV(O1)/4AV(O2)/16AW(O1)/4AW(O2)/16BV(O2)/4BV(O1)/16BW(O2)/4BW(O1)", # uncertain (0.8) AX-1, AY-1, BX-2, BY-2
             "32A(O1)/8A(O2)/32B(O2)/8B(O1)"), # uncertain (0.8) A-1, B-2 
  R1 = c(TRUE)
)


# parsing the design and showing the original and what was detected
parsed <- parse_design(simple_uncertainty_LP_design)




### Run simulation - RW simple

pars_RW1972 <- get_parameters(simple_uncertainty_LP_design, model = "RW1972")

LP_simple_RW <- run_experiment(
  simple_uncertainty_LP_design, # note we do not need to pass the parsed design
  model = "RW1972",
  parameters = pars_RW1972,
  iterations = 10
)


### Plot the results - RW

# calculate and plot Vs

vs_res <-
  results(LP_simple_RW)[["associations"]] %>%
  filter(s1 %in% c("A", "B", "V", "W"),
         s2 %in% c("O1", "O2")) %>%
  group_by(group, trial, s1, s2) %>%
  summarise(value = mean(value))

vs_res %>%
  ggplot(aes(x = trial, y = value, colour = s1)) +
  geom_line() +
  facet_grid(rows = vars(group), cols = vars(s2)) +
  labs(title = "Associative Strengths",
       colour = "Cue")



