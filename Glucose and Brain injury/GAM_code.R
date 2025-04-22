library(dplyr)
library(readxl)
library(ggpubr)
library(Hmisc)
library(corrplot)
library(ggplot2)
library(gplots)
library(glue)
library(mgcv)
library(ggeffects)

                              
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

data_name <- <here use a proper path>                                           

                                                                                                   
df <- read.csv(data_name, header = TRUE)

#Modify the 'dd_eg_rn_decimal' column in the df
df$dd_eg_rn_decimal <- round(df$dd_eg_rn_decimal, 2)


#Create groups of gestational age 
df$eg_group <- ifelse(df$dd_eg_rn_decimal <= 28, 1, 0)

#Create groups of gestational age 
df$eg_classes <- cut(df$dd_eg_rn_decimal,
                  breaks = c(-Inf, 23.99, 26, 29, 33),
                  labels = c(NA, "0", "1", "2"),
                  right = TRUE)


df$monitoring_days <- df$elapsed_time/24

df <- df%>%subset( select = -c(`Date_of_birth`, `Time_of_birth`, `Time`, `date_time`, `Date`))
df <- df%>%subset( select = -c(`delta_time`))

colnames(df)

# Which features should be considered as factors (categorical features)

df <- df %>% rename('Sex' = 'dd_sexo',
              'Gestational diabetes' = 'dp_diabetes',
              'Gestational age' = 'eg_group',
              'Classes gestational age' = 'eg_classes',
              'Prenatal steroids' = 'dp_esteroides_prenatales',
              'Small for gestational age' = 'dd_peg_p10',
              'Late sepsis' = 'co_sepsis_tardia',
              'Parenchymal hemorrhagic infarction' = 'eco_ihp',
              'GMH & PHI' = 'hmg3_ihp',
              'Bronchopulmonary dysplasia' = 're_dbp_mild_severe',
              'Hemodynamically significant ductus arteriosus' = 're_ductus_hs',
              'Severe retinopathy' = 're_retinopathy_severe',
              'White matter injury' = 'eco_lsb',
              'White matter injury light to severe' = 're_eco_lsb_light_severe',
              'White matter injury mild to severe' = 're_eco_lsb_severe',
              'Germinal matrix hemorrhage' = 'eco_hmg',
              'Germinal matrix hemorrhage mild to severe' = 're_eco_hmg_mild_severe',
              'Germinal matrix hemorrhage severe' = 're_eco_hmg_severe',
              'Apgar 1' = 'dp_apgar_1',
              'Apgar 5' = 'dp_apgar_5')

factor_variables <- c('Sex', 'Gestational diabetes',
                      'Prenatal steroids', 'Small for gestational age',
                      'Late sepsis', 'Parenchymal hemorrhagic infarction', 'GMH & PHI',
                      'Bronchopulmonary dysplasia', 'Hemodynamically significant ductus arteriosus',
                      'Severe retinopathy', 'White matter injury',
                      'White matter injury light to severe', 'White matter injury mild to severe',
                      'Germinal matrix hemorrhage', 'Germinal matrix hemorrhage severe',
                      'Apgar 1','Apgar 5')



for(i in factor_variables){
  print(length(unique(df[,grep(i, colnames(df))])))
}


# Which features should be considered as continuous
continuous_variables <-  c('Glucose','monitoring_days', 'PMA')


for(i in continuous_variables){
  print(length(unique(df[,grep(i, colnames(df))])))
}


df[factor_variables] <- lapply(df[factor_variables], as.factor)

# Make the ordinal variables integers
df[continuous_variables] <- lapply(df[continuous_variables], as.numeric)



# Plot Parameters
line_size_ <- 0.3
size_ <- 1
alpha_ <- 0.5
legend_size <- 10
width_ <-  16
height_ <- 9
res_ <- 300


## Change the column names
colnames(df) <- gsub(" ", replacement = "_", colnames(df))
colnames(df) <- gsub("&", replacement = "", colnames(df))

factor_variables <- gsub(" ", replacement = "_", factor_variables)
factor_variables <- gsub("&", replacement = "", factor_variables)

## Create ists to save the models and the results
gam_results <- list()
gam_models <- list()

## Dataframes to store the results in a structured manner
results_df <- data.frame(Covariate = character(), AIC = numeric(),
                         Deviance_Explained = numeric(), P_val = numeric(), 
                         stringsAsFactors = FALSE)
overall_summary <- data.frame(Model = character(), term = character(),
                              Effective_Degrees_of_Freedom = numeric(), P_value = numeric(), stringsAsFactors = FALSE)

path_to_plot <- paste0("./GAM_results")

### Outer loop through the continuous variables [monitoring time, PMA]
for(f_feat in continuous_variables){
  if(f_feat == 'Glucose'){
  next
  }
  if(f_feat == 'elapsed_time') x_name <- 'Monitoring Hours'
  if(f_feat == 'monitoring_days') x_name <- 'Monitoring Days'
  if(f_feat == 'PMA') x_name <- 'PMA'
  
  df[[f_feat]] <- as.numeric(df[[f_feat]])
  ## Creation of a null model that checks how glucose changes over the time variable only
  baseline_formula <- as.formula(glue("Glucose ~ s(`{f_feat}`) + s(ID, bs = 're')"))
  baseline_gam_model <- bam(formula = baseline_formula, data = df)
  
  ## Flag to use in case we need to fit the model again if there are NaN in the data
  flg = FALSE
  
  ## Inner loop through the covariates
  for(cov in factor_variables){
    
    ## Check if the flag is "raised". If yes it re-fits the baseline model
    if(flg){
      baseline_formula <- as.formula(glue("Glucose ~ s(`{f_feat}`) + s(ID, bs = 're')"))
      baseline_gam_model <- bam(formula = baseline_formula, data = df)
    }
    
    ## Change the covariate name for aesthetic resons
    cov_name <- gsub("_", " ", cov)
    cov_name <- gsub("  ", " & ", cov_name)
    model_name <- glue("{f_feat} - {cov_name}")
    
    print(glue('Glucose ~ {f_feat} + {cov_name} '))
    
    
    ## GAM formula and model fit
    formula_gam <- as.formula(glue("Glucose ~ s(`{f_feat}`, by = `{cov}`, k=-1, bs = 'cs') + `{cov}` + s(ID, bs = 're')")) # + s(ID, bs = 're'
    bam_model <- bam(formula = formula_gam, data = df)
    
    ### This gives each level's statistics
    smr_temp <- summary(bam_model)
    
    ## Keep the statistics of each interaction of time:covariate_level in the model
    for (i in c(2:nrow(smr_temp$p.table))){
      term_i <- rownames(smr_temp$p.table)[i]
      edf_i <- smr_temp$p.table[i,1]
      p.val_i <- smr_temp$p.table[i,4]
      overall_summary <- rbind(overall_summary, data.frame(Model = model_name,
                                                           term = term_i,
                                                           Effective_Degrees_of_Freedom = edf_i,
                                                           P_value = p.val_i))
    }
    
    ## Save the models and the summary in the lists
    gam_models[[glue("{f_feat} - {cov}")]] <- bam_model
    gam_results[[glue("{f_feat} - {cov}")]] <- smr_temp
    
    ## Calculate the statistics to evaluate the fit
    aic_value <- AIC(bam_model)
    dev_expl <- round(smr_temp$dev.expl * 100, digits = 2)
    
    ## Check if there are missing values in the specific covariate, if yes, re-fit the base model by eliminating the NaN rows
    if(any(is.na(df[[cov]]))){
      baseline_gam_model <- bam(formula = baseline_formula, data = df[which(!is.na(df[[cov]])),c('ID','Glucose', f_feat, cov)])
      flg = TRUE
    }
    
    ## Test if the baseline model and the GAM model are statistically different
    models_anova <- anova(baseline_gam_model, bam_model, test = "Chisq")
    models_p_val <- ifelse(nrow(models_anova) > 1, models_anova$`Pr(>Chi)`[2], NA)
    
    ## Save the results in a Dataframe
    results_df <- rbind(results_df, data.frame(Covariate = cov_name,
                                               AIC = aic_value,
                                               Deviance_Explained = dev_expl,
                                               P_val = models_p_val))
    
    # Produce and save the images
    jpg_path <- paste0(path_to_plot,"/GAM_Glucose_VS_", f_feat,"_", cov ,".jpg")
    jpeg(filename = jpg_path, units="cm", width=width_,height=height_, res=res_)

    plt <- ggplot(df, aes(df[[f_feat]], Glucose)) + 
      geom_smooth(aes(color = df[[cov]]),method='gam', 
                  fullrange = TRUE, linewidth=line_size_) +
      labs(title = glue('GAM: Glucose Over {x_name} by {cov_name}'),
           x = x_name, y = "Glucose [estimated]", color = paste(strwrap(cov_name,width = 17), collapse = '\n')) +
      theme_bw() +
      theme(legend.position = "right",
            legend.text = element_text(size = legend_size),
            legend.title = element_text(size = legend_size+1),
            legend.title.align = 0.5,
            plot.title = element_text(size = 12),
            plot.subtitle = element_text(size = 9))

    print(plt)
    dev.off()
  }
}
