input_file="../inputdata/training_set.tsv"
rows_in_train = c(1:100)

source("./aristo_data.R")
train_data <- aristo_data(input_file, rows_in_train)

summary(train_data)