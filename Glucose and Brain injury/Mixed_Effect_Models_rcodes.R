
library(dplyr)
library (Matrix)
library(lme4)
library(ggplot2)
library(afex)
library(ggpubr)
library(emmeans)
library(readxl)
library(glue)
library("ggpubr")
library("Hmisc")
library(corrplot)
library(ggplot2)
library(devtools)
library("ggpubr")
library(cluster)


#reading the file post normalisation and missing value impute
setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

data_name <- <Provide a path to the files>

lmData <- read.csv(data_name, header = TRUE)

## Drop columns of date of birth and time since we have the intervals and collapse time
lmData <- lmData%>%subset( select = -c(`Date_of_birth`, `Time_of_birth`, `Time`, `date_time`, `Date`))
lmData <- lmData%>%subset( select = -c(`delta_time`))


############### Continuous PMA #############
lmData$PMA_continuous <- lmData$PMA
for(sample_id in unique(lmData$ID)){
  
  PMAs <- unique(lmData[lmData$ID == sample_id, 'PMA'])
  
  for(i in 2:length(PMAs)){
    current_PMA <- PMAs[i]
    prev_PMA <- PMAs[i-1]
    lmData$PMA_continuous[lmData$ID == sample_id & lmData$PMA == prev_PMA] <- seq(prev_PMA, current_PMA, length.out = length(lmData[lmData$ID == sample_id & lmData$PMA == prev_PMA, 'PMA']))
  }
}


lmData$Gestational_Age_binary <- ifelse(lmData$dd_eg_rn_decimal <= 28, 1, 0)

lmData$Gestational_Age_triple <- cut(lmData$dd_eg_rn_decimal,
                                     breaks = c(-Inf, 23.99, 26, 29, 33),
                                     labels = c(NA, "0", "1", "2"),
                                     right = TRUE)

df <- lmData

############################################


# Find the columns with only one constant variable
if(length(which(apply(lmData, 2 ,function(x) length(unique(x)))<2))!=0){
  print('There are some variables with only one value throughout the dataset. They will be dropped!')
  lmData <- lmData%>%subset(select = -which(colnames(lmData) %in% colnames(lmData[which(apply(lmData,2,function(x) length(unique(x)))<2)])))
}else print('All good! Continue!')

# The following doesn't exist!
if('dd_perimetro_craneal' %in% colnames(lmData)){
  lmData$dd_perimetro_craneal[lmData$dd_perimetro_craneal>50] <- lmData$dd_perimetro_craneal[lmData$dd_perimetro_craneal>50]/10
}

# Drop the patient with wrong dates (ID = 319)
if(length(unique(lmData$ID[lmData$elapsed_time>500]))!=0){
  lmData <- lmData[-which(lmData$ID==unique(lmData$ID[lmData$elapsed_time>500])),]
}

table(sapply(lmData , typeof))
colnames(lmData)[which(sapply(lmData , typeof)=='double')]

# Find the distribution of unique values in the data
table(apply(lmData,2,function(x) length(unique(x))))

# Display the names of feature with missing values
colnames(lmData)[apply(lmData,2,function(x) any(is.na(x)))]

# Which features should be considered as factors (categorical features)

factor_variables <- c('ID','Gender', 'Gestational diabetes',
                      'Gestational Age binary', 'Gestational Age cat',
                      'Prenatal steroids', 'Small for gestational age',
                      'Late sepsis', 'Parenchymal hemorrhagic infarction', 'hmg3_ihp',
                      'Bronchopulmonary dysplasia', 'Hemodynamically significant ductus arteriosus',
                      'Severe retinopathy', 'White matter injury',
                      'White matter injury light to severe', 'White matter injury mild to severe')

for(i in factor_variables){
  print(paste(i, ': ',length(unique(lmData[,grep(i, colnames(lmData))]))))
}

# Which features should be considered as continuous

continuous_variables <-  c('Glucose','Elapsed time', 'Elapsed time days', 'PMA',
                           'dd_eg_rn_decimal', 'SNAP-PE II', 'PMA_continuous')
for(i in continuous_variables){
  print(paste(i, ': ',length(unique(lmData[,grep(i, colnames(lmData))]))))
}
# Which features should be considered as ordinal (The order counts)

ordinal_variables <-  c('Germinal matrix hemorrhage', 'Germinal matrix hemorrhage mild to severe',
                        'Germinal matrix hemorrhage severe',
                        'Apgar 1','Apgar 5')

for(i in ordinal_variables){
  print(paste(i, ': ',length(unique(lmData[,grep(i, colnames(lmData))]))))
}

backup_data <- lmData


### Imputation of missing values based on the type of the feature (continuous, ordinal or factor)
## Ordinal and categorical will be imputed with the most frequent value
## Continuous features will be imputed with the median value (because some times mean is meaningless)
for(feature in colnames(lmData)){
  
  if(feature %in% c(ordinal_variables, factor_variables) & any(is.na(lmData[feature]))){
    ##### If there are missing values in the ordinal/factor variables, impute with the most common value
    print(feature)
    print(paste('There are :',sum(is.na(lmData[feature])), 'missing values wich will be imputed with the most frequent value of the feature'))
    
    lmData[is.na(lmData[,feature]), feature] <- as.numeric(tail(names(sort(table(lmData[,feature]))), 1))
    print(table(lmData[,feature]))
    
    print(paste('Done, now there are ',sum(is.na(lmData[,feature])), 'missing values!'))
    
  }else if (feature %in% continuous_variables & any(is.na(lmData[feature]))){
    ##### If there are missing values in the continuous variables, impute with the median value
    print(feature)
    print(paste('There are :',sum(is.na(lmData[feature])), 'missing values wich will be imputed with the mean value of the feature'))
    
    lmData[is.na(lmData[,feature]), feature] <- median(as.matrix(lmData[,feature]), na.rm = TRUE) #Because some of them are in years like years of studies of parents
    
    print(paste('Done, now there are ',sum(is.na(lmData[feature])), 'missing values!'))
  }
}


summary(lmData[,colnames(lmData)[apply(lmData, 2, function(x) any(is.na(x)))]])

# Transform into factors the above features
lmData[factor_variables] <- lapply(lmData[factor_variables], as.factor)
# Make the ordinal variables integers
lmData[ordinal_variables] <- lapply(lmData[ordinal_variables], as.integer)

# Sanity check
typeof(lmData$Gender)
is.factor(lmData$Gender)

# check datatype of columns
table(sapply(lmData , typeof))

# Convert to factor (or grouping) variables.
if(!is.factor(lmData$ID)) lmData$ID <- as.factor(lmData$ID)

# Save the data
output_path <- './Mixed_Effect_Models_Results'
if(!dir.exists(output_path)){
  dir.create(output_path)
}else print('Directory exists!')
if(FALSE){
  write.csv(x = lmData, file = glue('{output_path}/Endpoint_A_C_D.csv'), row.names = FALSE)
  #write.csv(x = lmData, file = './All_patients.csv', row.names = FALSE)
}


cols <- colnames(lmData)
# check the data types
str(lmData)


# create an empty dataframe to store the data
dat <- as.data.frame(matrix(ncol=4, nrow=0))

## Get the index of where the factors and the continuous variables are!
index_of_factors <- which(colnames(lmData) %in% factor_variables)
index_of_continuous <- which(colnames(lmData) %in% continuous_variables)

### We check the factors only because for the continuous variables the computations for the interaction term goes out of hand
for(i in index_of_factors[2:length(index_of_factors)]){#[2:length(index_of_factors)]){ # from 2:end because we need to avoid ID
  print(cols[i])
  
  ## Initialize the output if it is the first iteration
  if(i == index_of_factors[2]){
    j = 1
    dat <- as.data.frame(matrix(ncol=4, nrow=0))
  }
  
  factor_i <- lmData[[cols[i]]]
  # creation of a mixed-effect model
  lmeModel = lmer(lmData$Glucose ~ factor_i*lmData$`Elapsed time` + (1|lmData$ID))
  # ANOVA analysis of the different factor levels and interactions
  res <- anova(lmeModel) # p-value
  
  rownames(res) <- c(cols[i], 'Elapsed_time', glue('{cols[i]}:Elapsed_time'))
  print(res)
  
  ## Save the ANOVA information
  factor_i_pval <- res[1,6]
  ElapseTime_pval <- res[2,6]
  Interaction_pval <- res[3,6]  
  dat[j,1] <- cols[i]
  dat[j,2] <- factor_i_pval
  dat[j,3] <- ElapseTime_pval
  dat[j,4] <- Interaction_pval
  
  j = j+1
}

colnames(dat) <- c("Feature_name","Feature_pvalue","EllapseTime_pvalue","Interaction_pvalue")


Feature_pvalue_FDR = p.adjust(dat$Feature_pvalue, method="BH", n=nrow(dat))
dat$Feature_pvalue_FDR <- Feature_pvalue_FDR

ElapseTime_pval_FDR = p.adjust(dat$EllapseTime_pvalue, method="BH", n=nrow(dat))
dat$ElapseTime_pval_FDR <- ElapseTime_pval_FDR

Interaction_pvalue_FDR = p.adjust(dat$Interaction_pvalue, method="BH", n=nrow(dat))
dat$Interaction_pvalue_FDR <- Interaction_pvalue_FDR

if(FALSE){
  output_folder <- glue("{output_path}/ANOVA_analysis")
  if(!dir.exists(output_folder)){
    print('creating the directory to save the data')
    dir.create(output_folder)
  }else print('Directory exists!')
  #write.csv(dat,file="results_group_comparisons/overall_stats_endpoint_A_C_D.csv",row.names = FALSE)
  write.csv(dat, file = glue("{output_folder}/ANOVA_endpoints_A_C_D.csv"), row.names = FALSE)
}


##### Plots #########

############## Factor variables ###################
factors_ <- cbind(lmData$Glucose, lmData[,factor_variables])
colnames(factors_) <- make.names(colnames(factors_), allow_ = TRUE)
colnames(factors_) <- gsub('\\.', '_', colnames(factors_))
colnames(factors_)[1] <- 'Glucose'
x_2 <- chiSquare(as.formula(paste("Glucose ~ ", paste(colnames(factors_), collapse= "+"))), data = factors_)



###########################################################################
 ############################ Function for plots #########################

run_analysis <- function(cor_res, comparison, lmData){
  
  colnames(lmData) <- gsub(' ', '_', colnames(lmData))
  lmData <- lmData[,-which(duplicated(colnames(lmData)))]
  colnames(cor_res$r) <- gsub(' ', '_', colnames(cor_res$r))
  rownames(cor_res$r) <- gsub(' ', '_', rownames(cor_res$r))
  colnames(cor_res$P) <- gsub(' ', '_', colnames(cor_res$P))
  rownames(cor_res$P) <- gsub(' ', '_', rownames(cor_res$P))
  
  #### Go to the plots and plot it now
  
  ## Get the correlation score only
  corrs <- cor_res$r
  rownames(corrs)[1] <- 'Glucose'
  colnames(corrs)[1] <- 'Glucose'
  
  #pvals<-res[3]$P[1:357,358:ncol(res[3]$P)]
  
  pvals <- cor_res$P
  rownames(pvals)[1] <- 'Glucose'
  colnames(pvals)[1] <- 'Glucose'
  for (i in 1:dim(pvals)[1]){
    if (i==1) {
      fdr_pvals <- p.adjust(pvals[1,], method = "BH", n = ncol(pvals))
      names(fdr_pvals) <- colnames(corrs)
    }else{
      new_fdr <- p.adjust(pvals[i,], method = "BH", n = ncol(pvals))
      names(new_fdr) <- colnames(corrs)
      fdr_pvals <- rbind(fdr_pvals, new_fdr)
    }
    
  }
  
  row.names(fdr_pvals) <- row.names(corrs)
  colnames(fdr_pvals) <- colnames(corrs)
  
  
  ##################################################
  
  output_path <- "Results"
  
  # Create the folder (output_path) if it doesn't exist
  if (!dir.exists(output_path)) {
    dir.create(output_path)
    message("Folder created: ", output_path)
  } else {
    message("Folder already exists: ", output_path)
  }
  
  dedicated_dir <- glue('{output_path}/All_Endpoints')
  if(!dir.exists(dedicated_dir)){
    cat(paste0('creating the directory! '))
    dir.create(dedicated_dir, recursive = TRUE)
    #setwd(dedicated_dir)
    print('Done!')
  }

  if(comparison == "Factors"){
    tmp <- cbind(corrs[,1], pvals[,1], fdr_pvals[,1])
    colnames(tmp) <- c("Correlation", "P.Value", "FDR")
    write.csv(tmp, glue('{dedicated_dir}/Correlation_Glucose_VS_Factors_A_C_D.csv'))
  }
  ######### Plot commands 
  ########               
  shape_ <- 16
  size_ <- 1
  alpha_ <- 0.5
  legend_size <- 10
  width_ <-  16
  height_ <- 9
  res_ <- 600
  
  for (i in 2:ncol(pvals)){
    #break
    # Chech only for the significant ones
    if (fdr_pvals[1,i]<0.05){
      feature_plot <- colnames(fdr_pvals)[i]
      if(feature_plot == 'ID') next
      
      # find the index of this feature in the main dataset
      index_map <- which(colnames(lmData) == feature_plot) #grep(feature_plot, colnames(lmData), ignore.case = TRUE, fixed = TRUE)
      print(feature_plot)
      
      if(is.factor(lmData[[feature_plot]])){
        
        categorical_path <- 'Glucose_Correlation_plots/new_plots/Categorical'
        if(!dir.exists(categorical_path)){
          cat(paste0('creating the directory! '))
          dir.create(categorical_path, recursive = TRUE)
          print('Done!')
        }
        
        ########################################################################
        
        image_name <- gsub(' ', '_', feature_plot)
        
        ####### dotplot
        png(filename=glue("./{categorical_path}/Glucose_VS_{image_name}.png"),
            units="cm", width=width_, height=height_, res=res_)
        myplot<-ggplot(lmData, aes(x=as.numeric(lmData[[feature_plot]]), y=Glucose)) +
          geom_jitter(size = size_, shape = shape_, alpha = alpha_) + # aes(color = lmData$ID)
          ggtitle(paste0("Cor: ",signif(corrs[1,i],2), ", q-val:",signif(fdr_pvals[1,i],2))) +
          geom_smooth(method=lm, se=FALSE) +
          labs(x = rownames(fdr_pvals)[i], y = rownames(fdr_pvals)[1], color = 'ID') +
          theme_bw() +
          theme(plot.title = element_text(hjust = 0.5), panel.background = element_blank(),
                axis.line = element_line(color="black"), axis.line.x = element_line(color="black")) +
          theme(legend.position = "right",
                legend.text = element_text(size = legend_size), legend.text.align = 1,
                legend.title = element_text(size = legend_size+1), legend.title.align = 1)
        print(myplot)
        dev.off()
        
        ####### Boxplots:
        png(filename=glue("./{categorical_path}/Glucose_VS_{image_name}_boxplot.png"),
            units="cm", width=width_, height=height_, res=res_)
        myplot<-ggplot(lmData, aes(x=lmData[,feature_plot], group=lmData[,feature_plot], y=Glucose)) + 
          geom_boxplot() + 
          labs(title=glue("Boxplot of Glucose per {feature_plot} level"),x=feature_plot)
        print(myplot)
        dev.off()
        
        ####### Boxplots:
        png(filename=glue("./{categorical_path}/Glucose_VS_{image_name}_boxplotDot.png"),
            units="cm", width=width_, height=height_, res=res_)
        myplot2 <- myplot + geom_jitter(shape=16, position=position_jitter(0.3), alpha = 0.05, colour = 'brown3')
        print(myplot2)
        dev.off()
        
        ######## Violin plots
        # Corrected png function call
        png(filename = glue("./{categorical_path}/Glucose_VS_{image_name}_Violin.png"), 
            units = "cm", width = width_, height = height_, res = res_)
        
        # Corrected ggplot code
        myplot3 <- ggplot(lmData, aes_string(x = feature_plot, group = feature_plot, y = "Glucose", fill = feature_plot)) + 
          geom_violin() +
          stat_summary(fun.data = mean_sdl, geom = "pointrange") +
          scale_fill_brewer(palette = "Accent") +
          labs(title = glue("Boxplot of Glucose per {feature_plot} level"), x = feature_plot) + 
          theme(legend.position = "none")
        
        print(myplot3)
        dev.off()


      }else if(is.integer(lmData[[feature_plot]])){
        
        ordinal_path <- 'Glucose_Correlation_plots/new_plots/Ordinal'
        if(!dir.exists(ordinal_path)){
          cat(paste0('creating the directory! '))
          dir.create(ordinal_path, recursive = TRUE)
          print('Done!')
        }
        
        if(!dir.exists(glue("./{ordinal_path}"))){
          print('creating the directory')
          dir.create(glue("./{ordinal_path}"), recursive = TRUE)
        }
        
        image_name <- gsub(' ', '_', feature_plot)
        
        ####### dotplot
        png(filename=glue("./{ordinal_path}/Glucose_VS_{image_name}.png"),
            units="cm", width=width_, height=height_, res=res_)
        myplot<-ggplot(lmData, aes(x=as.numeric(lmData[[feature_plot]]), y=Glucose)) +
          geom_jitter(size = size_, shape = shape_, alpha = alpha_) + # aes(color = lmData$ID)
          ggtitle(paste0("Cor: ",signif(corrs[1,i],2), ", q-val:",signif(fdr_pvals[1,i],2))) +
          geom_smooth(method=lm, se=FALSE) +
          labs(x = rownames(fdr_pvals)[i], y = rownames(fdr_pvals)[1], color = 'ID') +
          theme_bw() +
          theme(plot.title = element_text(hjust = 0.5), panel.background = element_blank(),
                axis.line = element_line(color="black"), axis.line.x = element_line(color="black")) +
          theme(legend.position = "right",
                legend.text = element_text(size = legend_size), legend.text.align = 1,
                legend.title = element_text(size = legend_size+1), legend.title.align = 1)
        print(myplot)
        dev.off()
        
        ####### Boxplots:
        png(filename=glue("./{ordinal_path}/Glucose_VS_{image_name}_boxplot.png"),
            units="cm", width=width_, height=height_, res=res_)
        myplot<-ggplot(lmData, aes(x=lmData[,feature_plot], group=lmData[,feature_plot], y=Glucose)) + 
          geom_boxplot() + 
          labs(title=glue("Boxplot of Glucose per {feature_plot} level"),x=feature_plot)
        print(myplot)
        dev.off()
        
        ####### Boxplots:
        png(filename=glue("./{ordinal_path}/Glucose_VS_{image_name}_boxplotDot.png"),
            units="cm", width=width_, height=height_, res=res_)
        myplot2 <- myplot + geom_jitter(shape=16, position=position_jitter(0.3), alpha = 0.05, colour = 'brown3')
        print(myplot2)
        dev.off()
        
        save.image('data.RData')
        ######## Violin plots
        png(filename=glue("./{ordinal_path}/Glucose_VS_{image_name}_Violin.png"),
            units="cm", width=width_, height=height_, res=res_)
        myplot3 <- ggplot(lmData, aes(x=lmData[,feature_plot], group=lmData[,feature_plot], y=Glucose, fill = as.factor(lmData[,feature_plot]))) + 
          geom_violin() +
          stat_summary(fun.data=mean_sdl, geom="pointrange") +
          scale_fill_brewer(palette="Accent") +
          labs(title=glue("Boxplot of Glucose per {feature_plot} level"),x=feature_plot) + 
          theme(legend.position="none")
        print(myplot3)
        dev.off()
        
      }else if(is.double(lmData[[feature_plot]])){
        
        Continuous_path <- 'Glucose_Correlation_plots/new_plots/Continuous'
        if(!dir.exists(Continuous_path)){
          cat(paste0('creating the directory! '))
          dir.create(Continuous_path, recursive = TRUE)
          print('Done!')
        }
        
        if(!dir.exists(glue("./{Continuous_path}"))){
          print('creating the directory')
          dir.create(glue("./{Continuous_path}"), recursive = TRUE)
        }
        jpeg(filename=glue("./{Continuous_path}/Glucose_VS_{feature_plot}.jpg"),
             units="cm", width=width_, height=height_, res=res_)
        
        myplot<-ggplot(lmData, aes(x=as.numeric(lmData[[feature_plot]]), y=Glucose)) +
          geom_jitter(size = size_, shape = shape_, alpha = alpha_) + # aes(color = lmData$ID)
          ggtitle(paste0("Cor: ",signif(corrs[1,i],2), ", q-val:",signif(fdr_pvals[1,i],2))) +
          geom_smooth(method=lm, se=FALSE) +
          labs(x = rownames(fdr_pvals)[i], y = rownames(fdr_pvals)[1], color = 'ID') +
          theme_bw() +
          theme(plot.title = element_text(hjust = 0.5), panel.background = element_blank(),
                axis.line = element_line(color="black"), axis.line.x = element_line(color="black")) +
          theme(legend.position = "right",
                legend.text = element_text(size = legend_size), legend.text.align = 1,
                legend.title = element_text(size = legend_size+1), legend.title.align = 1)
        print(myplot)
        dev.off()
      }
    }
  }
}



#########################################################################
 #######################################################################
cor_res <- rcorr(lmData$Glucose, as.matrix(lmData[,factor_variables]), type="spearman")
comparison <- 'Factors'
run_analysis(cor_res, comparison, lmData)
############## Ordinal variables ###################
cor_res <- rcorr(lmData$Glucose, as.matrix(lmData[,ordinal_variables]), type="spearman")
comparison <- 'Ordinal'
run_analysis(cor_res, comparison, lmData)
############## Continuous variables ###################
cor_res <- rcorr(lmData$Glucose, as.matrix(lmData[,continuous_variables[-1]]), type="spearman") # I don't need glucose twice
comparison <- 'continuous'
run_analysis(cor_res, comparison, lmData)

####################################################### ####################################################### 
################## ANOVA & Corrplots #####################
if(!dir.exists('./ANOVA_analysis')){
  dir.create('./ANOVA_analysis')
}else{
  print('Direcroty exists!')
}
jpeg('./ANOVA_analysis/Factors_corrplot.jpg', width = 16, height = 9, units = 'cm', res = 600)
corrplot(rcorr(as.matrix(lmData[,factor_variables[-1]]), type="spearman")$r, 
         method = 'circle', order = 'hclust', is.corr = TRUE, hclust.method = 'single',
         na.label = 'NA', 
         cl.cex = 0.5, cl.pos = 'b', cl.offset = 0.5, win.asp = 9/16,
         tl.col = 'black', tl.cex = 0.5, tl.srt = 77.5,
         addrect = 5, rect.col = 'darkred', rect.lwd = 1)
dev.off()

##################################################
####################################################### ####################################################### 
