library(tidyverse)
library(afex)
library(ggrepel)

load("UNW01_proc_data.RData")


# analyse phase 1 in uncertain condition

data_p1 <- 
  data %>% 
  drop_na() %>% # coding error meant no "probable response" column for early Ps
  filter(phase == 1,
         accuracy != -99)


data_p1 %>% 
  group_by(pNum, cert_cond) %>% 
  summarise(meanProb = mean(prob_resp)) %>% 
  ggplot(aes(x = cert_cond, y = meanProb))+
  geom_boxplot(width = .2) +
  geom_point(size = 5, 
             alpha = .2) +
  geom_text_repel(aes(label = pNum), 
                  direction = 'y', 
                  nudge_x = .2, 
                  segment.colour = "red", 
                  colour = "red", 
                  segment.alpha = .2) +
  labs(title = "Boxplots with data labelled by participant ID",
       y = "Mean Probable response",
       x = "Certain condition")


data_unc_p1 %>% 
  group_by(block, cert_cond) %>% 
  summarise(meanProb = mean(prob_resp)) %>% 
  ggplot(aes(x = block, y = meanProb, colour = cert_cond, group = cert_cond)) +
  geom_point(size = 5) +
  geom_line(size = 1) +
  theme_classic(base_size = 14) +
  labs(x = "Blocks of 8 trials",
       y = "Proportion of probable responses",
       title = "Stage 1",
       colour = "Certainty condition") +
  scale_x_continuous(breaks = 1:15)


# analyse phase 2 and 3 performance

data_p23 <- 
  data %>% 
  filter(phase > 1,
         accuracy != -99)

data_p23 %>% 
  group_by(cert_cond, block, cue_type) %>% 
  summarise(meanAcc = mean(accuracy)) %>% 
  mutate(cue_type = as.factor(cue_type)) %>% 
  ggplot(aes(x = block, colour = cue_type, y = meanAcc)) +
  geom_point(size = 3) +
  geom_line(aes(group = cue_type)) +
  labs(x = "Blocks of 8 trials",
       y = "Proportion of accurate responses",
       title = "Accuracy of responses in stages 2 and 3",
       colour = "Cue training schedule") +
  facet_wrap(~cert_cond) +
  theme_classic()


# visualise test performance

test_data %>% 
  group_by(cert_cond, cue_type, association) %>% 
  summarise(meanRating = mean(rating),
            sd = sd(rating)) %>% 
  ggplot(aes(x = association, y = meanRating, fill = cert_cond)) +
  geom_col(position = position_dodge2()) +
  facet_wrap(~cue_type)

# work out how much was learned relative to baseline
test_data <- 
  test_data %>% 
  select(pNum, cert_cond, cue, association, cue_type, rating)

test_data_summary <- 
  test_data %>% 
  pivot_wider(names_from = association, values_from = rating) %>% 
  group_by(pNum, cert_cond, cue_type) %>% 
  summarise(across(not_paired:phase_1, mean)) %>% 
  mutate(phase_2_NL = phase_2_3 - not_paired)

test_data_sum %>% 
  group_by(cert_cond, cue_type) %>% 
  summarise(phase_2_effect = mean(phase_2_NL)) %>% 
  ggplot(aes(x = cert_cond, y = phase_2_effect, fill = cue_type)) +
  geom_col(position = position_dodge2())

aov_car(phase_2_NL ~ cert_cond + Error(pNum/cue_type), data = test_data_sum)




