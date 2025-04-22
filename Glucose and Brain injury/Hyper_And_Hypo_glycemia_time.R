library(groupdata2)
library(glmnet)
library(tidyr)
library(dplyr)
library(readxl)
library(ggpubr)
library(Hmisc)
library(corrplot)
library(ggplot2)
library(gplots)
library(mgcv)
library(glue)
library(tidyverse)
library(broom)
library(ROCit)
library(tibble)
library(caret)
library(pROC)


setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

#--------------------Calculate average, hyper and hypo--------------#


get_duration_of_hyperglycemia <- function(result, df, starts, ends){
  
  run_info <- data.frame(
    run = seq_along(result$lengths),
    on = result$values,
    start_index = starts,
    end_index = ends,
    start_time = df$date_time[starts],
    end_time = df$date_time[ends],
    duration = difftime(df$date_time[ends], df$date_time[starts], units = 'hours')
  )
  
  # Filter to include only the fragments where the condition was TRUE
  on_fragments <- run_info[run_info$on, ]
  #print(on_fragments)
  #print(sum(on_fragments$duration))
  return(sum(on_fragments$duration))
}


### Inputting the glucose (time-series) data
input_file_name = insert_the_input_path_here
df <- read.csv(input_file_name, header = TRUE)


unique_ids <- unique(df$ID)

## Creating thresholds for Hyper/Hypo glycemia levels
thresholds <- c(125, 150, 180, 250)
low_threshold = 47

## Initialize the dataframe, and list to be saved at the end 
result_df <- data.frame(ID = character(), Hyper_A = numeric(), Hyper_B = numeric(), 
                        Hyper_C = numeric(), Hyper_D = numeric(), Hypo = numeric(),
                        Hyper = numeric(), Hyper_A_perc = numeric(), Hyper_B_perc = numeric(), 
                        Hyper_C_perc = numeric(), Hyper_D_perc = numeric(), Hypo_perc = numeric(),
                        Hyper_perc = numeric(), label = numeric())
mean_glucose_list <- list()


## Loop through IDs
for (id in unique_ids){
  ## For the first day. Elapsed time is measured in hours!
  hours_to_keep = 24
  df_temp <- df %>% filter(ID == id & elapsed_time <= hours_to_keep)
  print(id)
  print(quantile(df_temp$Glucose))
  
  ## Loop through the thresholds
  for (i in c(1:length(thresholds))){
    print(glue("{thresholds[i]} - {thresholds[i+1]}"))
    
    ## When checking the last threshold (>250 mg/dL):
    if (i == length(thresholds)) {
      within_thresholds <- df_temp$Glucose > thresholds[i]
      
      ## Create a list of fragments in case there are missing values in the data
      rle_results <- rle(within_thresholds)
      num_fragments <- sum(rle_results$values)
      cat(glue("Number of fragments above the {thresholds[i]} threshold: {num_fragments}"),"\n")
      ends <- cumsum(rle_results$lengths)
      starts <- c(1, head(ends, -1) + 1)
      
      if(num_fragments>=3){
      total_time_hyper_d <- get_duration_of_hyperglycemia(rle_results, df = df_temp, starts = starts, ends = ends)
      } else{
        total_time_hyper_d <- 0
      }
      perc_time_hyper_d <- 100 * total_time_hyper_d / 24
      break
    }
    
    ## for the cases of 125 - 150, 150 - 180, 180 - 250 mg/dL
    within_thresholds <- df_temp$Glucose > thresholds[i] & df_temp$Glucose < thresholds[i+1]
    
    ## Create a list of fragments in case there are missing values in the data
    rle_results <- rle(within_thresholds)
    num_fragments <- sum(rle_results$values)
    cat(glue("Number of fragments between the range {thresholds[i]} - {thresholds[i+1]}: {num_fragments}"),"\n")
    ends <- cumsum(rle_results$lengths)
    starts <- c(1, head(ends, -1) + 1)
    
    if(num_fragments>=3){
      time_within <- get_duration_of_hyperglycemia(rle_results, df = df_temp, starts = starts, ends = ends)
    } else{
      time_within <- 0
    }
    
    # for 125 - 150 mg/dL
    if (i==1){
      total_time_hyper_a <- time_within
      perc_time_hyper_a <- 100 * total_time_hyper_a / 24 
    }
    # for 150 - 180 mg/dL
    else if (i==2){
      total_time_hyper_b <- time_within
      perc_time_hyper_b <- 100 * total_time_hyper_b / 24
    }
    # for 180 - 250 mg/dL
    else if (i==3){
      total_time_hyper_c <- time_within
      perc_time_hyper_c <- 100 * total_time_hyper_c / 24
    }
  }
  
  ## Find the time the sample had Hypoglycemia
  below_threshold <- df_temp$Glucose < low_threshold
  
  ## Create a list of fragments in case there are missing values in the data
  rle_results <- rle(below_threshold)
  num_fragments <- sum(rle_results$values)
  cat(glue("Number of fragments below the {low_threshold} threshold: {num_fragments}"),"\n")

  ends <- cumsum(rle_results$lengths)
  starts <- c(1, head(ends, -1) + 1)
  
  if(num_fragments>=3){
    total_time_hypo <- get_duration_of_hyperglycemia(rle_results, df = df_temp, starts = starts, ends = ends)
  } else{
    total_time_hypo <- 0
  }
  perc_time_hypo <- 100 * total_time_hypo / 24
  
  ## Update the dataframe by adding a row to it with the results
  mean_glucose_col = mean(df_temp$Glucose)
  total_time_hyper = sum(c(total_time_hyper_a, total_time_hyper_b, total_time_hyper_c, total_time_hyper_d))
  perc_time_hyper <- 100 * total_time_hyper / 24
  result_df <- rbind(result_df, data.frame(ID = id, mean_glucose = mean_glucose_col,
                                           Hypo = total_time_hypo, Hyper = total_time_hyper,
                                           Hyper_A = total_time_hyper_a, Hyper_B = total_time_hyper_b,
                                           Hyper_C = total_time_hyper_c, Hyper_D = total_time_hyper_d,
                                           Hyper_A_perc = perc_time_hyper_a, Hyper_B_perc = perc_time_hyper_b, 
                                           Hyper_C_perc = perc_time_hyper_c, Hyper_D_perc = perc_time_hyper_d,
                                           Hypo_perc = perc_time_hypo, Hyper_perc = perc_time_hyper,
                                           label = df_temp$eco_lsb[1]))
  
  
  }


result_df <- round(result_df, 2)

# print(result_df)



####################### SOME PLOTS ################################



# Reshape total times from wide to long format
df_long_times <- result_df %>%
  pivot_longer(
    cols = c(Hypo, Hyper_A, Hyper_B, Hyper_C, Hyper_D, Hyper),
    names_to = "Condition",
    values_to = "TotalTime"
  )


ggplot(df_long_times, aes(x = Condition, y = TotalTime, fill = Condition)) +
  geom_boxplot() + scale_fill_brewer(palette = "Accent") +
  facet_wrap(~ label, labeller = labeller(label = c('0' = 'No White Matter Injury', '1' = "White Matter Injury"))) +
  labs(title = "Distribution of Total Times for the abnormal glucose types by Condition",
       x = "Type of abnormal glocose level", y = "Total Time (hours)") +
  theme_minimal()+
  theme(axis.text.x = element_text(angle = 0, hjust = 1, size = 18),
        legend.position = "none",
        axis.title.x = element_text(size = 18, margin = margin(t = 25)),
        axis.title.y = element_text(size = 18, margin = margin(r = 25)),
        axis.text.y = element_text(size = 18),
        strip.text = element_text(size = 16), 
        plot.title = element_text(size = 18 ,margin = margin(b = 20)))


#### Mean glucose
ggplot(result_df, aes(x = as.factor(label), y = mean_glucose, fill = as.factor(label))) +
  geom_violin(fill = "lightblue", color = "gray", alpha = 0.5) +
  geom_boxplot(width = 0.1)+ scale_fill_brewer(palette = "Accent") +
  #facet_wrap(~ label, labeller = labeller(label = c('0' = 'No White Matter Injury', '1' = "White Matter Injury"))) +
  labs(title = "Mean glucose levels over 24h of monitoring by condition",
       x = "White Matter Injury", y = "Mean Glucose [mg/dL]") +
  scale_x_discrete(labels = c("0" = "No", "1" = "Yes")) +
  theme_minimal()+
  theme(axis.text.x = element_text(angle = 0, hjust = 0.5, size = 18),
        axis.text.y = element_text(size = 18),
        legend.position = "none",
        axis.title.x = element_text(size = 16, margin = margin(t = 25)),
        axis.title.y = element_text(size = 16, margin = margin(r = 25)),
        plot.title = element_text(size = 18 ,margin = margin(b = 20)))



